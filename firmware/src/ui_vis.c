/* SPDX-License-Identifier: GPL-3.0-only */
/* SLOOP 2.9.15: the full-screen visualiser, WIRES only. On HOME (the TRACKS screen), HOME tapped opens
 * it; HOME again or any page closes it. 2.4's twelve styles are cut down to the one this build keeps:
 * the eleven other draw routines, the 512-point FFT, the spectrogram's heat and the Lissajous trail are
 * gone (flash and about 7 KB of RAM back). The keys, PLAY and REC work as always.
 * It reads what the audio already leaves for the UI: the tracks' peaks (fx.c / drums.c, as the TRACKS
 * meters read them) and the notes that started (voice.c vis_hit). Everything is drawn in the main loop,
 * every other frame, in two bands of 120 rows (the canvas holds 124): no cost to the audio. */
#define VIS_N 1u
static const char *const VIS_NAME[VIS_N] = {"WIRES"};
/* vis_on, vis_shown_last, vis_name_t: ui_draw.c; vis_style: panel.c (its slot in the settings' word
 * stays; the visualiser itself no longer reads it) */
static struct {
    int16_t wamp[4];                                /* each string's swing (0..1000) */
    uint8_t wn[4];                                  /* its wave count (from the note) */
    uint32_t wph;                                   /* the wires' phase */
} vs;

static int vis_shown(void) { return vis_on && !ui.home && !ui.menu && cur_page()->scope == SC_TRK; }
static void vis_open(void)
{
    vis_on = 1;
    vis_name_t = 30;
    ui.force = 1;
}
static int32_t isin(uint32_t a) { return SINE[a & 1023u]; }          /* a: 1024 a turn; Q15 */
/* |x| (Q15) -> 0..1000 over 48 dB (8 log2: 6 dB a step of 8) */
static int32_t vis_lvl(int32_t a)
{
    int32_t lg = 0, v;
    if (a < 0)
        a = -a;
    if (a < 16)
        return 0;
    while ((a >> lg) > 1)
        lg++;
    v = lg * 8 + (((a << 3) >> lg) & 7);           /* 120 = 0 dB */
    return clamp((v - 56) * 1000 / 64, 0, 1000);
}

/* ---- drawing helpers (canvas coordinates; cv_oy picks the band) ---- */
static void vis_ellipse(int32_t cx, int32_t cy, int32_t rx, int32_t ry, uint16_t c)
{
    int32_t y;
    if (rx < 1 || ry < 1)
        return;
    for (y = -ry; y <= ry; y++) {
        int32_t w = 0;
        while (w <= rx && (w * w) * (ry * ry) + (y * y) * (rx * rx) <= (rx * rx) * (ry * ry))
            w++;
        if (w)
            cv_rect(cx - w + 1, cy + y, 2 * w - 1, 1, c);
    }
}
static void vis_thick(int32_t x0, int32_t y0, int32_t x1, int32_t y1, uint16_t c)   /* 2 px */
{
    cv_line(x0, y0, x1, y1, c);
    cv_line(x0, y0 + 1, x1, y1 + 1, c);
}

/* ---- the frame's data ---- */
static void vis_update(void)
{
    uint32_t i, hit;
    int32_t pk[4];
    fm1_irq_off();                                  /* the tracks' peaks since the last look (as the TRACKS
                                                     * meters take them) and the notes that started */
    for (i = 0; i < NPART; i++) {
        pk[i] = trk[i].peak;
        trk[i].peak = 0;
    }
    pk[3] = drums.peak;
    drums.peak = 0;
    hit = vis_hit;
    vis_hit = 0;
    fm1_irq_on();
    for (i = 0; i < 4u; i++) {
        int32_t v = trk_level(i) && !trk[i].p[P_MUTE] ? vis_lvl(pk[i]) : 0;
        if ((hit >> i) & 1u) {
            vs.wn[i] = (uint8_t)(2u + vis_note[i] % 12u / 2u);
            if (vs.wamp[i] < 1000)
                vs.wamp[i] = 1000;
        }
        vs.wamp[i] = (int16_t)(vs.wamp[i] > v ? vs.wamp[i] - (vs.wamp[i] - v) / 6 - 4 : v);
        if (vs.wamp[i] < 0)
            vs.wamp[i] = 0;
    }
    vs.wph += 37u;
}

/* ---- the style (draws the whole screen; called once per band) ---- */
static void vis_wires(void)
{
    uint32_t i, x;
    for (i = 0; i < 4u; i++) {
        int32_t y0 = 40 + (int32_t)i * 52, amp = vs.wamp[i] * 22 / 1000, py = y0;
        char lab[2] = {(char)('1' + i), 0};
        for (x = 0; x < 240u; x += 2u) {           /* a standing wave: the string's shape x its swing */
            uint32_t a = x * 512u / 240u, cyc = i == 3u ? 8u : vs.wn[i] ? vs.wn[i] : 2u;   /* sin(pi x / L) */
            int32_t env = isin(a), wv = isin(x * cyc * 1024u / 240u + vs.wph * (3u + i));
            int32_t y = y0 - (((env * wv) >> 15) * amp >> 15);
            if (x)
                vis_thick((int32_t)x - 2, py, (int32_t)x, y, TE_COL[i]);
            py = y;
        }
        vis_ellipse(4, y0, 4, 4, C_WHITE);
        vis_ellipse(236, y0, 4, 4, C_WHITE);
        cv_text(10, y0 - 22, &FONT_S, lab, TE_COL[i]);
    }
}

/* the visualiser, every other frame: the update, then both bands */
static void vis_draw(void)
{
    uint32_t pass;
    if (!vis_shown_last || ui.force) {
        vis_shown_last = 1;
        lcd_fill(0, 0, 240, 240, C_BLACK);
    } else if (ui.frame & 1u) {
        return;
    }
    vis_update();
    for (pass = 0; pass < 2u; pass++) {
        cv_begin(240, 120, C_BLACK);
        cv_oy = -(int32_t)(pass * 120u);
        vis_wires();
        if (!pass && (vis_name_t || ui.msg_t)) {    /* the style's name a second (or a message) */
            const char *s = ui.msg_t ? ui.msg : VIS_NAME[0];
            cv_rect(0, 0, 240, 20, C_BLACK);
            cv_text(120 - text_w(&FONT_S, s) / 2, 2, &FONT_S, s, C_WHITE);
        }
        cv_oy = 0;
        cv_blit(0, pass * 120u);
    }
    if (vis_name_t)
        vis_name_t--;
}
