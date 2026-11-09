/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 Leo Kuroshita (@kurogedelic), Hügelton Instruments */
/* SLOOP menu (HOME held), in sections as the pages are (2.4): SCREEN (COLOR, ZOOM, KNOB ACCEL (2.7)), LIGHTS (LIGHTS, KEYS, NOTES),
 * AUDIO (LOWCUT, USB AUDIO, USB SERIAL (FELUCCA_CDC builds only), USB RATE (2.7 beta), FILTER RESO (2.7.2)), SEQ (2.7.1: STEP ADVANCE, DRUM PREVIEW),
 * SYSTEM (2ND CORE (dualcore), HARDWARE CALIBRATION, LEARN CLEAR (2.6), ABOUT),
 * then one page per Dub function (2.9): DUB (DUB ENABLE, DUB PRESET, DUB MIX), SIREN (2.9.1, two pages:
 * SIR — SIREN TYPE, SIREN WAVE, SIREN PITCH, SIREN LEVEL — and SR2 — SIREN RATE, SIREN DEPTH, SIREN SYM,
 * SIREN SEND), SKANK (SKANK CHORD, SKANK ROOT, SKANK OCT, SKANK VEL; OCT+ plays the chord),
 * DSEQ (SEQ TRACK 2.9.2, SEQ LENGTH, SEQ STEP, SEQ NOTE, SEQ VELOCITY), RIDDIM (2.9.2:
 * RIDDIM, BASS PATTERN, SKANK PATTERN, DRUM PATTERN; OCT+ on each loads the selection into
 * the dub sequence: KNOB 1 the whole riddim, KNOB 2 the bass line, KNOB 3 the skanks,
 * KNOB 4 the drums) and PRESET (2.9.3: BASS PRESET, SKANK PRESET, MELODY PRESET, DRUM KIT;
 * OCT+ on each loads the selection into the riddim's track: KN1 the bass sound, KN2 the
 * skank's, KN3 the melody's, KN4 a reggae dub drum kit) and ISO (SUB, BASS, MIDS, TOPS;
 * OCT+ mutes the band).
 * SELECT goes to the page before / after (stopping at the ends), KNOB 1..4 set the page's settings in order (the knob's colour marks
 * its row), PRESETS moves the cursor; OCT+ steps the cursor's setting round or opens it (CALIBRATION, ABOUT, a skank chord),
 * OCT- closes (from ABOUT: back to the page). The tab strip shows five pages around the cursor: the screen
 * holds ten 3-letter tabs only with a window (a full row of ten would end at 298). */
/* ------------------------------------------------------------ menu --- */
/* (2.7: USB SERIAL only in a build with the serial console, FELUCCA_CDC=1: the FM-1's build has none) */
enum { MI_COLOR, MI_ZOOM, MI_ACCEL, MI_LIGHTS, MI_KEYS, MI_NOTES, MI_LOWCUT, MI_USB,
#if FELUCCA_CDC
       MI_SERIAL,
#endif
       MI_RATE, MI_FRESO, MI_ADV, MI_DPREV, MI_CPU1, MI_PANEL, MI_LCLEAR, MI_ABOUT,
       MI_DUB_ON, MI_DUB_PRESET, MI_DUB_MIX,
       MI_SIR_TYPE, MI_SIR_WAVE, MI_SIR_FRQ, MI_SIR_LVL,
       MI_SIR_RATE, MI_SIR_DPT, MI_SIR_SYM, MI_SIR_SEND,
       MI_SKANK_CHD, MI_SKANK_ROOT, MI_SKANK_OCT, MI_SKANK_VEL,
       MI_DUB_TRACK, MI_DUB_LEN, MI_DUB_STEP, MI_DUB_NOTE, MI_DUB_VEL,
       MI_RD_SEL, MI_RD_BASS, MI_RD_SKANK, MI_RD_DRUM,
       MI_PS_BASS, MI_PS_SKANK, MI_PS_MEL, MI_PS_KIT,
       MI_DUB_SUB, MI_DUB_BASS, MI_DUB_MIDS, MI_DUB_TOPS, MI_COUNT };
static const char *const MI_NAME[MI_COUNT] = {"COLOR", "ZOOM", "KNOB ACCEL", "LIGHTS", "KEYS", "NOTES", "SPEAKER LOWCUT", "USB AUDIO",
#if FELUCCA_CDC
                                              "USB SERIAL",
#endif
                                              "USB RATE", "FILTER RESO", "STEP ADVANCE", "DRUM PREVIEW", "2ND CORE", "HARDWARE CALIBRATION", "MIDI LEARN CLEAR", "ABOUT",
                                              "DUB ENABLE", "DUB PRESET", "DUB MIX",
                                              "SIREN TYPE", "SIREN WAVE", "SIREN PITCH", "SIREN LEVEL",
                                              "SIREN RATE", "SIREN DEPTH", "SIREN SYM", "SIREN SEND",
                                              "SKANK CHORD", "SKANK ROOT", "SKANK OCT", "SKANK VEL",
                                              "SEQ TRACK", "SEQ LENGTH", "SEQ STEP", "SEQ NOTE", "SEQ VELOCITY",
                                              "RIDDIM", "BASS PATTERN", "SKANK PATTERN", "DRUM PATTERN",
                                              "BASS PRESET", "SKANK PRESET", "MELODY PRESET", "DRUM KIT",
                                              "SUB", "BASS", "MIDS", "TOPS"};
enum { MS_SCREEN, MS_LIGHTS, MS_AUDIO, MS_SEQ, MS_SYSTEM, MS_DUB, MS_SIREN, MS_SIREN2, MS_SKANK, MS_DSEQ, MS_RIDDIM, MS_PRESET, MS_ISO, MS_COUNT };
static const char *const MS_NAME[MS_COUNT] = {"SCR", "LGT", "AUD", "SEQ", "SYS", "DUB", "SIR", "SR2", "SKK", "DSQ", "RDM", "PRS", "ISO"};

static uint8_t dub_menu_siren = 88;              /* the level OCT+ toggles the siren between */
static uint8_t dub_menu_chord;                   /* the skank's quality, DUB_SKANK_NAMES (dub_skank_conf) */
static uint8_t dub_menu_root;                    /* the skank's root pitch class, 0..11 (C..B) (dub_skank_conf) */
static uint8_t dub_menu_oct = 3;                 /* the skank's octave, 3..5 (dub_skank_conf) */
static uint8_t dub_menu_vel = 108;               /* the skank's velocity (dub_skank_conf) */
static uint8_t dub_menu_dtrk;                    /* the DSEQ page's track, DUB_TRK_* */
static uint8_t dub_menu_riddim;                  /* the RIDDIM page's four selections */
static uint8_t dub_menu_rbass;
static uint8_t dub_menu_rskank;
static uint8_t dub_menu_rdrum;
static uint8_t dub_menu_pbass;                   /* the PRESET page's four selections */
static uint8_t dub_menu_pskank;
static uint8_t dub_menu_pmel;
static uint8_t dub_menu_pkit;
static uint8_t dub_menu_preset;
static uint8_t dub_menu_len = 16;
static uint8_t dub_menu_step;
static uint8_t dub_menu_note = 36;
static uint8_t dub_menu_step_vel = 100;          /* the dub sequence's step velocity */
static uint8_t dub_menu_skank_notes[DUB_SKANK_MAX_NOTES];
static uint8_t dub_menu_skank_count;
static const char *const DUB_NOTE[12] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

UI_SMALL static void dub_menu_skank(void)        /* play the chord the SKANK page holds */
{
    dub_skank_t s;
    uint8_t notes[DUB_SKANK_MAX_NOTES], i;
    for (i = 0; i < dub_menu_skank_count; i++)
        input_off(&trk[0], dub_menu_skank_notes[i]);
    s = dub_skank_conf;
    s.root = dub_menu_root;
    dub_menu_skank_count = dub_skank_build(&s, 0, notes, DUB_SKANK_MAX_NOTES);
    for (i = 0; i < dub_menu_skank_count; i++) {
        dub_menu_skank_notes[i] = notes[i];
        input_on(&trk[0], notes[i], s.velocity);
    }
    dub_enabled = 1;
    dub_isolator.enabled = 1;
}

UI_SMALL static void dub_menu_riddim_load(uint32_t track)   /* OCT+ on the RIDDIM page: what KNOB 1..4 hold */
{
    uint32_t r = (uint32_t)dub_menu_riddim;
    if (track >= DUB_TRK_N) {
        dub_riddim_load(&dub_sequence, r);
        dub_menu_len = 64;
        ui_message("RIDDIM LOADED");
    } else {
        dub_riddim_load_track(&dub_sequence, track == DUB_TRK_BASS ? (uint32_t)dub_menu_rbass :
                                             track == DUB_TRK_SKANK ? (uint32_t)dub_menu_rskank :
                                                                      (uint32_t)dub_menu_rdrum, track);
        ui_message(track == DUB_TRK_BASS ? "BASS LOADED" : track == DUB_TRK_SKANK ? "SKANK LOADED" : "DRUM LOADED");
    }
    dub_enabled = 1;
    dub_isolator.enabled = 1;
}

UI_SMALL static void dub_menu_sound_load(uint32_t role)    /* OCT+ on the PRESET page: what KNOB 1..4 hold */
{
    const dub_sound_t *s;
    switch (role) {
    case 0:                                            /* the bass line's sound, track 1 */
        s = &DUB_BASS_SOUNDS[dub_menu_pbass % DUB_BASS_N];
        set_engine_of(&trk[0], s->engine);
        apply_preset_to(&trk[0], s->preset);
        ui_message("BASS LOADED");
        break;
    case 1:                                            /* the skank's sound, track 2 */
        s = &DUB_SKANK_SOUNDS[dub_menu_pskank % DUB_SKANK_N];
        set_engine_of(&trk[1], s->engine);
        apply_preset_to(&trk[1], s->preset);
        ui_message("SKANK LOADED");
        break;
    case 2:                                            /* the melody's sound, track 3 */
        s = &DUB_MEL_SOUNDS[dub_menu_pmel % DUB_MEL_N];
        set_engine_of(&trk[2], s->engine);
        apply_preset_to(&trk[2], s->preset);
        ui_message("MELODY LOADED");
        break;
    default:                                           /* the drum kit, the drum track's P_E0 */
        TDRUM->p[P_E0] = (int16_t)DUB_DK_KITS[dub_menu_pkit % DUB_DK_N];
        ui_message("KIT LOADED");
        break;
    }
    dub_enabled = 1;
    dub_isolator.enabled = 1;
}

UI_SMALL static void dub_menu_siren_play(void)   /* OCT+ sounds the siren at its level (88 when it was off) */
{
    if (!dub_menu_siren)
        dub_menu_siren = 88u;
    dub_siren_trigger(&dub_siren, dub_menu_siren);
    dub_enabled = 1;
    dub_isolator.enabled = 1;
}

UI_SMALL static void dub_menu_band(uint32_t band, int32_t delta, uint8_t toggle_mute)
{
    dub_band_param_t p;
    if (band >= DUB_BANDS)
        return;
    p = dub_isolator.p[band];
    if (toggle_mute)
        p.mute = (uint8_t)!p.mute;
    else {
        int32_t g = p.gain_db + delta;
        p.gain_db = (int8_t)(g < -24 ? -24 : g > 12 ? 12 : g);
    }
    dub_isolator_set_band(&dub_isolator, band, p);
    dub_enabled = 1;
    dub_isolator.enabled = 1;
}

UI_SMALL static void dub_menu_preset_apply(void)
{
    const dub_preset_t *p = &DUB_PRESETS[dub_menu_preset % DUB_PRESET_COUNT];
    uint32_t b;
    dub_enabled = 1;
    dub_isolator.enabled = 1;
    dub_menu_chord = (uint8_t)(p->chord & (DUB_SKANK_QUALITIES - 1u));
    dub_skank_conf.quality = dub_menu_chord;
    dub_skank_conf.root = dub_menu_root;
    dub_skank_conf.octave = dub_menu_oct;
    dub_skank_conf.velocity = dub_menu_vel;
    for (b = 0; b < DUB_BANDS; b++) {
        dub_band_param_t q = dub_isolator.p[b];
        q.gain_db = p->level / 2;
        q.mute = 0;
        dub_isolator_set_band(&dub_isolator, b, q);
    }
    dub_menu_siren = dub_menu_preset == 2u ? 88u : 0u;
    dub_siren_trigger(&dub_siren, dub_menu_siren);
    dub_siren_set_send(&dub_siren, (uint8_t)(p->delay < 0 ? 0 : p->delay > 127 ? 127 : p->delay));
}
static const uint8_t MS_FIRST[MS_COUNT + 1] = {MI_COLOR, MI_LIGHTS, MI_LOWCUT, MI_ADV, MI_CPU1,
                                               MI_DUB_ON, MI_SIR_TYPE, MI_SIR_RATE, MI_SKANK_CHD, MI_DUB_TRACK, MI_RD_SEL, MI_PS_BASS, MI_DUB_SUB, MI_COUNT};

UI_SMALL static int mi_cpu1_have(void)                      /* the second core is running (cpu1.c; the host tests have no cpu1.c) */
{
#if FELUCCA_CPU1
    return cpu1_state == CPU1_OK;
#else
    return 0;
#endif
}
static const char *const LIGHTS_NAME[LIGHTS_N] = {"OFF", "LOW", "MID", "HIGH"};   /* every button lit, the labels readable */
static const char *const KEYS_NAME[KEYS_N] = {"OFF", "C KEYS", "WHITE KEYS", "ALL KEYS"};      /* keys lit too, at the LIGHTS level */
#define MI_Y0 26                                   /* the first row, under the section tabs */
#define MI_DY 50                                   /* a row: the label, the value in large type */

UI_SMALL static uint32_t mi_sec(uint32_t i)                 /* the section of item i */
{
    uint32_t k = 0;
    while (k + 1u < MS_COUNT && i >= MS_FIRST[k + 1u])
        k++;
    return k;
}
UI_SMALL static uint32_t mi_row(uint32_t i) { return i - MS_FIRST[mi_sec(i)]; }   /* its row: KNOB 1 + row sets it */

/* item i's value as shown, and its colour */
UI_SMALL static const char *mi_value(uint32_t i, uint16_t *c)
{
    *c = C_HI;
    switch (i) {
    case MI_COLOR:                                    /* (2.7) your theme, by its name */
        if (theme_shown()) {
            static char b[9];
            uint32_t k;
            for (k = 0; k < 8u && theme.name[k]; k++)
                b[k] = theme.name[k];
            b[k] = 0;
            return k ? b : "MY THEME";
        }
        return PALETTES[settings.palette % NPALETTES].name;
    case MI_ZOOM: return settings.zoom ? "ON" : "OFF";
    case MI_ACCEL: return knob_accel_off ? "OFF" : "ON";   /* (2.7) the knobs speed up with a fast turn */
    case MI_ADV: return step_adv_off ? "OFF" : "ON";      /* (2.7.1) the STEP page's cursor moves on when the keys are let go */
    case MI_DPREV: return drum_preview ? "ON" : "OFF";     /* (2.7.1) a drum sound picked with a knob is heard */
    case MI_LIGHTS: return LIGHTS_NAME[lights_lvl % LIGHTS_N];
    case MI_KEYS:
        *c = lights_lvl ? C_HI : C_DIM;               /* (needs LIGHTS) */
        return KEYS_NAME[lights_keys % KEYS_N];
    case MI_NOTES: return lights_notes ? "ON" : "OFF";
    case MI_LOWCUT: return settings.lowcut ? "ON" : "OFF";
    case MI_USB: return usb_full ? "FULL" : "MASTER";
#if FELUCCA_CDC
    case MI_SERIAL: return usb_serial ? "ON" : "OFF";
#endif
    case MI_RATE: {                                   /* (2.7 beta) the rates the USB audio input offers (usb.c) */
        static const char *const R[3] = {"AUTO", "44.1 KHZ", "48 KHZ"};
        return R[usb_rate % 3u];
    }
    case MI_FRESO: {                                  /* (2.7.2) the track filter's resonance, 0 (clean) .. 10 (fx.c) */
        static char b[4];
        if (!flt_reso) {
            *c = C_DIM;
            return "OFF";
        }
        fmt_int(b, flt_reso > 10u ? 10 : flt_reso);
        return b;
    }
    case MI_CPU1:                                     /* the render on both cores (fx.c); live, the sound is the same */
        *c = mi_cpu1_have() ? C_HI : C_DIM;
        return cpu1_off ? "OFF" : "ON";
    case MI_LCLEAR: {                                 /* (2.6) the CCs MIDI LEARN holds; OCT+ clears them */
        static char b[8];
        uint32_t n = ml_count();
        if (!n) {
            *c = C_DIM;
            return "NONE";
        }
        fmt_int(b, (int32_t)n);
        str_cpy(b + str_len(b), " CC", 4);
        return b;
    }
    case MI_DUB_ON: return dub_enabled ? "ON" : "OFF";
    case MI_DUB_PRESET: return DUB_PRESETS[dub_menu_preset % DUB_PRESET_COUNT].name;
    case MI_DUB_MIX: {
        static char b[8];
        fmt_int(b, dub_isolator.mix);
        return b;
    }
    case MI_SIR_TYPE: return DUB_SIR_TYPE_NAMES[dub_siren.type];
    case MI_SIR_WAVE: return DUB_SIW_NAMES[dub_siren.wave];
    case MI_SIR_FRQ: {
        static char b[8];
        fmt_int(b, dub_siren.freq_hz);
        str_cpy(b + str_len(b), " HZ", 4);
        return b;
    }
    case MI_SIR_LVL: {
        static char b[8];
        if (!dub_siren.active) return "OFF";
        fmt_int(b, dub_siren.level);
        return b;
    }
    case MI_SIR_RATE: {
        static char b[8];
        fmt_int(b, (int32_t)dub_siren_rate_hz(dub_siren.rate));
        str_cpy(b + str_len(b), " HZ", 4);
        return b;
    }
    case MI_SIR_DPT: {
        static char b[8];
        fmt_int(b, dub_siren.depth);
        return b;
    }
    case MI_SIR_SYM: {
        static char b[8];
        fmt_int(b, dub_siren.sym);
        return b;
    }
    case MI_SIR_SEND: {
        static char b[8];
        if (!dub_siren.send) return "DRY";
        fmt_int(b, dub_siren.send);
        return b;
    }
    case MI_SKANK_CHD: return DUB_SKANK_NAMES[dub_menu_chord & (DUB_SKANK_QUALITIES - 1u)];
    case MI_SKANK_ROOT: return DUB_NOTE[dub_menu_root % 12u];
    case MI_SKANK_OCT: {
        static char b[8];
        fmt_int(b, dub_menu_oct);
        return b;
    }
    case MI_SKANK_VEL: {
        static char b[8];
        fmt_int(b, dub_menu_vel);
        return b;
    }
    case MI_DUB_TRACK: return DUB_TRK_NAMES[dub_menu_dtrk % DUB_TRK_N];
    case MI_DUB_LEN: {
        static char b[8];
        fmt_int(b, dub_sequence.length);
        return b;
    }
    case MI_DUB_STEP: {
        static char b[8];
        fmt_int(b, dub_menu_step + 1u);
        return b;
    }
    case MI_DUB_NOTE: {
        static char b[8];
        fmt_int(b, dub_menu_note);
        return b;
    }
    case MI_DUB_VEL: {
        static char b[8];
        fmt_int(b, dub_menu_step_vel);
        return b;
    }
    case MI_RD_SEL: return dub_riddim_name(dub_menu_riddim);
    case MI_RD_BASS: return dub_riddim_name(dub_menu_rbass);
    case MI_RD_SKANK: return dub_riddim_name(dub_menu_rskank);
    case MI_RD_DRUM: return dub_riddim_name(dub_menu_rdrum);
    case MI_PS_BASS: return DUB_BASS_SOUNDS[dub_menu_pbass % DUB_BASS_N].name;
    case MI_PS_SKANK: return DUB_SKANK_SOUNDS[dub_menu_pskank % DUB_SKANK_N].name;
    case MI_PS_MEL: return DUB_MEL_SOUNDS[dub_menu_pmel % DUB_MEL_N].name;
    case MI_PS_KIT: return DUB_DK_NAMES[dub_menu_pkit % DUB_DK_N];
    case MI_DUB_SUB:
    case MI_DUB_BASS:
    case MI_DUB_MIDS:
    case MI_DUB_TOPS: {
        static char b[12];
        uint32_t band = i - MI_DUB_SUB;
        if (dub_isolator.p[band].mute) return "MUTE";
        fmt_int(b, dub_isolator.p[band].gain_db);
        return b;
    }
    default:
        *c = C_DIM;
        return "";                                    /* (an action: OCT+ opens it) */
    }
}

UI_SMALL static void draw_menu(void)
{
    uint32_t i, pass, sec = mi_sec(ui.menu_sel % MI_COUNT);
    uint32_t sig = ui.menu * 7u + ui.menu_sel * 131u + settings.palette * 1009u + settings.lowcut * 7919u +
                   settings.zoom * 104729u + lights_lvl * 1299709u + lights_keys * 15485863u + ml_count() * 2654435u +
                   lights_notes * 32452843u + usb_full * 49979687u + usb_serial * 86028121u + usb_rate * 15486719u + theme_shown() * 32452867u + theme.crc + cpu1_off * 122949829u +
                   knob_accel_off * 179424673u + drum_preview * 236887691u + step_adv_off * 373587883u + flt_reso * 512927357u +
                   dub_enabled * 6700417u + dub_siren.active * 6700453u + dub_siren.level * 6700459u +
                   dub_siren.freq_hz * 6700477u + dub_siren.depth * 6700479u + dub_siren.rate * 6700481u +
                   dub_siren.type * 6700519u + dub_siren.wave * 6700523u + dub_siren.sym * 6700531u + dub_siren.send * 6700533u +
                   dub_menu_chord * 6700463u + dub_menu_preset * 6700467u + dub_menu_len * 6700471u +
                   dub_menu_step * 6700483u + dub_menu_note * 6700487u + dub_menu_step_vel * 6700491u +
                   dub_menu_root * 6700499u + dub_menu_oct * 6700503u + dub_menu_vel * 6700509u +
                   dub_menu_dtrk * 6700539u + dub_menu_riddim * 6700541u + dub_menu_rbass * 6700547u +
                   dub_menu_rskank * 6700551u + dub_menu_rdrum * 6700557u + dub_sequence.length * 6700563u +
                   dub_menu_pbass * 6700569u + dub_menu_pskank * 6700571u + dub_menu_pmel * 6700577u +
                   dub_menu_pkit * 6700581u +
                   dub_isolator.mix * 6700513u +
                   dub_isolator.p[DUB_SUB].gain_db * 6700493u + dub_isolator.p[DUB_BASS].gain_db * 6700497u +
                   dub_isolator.p[DUB_MIDS].gain_db * 6700501u + dub_isolator.p[DUB_TOPS].gain_db * 6700507u +
                   dub_isolator.p[DUB_SUB].mute * 6700511u + dub_isolator.p[DUB_BASS].mute * 6700517u +
                   dub_isolator.p[DUB_MIDS].mute * 6700521u + dub_isolator.p[DUB_TOPS].mute * 6700527u +
                   (ui.msg_t ? 6700599u : 0u) + (uint8_t)ui.msg[0] * 6700607u;
    if (!ui.force && sig == ui.menu_sig)
        return;
    ui.menu_sig = sig;
    if (ui.force)                                   /* head + rule + two bands cover rows 0..229 */
        lcd_fill(0, H_HEAD + 1 + 124 + 95, 240, 240 - (H_HEAD + 1 + 124 + 95), C_BLACK);
    cv_begin(240, H_HEAD, C_BLACK);
    if (ui.msg_t && ui.msg[0])                       /* the load's word, seen from the menu too */
        cv_text(4, 1, &FONT_S, ui.msg, C_AMB);
    else
        cv_text(4, 1, &FONT_S, ui.menu == 2 ? "ABOUT" : "MENU", C_HI);
    if (ui.menu != 2) {                             /* the page and its number, as a page's "ENV DEST 2/2" */
        char t[16];
        str_cpy(t, MS_NAME[sec], sizeof t);
        str_cpy(t + str_len(t), " ", 2);
        fmt_int(t + str_len(t), (int32_t)sec + 1);
        str_cpy(t + str_len(t), "/", 2);
        fmt_int(t + str_len(t), MS_COUNT);
        cv_text(236 - text_w(&FONT_S, t), 1, &FONT_S, t, C_GRAY);
    }
    cv_blit(0, Y_HEAD);
    lcd_fill(0, H_HEAD, 240, 1, C_LINE);
    for (pass = 0; pass < 2u; pass++) {             /* the canvas holds 124 rows: draw in two bands */
        cv_begin(240, pass ? 95u : 124u, C_BLACK);
        cv_oy = pass ? -124 : 0;
        if (ui.menu == 2) {
            cv_text(4, 4, &FONT_L, "SLOOP", C_WHITE);
            cv_rect(96, 10, 8, 4, TE_COL[0]), cv_rect(96, 16, 12, 4, TE_COL[1]);   /* the sail */
            cv_rect(96, 22, 16, 4, TE_COL[2]), cv_rect(96, 28, 20, 4, TE_COL[3]);
            cv_text(4, 36, &FONT_S, "BASED ON FELUCCA", C_AMB);
            cv_text(4, 54, &FONT_S, FELUCCA_VERSION, C_HI);
            cv_text(236 - text_w(&FONT_S, __DATE__), 54, &FONT_S, __DATE__, C_GRAY);   /* build date */
            cv_text(cv_text(4, 72, &FONT_S, "LEO KUROSHITA", C_HI) + 8, 72, &FONT_S, "@KUROGEDELIC", C_AMB);
            cv_text(4, 88, &FONT_S, "H\xDCGELTON INSTRUMENTS", C_HI);   /* Latin-1 U-umlaut */
            cv_text(4, 104, &FONT_S, "HUGELTON.COM", C_AMB);
#if FELUCCA_CPU1
            {
                char sv[12];
                cpu1_supplies(sv);                  /* (2.7) SYSVDD, VDC14 now: 1.38V 1.60V (fm1_sys.h) */
                cv_text(236 - text_w(&FONT_S, sv), 104, &FONT_S, sv, C_GRAY);
            }
#endif
            cv_text(4, 119, &FONT_S, "GPL-3.0, NO WARRANTY", C_HI);
#if FELUCCA_CPU1                                    /* (the host tests include this file without cpu1.c) */
            cv_text(236 - text_w(&FONT_S, cpu1_label()), 119, &FONT_S, cpu1_label(), C_AMB);   /* 2 CORES / 1 CORE (cpu1.c) */
#endif
            cv_text(4, 132, &FONT_S, "GITHUB.COM/ISOD89/SLOOP-FM1", C_AMB);   /* (the source of this firmware) */
            cv_text(4, 146, &FONT_S, "FONT: TERMINUS (OFL)", C_DIM);
            cv_text(4, 159, &FONT_S, "SAMPLES: VERSILIAN (CC0)", C_DIM);
            cv_text(4, 172, &FONT_S, "+ SONIC PI (CC0)", C_DIM);
            cv_text(4, 185, &FONT_S, "PHASE: CRISPYZEBRA (GPL)", C_DIM);
            cv_text(4, 198, &FONT_S, "VOICE: REF. KLATTSCH (MIT)", C_DIM);
        } else {
            int32_t x = 4;
            uint32_t t0 = sec >= 2u ? sec - 2u : 0u, t1;   /* the tab strip: five pages around this one */
            uint32_t last = MS_COUNT - 1u;
            if (t0 > last)
                t0 = last;
            t1 = t0 + 4u;
            if (t1 > last) {
                t1 = last;
                t0 = t1 > 4u ? t1 - 4u : 0u;
            }
            if (t0)
                x = cv_text(x, 4, &FONT_S, "<", C_DIM) + 2;
            for (i = t0; i <= t1; i++) {            /* the pages as tabs: this one lit */
                int32_t w = text_w(&FONT_S, MS_NAME[i]);
                if (i == sec)
                    cv_rect(x - 2, 3, w + 4, 18, C_LINE);
                cv_text(x, 4, &FONT_S, MS_NAME[i], i == sec ? C_WHITE : C_DIM);
                x += w + 6;                         /* (a window of five: 4 + 150 + arrows fits 240) */
            }
            if (t1 < last)
                cv_text(x, 4, &FONT_S, ">", C_DIM);
            for (i = MS_FIRST[sec]; i < MS_FIRST[sec + 1u]; i++) {
                uint32_t r = i - MS_FIRST[sec];
                int32_t y = MI_Y0 + (int32_t)r * MI_DY, xv;
                int cur = i == ui.menu_sel;
                uint16_t vc;
                const char *v = mi_value(i, &vc);
                char k[4] = {'K', (char)('1' + r), 0, 0};
                cv_rect(4, y + 2, 4, MI_DY - 8, cur ? C_WHITE : TE_COL[r & 3u]);   /* the knob's colour */
                xv = cv_text(14, y, &FONT_S, k, TE_COL[r & 3u]);
                cv_text(xv + 6, y, &FONT_S, MI_NAME[i], cur ? C_WHITE : C_GRAY);
                if (v[0] && text_w(&FONT_L, v) <= 222) {
                    xv = cv_text(14, y + 16, &FONT_L, v, cur && vc == C_HI ? C_WHITE : vc);
                } else if (v[0]) {                      /* (too wide for the large type: WHITE KEYS) */
                    xv = cv_text(14, y + 24, &FONT_S, v, cur && vc == C_HI ? C_WHITE : vc);
                } else {
                    xv = cv_text(14, y + 24, &FONT_S, "OCT+ OPENS", cur ? C_WHITE : C_DIM);
                }
                if (i == MI_COLOR) {                    /* the palette's colours */
                    uint32_t q;
                    for (q = 0; q < 5u; q++)
                        cv_rect(xv + 10 + (int32_t)q * 14, y + 28, 10, 10, pal[q]);
                }
                if (i == MI_RATE && usb_rate != usb_rate_now())
                    cv_text(xv + 8, y + 30, &FONT_S, "RESTART", C_AMB);   /* (usb.c: at the next start) */
#if FELUCCA_CDC
                if (i == MI_SERIAL && usb_serial != usb_cdc_now())
                    cv_text(xv + 8, y + 30, &FONT_S, "RESTART", C_AMB);   /* (usb.c: at the next start) */
#endif
                if (i == MI_CPU1 && !mi_cpu1_have())
                    cv_text(xv + 8, y + 30, &FONT_S, "NOT RUNNING", C_AMB);   /* (cpu1.c: ABOUT says 1 CORE) */
            }
            if (MS_FIRST[sec + 1u] - MS_FIRST[sec] <= 3u) {   /* (a page of three rows leaves the help's place) */
                cv_text(4, MI_Y0 + 3 * MI_DY + 6, &FONT_S, "SELECT PAGE  KNOB SETS", C_DIM);
                cv_text(4, MI_Y0 + 3 * MI_DY + 22, &FONT_S, "OCT+ OK   OCT- CLOSE", C_DIM);   /* (rows .. 218) */
            }
        }
        cv_oy = 0;
        cv_blit(0, H_HEAD + 1 + pass * 124u);
    }
}

UI_SMALL static void enc_drop(void)                             /* knob turns nobody takes */
{
    uint32_t k;
    for (k = 0; k < NE; k++)
        panel_enc(k);
}

UI_SMALL static void menu_close(void)
{
    if (song.playing || transport_req)
        settings_later = 1;                            /* (a flash write stops the audio: once stopped) */
    else
        settings_save();                               /* palette / panel table, if changed */
    ui.menu = 0;
    ui.force = 1;
    go_home();
}

/* item i: a knob turned s (> 0 right, < 0 left), or 0: OCT+ (steps round, toggles, or opens) */
UI_SMALL static void mi_set(uint32_t i, int32_t s)
{
    switch (i) {
    case MI_COLOR: {                                   /* both ways round; OCT+ the next. 2.7: your theme after MONO
                                                        * (the palette number stays the last built-in one: an older
                                                        * SLOOP shows that) */
        uint32_t n = NPALETTES + (theme_valid ? 1u : 0u), at = theme_shown() ? NPALETTES : settings.palette % NPALETTES;
        at = (at + (s < 0 ? n - 1u : 1u)) % n;
        theme_on = (uint8_t)(at == NPALETTES);
        if (!theme_on)
            settings.palette = at;
        palette_set(settings.palette);
        ui.force = 1;
        break;
    }
    case MI_ACCEL:                                     /* (2.7) right ON, left OFF; OCT+ toggles (ui_input.c accel) */
        knob_accel_off = (uint8_t)(s > 0 ? 0u : s < 0 ? 1u : !knob_accel_off);
        break;
    case MI_ADV:                                       /* (2.7.1) right ON, left OFF; OCT+ toggles (ui_input.c seq_entry) */
        step_adv_off = (uint8_t)(s > 0 ? 0u : s < 0 ? 1u : !step_adv_off);
        break;
    case MI_DPREV:                                     /* (2.7.1) right ON, left OFF; OCT+ toggles (ui_studio.c drum_hear) */
        drum_preview = (uint8_t)(s > 0 ? 1u : s < 0 ? 0u : !drum_preview);
        break;
    case MI_ZOOM:
    case MI_LOWCUT: {                                  /* right ON, left OFF; OCT+ toggles */
        uint32_t *v = i == MI_LOWCUT ? &settings.lowcut : &settings.zoom;
        *v = s > 0 ? 1u : s < 0 ? 0u : !*v;
        fx_lowcut = (uint8_t)(settings.lowcut != 0);
        break;
    }
    case MI_USB:                                       /* right FULL, left MASTER */
        usb_full = (uint8_t)(s > 0 ? 1u : s < 0 ? 0u : !usb_full);
        break;
#if FELUCCA_CDC
    case MI_SERIAL:
        usb_serial = (uint8_t)(s > 0 ? 1u : s < 0 ? 0u : !usb_serial);
        break;
#endif
    case MI_RATE:                                      /* (2.7 beta) AUTO 44.1 48: the knob steps (stops at the ends),
                                                        * OCT+ round; at the next start (usb.c usb_rate_mode) */
        if (s > 0 && usb_rate < 2u)
            usb_rate++;
        else if (s < 0 && usb_rate > 0u)
            usb_rate--;
        else if (!s)
            usb_rate = (uint8_t)((usb_rate + 1u) % 3u);
        break;
    case MI_FRESO:                                     /* (2.7.2) 0 (OFF/clean) .. 10, stops at the ends; OCT+ steps round */
        if (s > 0 && flt_reso < 10u)
            flt_reso++;
        else if (s < 0 && flt_reso > 0u)
            flt_reso--;
        else if (!s)
            flt_reso = (uint8_t)((flt_reso >= 10u ? 0u : flt_reso + 1u));
        break;
    case MI_CPU1:                                      /* right ON, left OFF; at once (the next block renders so) */
        cpu1_off = (uint8_t)(s > 0 ? 0u : s < 0 ? 1u : !cpu1_off);
        cpu1_units = cpu1_off ? 0 : -1;
        if (!cpu1_off && !cpu1_on())                   /* 2.7: core 1 starts only at power-on */
            ui_message("ON AT NEXT POWER-ON");
        break;
    case MI_NOTES:
        lights_notes = (uint8_t)(s > 0 ? 1u : s < 0 ? 0u : !lights_notes);
        break;
    case MI_LIGHTS:
    case MI_KEYS: {                                    /* brighter / dimmer (stops at the ends); OCT+ steps round */
        uint8_t *v = i == MI_LIGHTS ? &lights_lvl : &lights_keys;
        uint32_t n = i == MI_LIGHTS ? LIGHTS_N : KEYS_N;
        if (s > 0 && *v + 1u < n)
            (*v)++;
        else if (s < 0 && *v > 0u)
            (*v)--;
        else if (!s)
            *v = (uint8_t)((*v + 1u) % n);
        if (i == MI_KEYS && lights_keys && !lights_lvl)
            lights_lvl = LIGHTS_LOW;                   /* keys lit need a level: the lowest */
        break;
    }
    case MI_LCLEAR:                                    /* (2.6) every learned CC: OCT+ */
         if (!s)
             ui_message(ml_clear_all() ? "LEARN CLEARED" : "NOTHING LEARNED");
         break;
    case MI_DUB_ON:
        dub_enabled = (uint8_t)(s > 0 ? 1u : s < 0 ? 0u : !dub_enabled);
        dub_isolator.enabled = dub_enabled;
        if (!dub_enabled)
            dub_siren_trigger(&dub_siren, 0);
        break;
    case MI_DUB_PRESET:
        if (s > 0)
            dub_menu_preset = (uint8_t)((dub_menu_preset + 1u) % DUB_PRESET_COUNT);
        else if (s < 0)
            dub_menu_preset = (uint8_t)((dub_menu_preset + DUB_PRESET_COUNT - 1u) % DUB_PRESET_COUNT);
        else
            dub_menu_preset_apply();
        break;
    case MI_DUB_MIX:                                   /* the isolator's wet blend, 0 (dry) .. 127; OCT+ kills it */
        if (s > 0 && dub_isolator.mix < 127u)
            dub_isolator.mix++;
        else if (s < 0 && dub_isolator.mix > 0u)
            dub_isolator.mix--;
        else if (!s)
            dub_isolator.mix = dub_isolator.mix ? 0u : 127u;
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SIR_TYPE:                                  /* WAIL HILO RAMP SWEEP SPACE; OCT+ plays the siren */
        if (s > 0)
            dub_siren_set_type(&dub_siren, (uint8_t)((dub_siren.type + 1u) % DUB_SIR_TYPES));
        else if (s < 0)
            dub_siren_set_type(&dub_siren, (uint8_t)((dub_siren.type + DUB_SIR_TYPES - 1u) % DUB_SIR_TYPES));
        else
            dub_menu_siren_play();
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SIR_WAVE:                                  /* SQR PLS SAW TRI SIN; OCT+ plays the siren */
        if (s > 0)
            dub_siren_set_wave(&dub_siren, (uint8_t)((dub_siren.wave + 1u) % DUB_SIW_N));
        else if (s < 0)
            dub_siren_set_wave(&dub_siren, (uint8_t)((dub_siren.wave + DUB_SIW_N - 1u) % DUB_SIW_N));
        else
            dub_menu_siren_play();
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SIR_FRQ:                                   /* 220..1200 Hz, two Hz a detent; OCT+ back to 740 */
        if (s > 0)
            dub_siren_set_freq(&dub_siren, (uint16_t)(dub_siren.freq_hz + 2u));
        else if (s < 0)
            dub_siren_set_freq(&dub_siren, (uint16_t)(dub_siren.freq_hz - 2u));
        else
            dub_siren_set_freq(&dub_siren, 740u);
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SIR_LVL:                                   /* right up, left down (stops at the ends); OCT+ on / off */
        if (s > 0 && dub_menu_siren < 127u)
            dub_menu_siren++;
        else if (s < 0 && dub_menu_siren > 0u)
            dub_menu_siren--;
        else if (!s)
            dub_menu_siren = dub_menu_siren ? 0u : 88u;
        dub_siren_trigger(&dub_siren, dub_menu_siren);
        dub_enabled = dub_menu_siren ? 1u : dub_enabled;
        dub_isolator.enabled = dub_enabled;
        break;
    case MI_SIR_RATE:                                  /* the LFO's speed, 1..16 Hz; OCT+ back to 2 Hz */
        if (s > 0 && dub_siren.rate < 127u)
            dub_siren.rate++;
        else if (s < 0 && dub_siren.rate > 0u)
            dub_siren.rate--;
        else if (!s)
            dub_siren.rate = 8u;
        dub_siren_set_rate(&dub_siren, dub_siren.rate);
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SIR_DPT:                                   /* the pitch sweep, 0..127 = two octaves; OCT+ back to 96 */
        if (s > 0 && dub_siren.depth < 127u)
            dub_siren.depth++;
        else if (s < 0 && dub_siren.depth > 0u)
            dub_siren.depth--;
        else if (!s)
            dub_siren.depth = 96u;
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SIR_SYM:                                   /* the LFO's symmetry, 0..127; OCT+ back to 64 */
        if (s > 0 && dub_siren.sym < 127u)
            dub_siren.sym++;
        else if (s < 0 && dub_siren.sym > 0u)
            dub_siren.sym--;
        else if (!s)
            dub_siren.sym = 64u;
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SIR_SEND:                                  /* the delay send, 0..127; OCT+ 48 (a dubby echo) */
        if (s > 0 && dub_siren.send < 127u)
            dub_siren.send++;
        else if (s < 0 && dub_siren.send > 0u)
            dub_siren.send--;
        else if (!s)
            dub_siren_set_send(&dub_siren, dub_siren.send ? 0u : 48u);
        dub_enabled = 1;
        dub_isolator.enabled = 1;
        break;
    case MI_SKANK_CHD:                                 /* MAJ MIN DIM AUG 7TH MIN7 9TH PWR; OCT+ plays the chord */
        if (s > 0)
            dub_menu_chord = (uint8_t)((dub_menu_chord + 1u) & (DUB_SKANK_QUALITIES - 1u));
        else if (s < 0)
            dub_menu_chord = (uint8_t)((dub_menu_chord + DUB_SKANK_QUALITIES - 1u) & (DUB_SKANK_QUALITIES - 1u));
        else
            dub_menu_skank();
        dub_skank_conf.quality = dub_menu_chord;
        break;
    case MI_SKANK_ROOT:                                /* C..B, round; OCT+ plays the chord */
        if (s > 0)
            dub_menu_root = (uint8_t)((dub_menu_root + 1u) % 12u);
        else if (s < 0)
            dub_menu_root = (uint8_t)((dub_menu_root + 11u) % 12u);
        else
            dub_menu_skank();
        dub_skank_conf.root = dub_menu_root;
        break;
    case MI_SKANK_OCT:                                 /* octaves 3..5, stops at the ends; OCT+ plays the chord */
        if (s > 0 && dub_menu_oct < 5u)
            dub_menu_oct++;
        else if (s < 0 && dub_menu_oct > 3u)
            dub_menu_oct--;
        else if (!s)
            dub_menu_skank();
        dub_skank_conf.octave = dub_menu_oct;
        break;
    case MI_SKANK_VEL:                                 /* 0..127; OCT+ plays the chord */
        if (s > 0 && dub_menu_vel < 127u)
            dub_menu_vel++;
        else if (s < 0 && dub_menu_vel > 0u)
            dub_menu_vel--;
        else if (!s)
            dub_menu_skank();
        dub_skank_conf.velocity = dub_menu_vel;
        break;
    case MI_DUB_TRACK:                                 /* BASS SKNK MEL DRUM: the track DSEQ edits, round */
        if (s > 0 || !s)
            dub_menu_dtrk = (uint8_t)((dub_menu_dtrk + 1u) % DUB_TRK_N);
        else
            dub_menu_dtrk = (uint8_t)((dub_menu_dtrk + DUB_TRK_N - 1u) % DUB_TRK_N);
        break;
    case MI_DUB_LEN:
        if (s > 0 || !s)
            dub_menu_len = dub_menu_len == 16u ? 32u : dub_menu_len == 32u ? 64u : 16u;
        else if (dub_menu_len == 16u)
            dub_menu_len = 64u;
        else if (dub_menu_len == 32u)
            dub_menu_len = 16u;
        else
            dub_menu_len = 32u;
        dub_seq_set_length(&dub_sequence, dub_menu_len);
        break;
    case MI_DUB_STEP:
        if (s > 0 || !s)
            dub_menu_step = (uint8_t)((dub_menu_step + 1u) % dub_sequence.length);
        else
            dub_menu_step = (uint8_t)((dub_menu_step + dub_sequence.length - 1u) % dub_sequence.length);
        break;
    case MI_DUB_NOTE:
        dub_menu_note = (uint8_t)(s > 0 ? dub_menu_note + 1u : s < 0 ? dub_menu_note - 1u : dub_menu_note);
        if (!s)
            dub_menu_note = (uint8_t)(dub_menu_note + 12u > 127u ? 36u : dub_menu_note + 12u);
        dub_seq_set_step(&dub_sequence, dub_menu_dtrk, dub_menu_step, dub_menu_note, dub_menu_step_vel);
        break;
    case MI_DUB_VEL:
        if (s > 0 && dub_menu_step_vel < 127u) dub_menu_step_vel++;
        else if (s < 0 && dub_menu_step_vel > 0u) dub_menu_step_vel--;
        else if (!s) dub_menu_step_vel = dub_menu_step_vel ? 0u : 100u;
        dub_seq_set_step(&dub_sequence, dub_menu_dtrk, dub_menu_step, dub_menu_note, dub_menu_step_vel);
        break;
    case MI_RD_SEL:                                    /* the ten riddims, round; OCT+ loads the whole */
        if (s > 0)
            dub_menu_riddim = (uint8_t)((dub_menu_riddim + 1u) % DUB_RIDDIM_COUNT);
        else if (s < 0)
            dub_menu_riddim = (uint8_t)((dub_menu_riddim + DUB_RIDDIM_COUNT - 1u) % DUB_RIDDIM_COUNT);
        else
            dub_menu_riddim_load(DUB_TRK_N);           /* (a track past the drum: the whole riddim) */
        break;
    case MI_RD_BASS:                                   /* the bass motifs, round; OCT+ loads the track */
        if (s > 0)
            dub_menu_rbass = (uint8_t)((dub_menu_rbass + 1u) % DUB_RIDDIM_COUNT);
        else if (s < 0)
            dub_menu_rbass = (uint8_t)((dub_menu_rbass + DUB_RIDDIM_COUNT - 1u) % DUB_RIDDIM_COUNT);
        else
            dub_menu_riddim_load(DUB_TRK_BASS);
        break;
    case MI_RD_SKANK:                                  /* the skank motifs, round; OCT+ loads the track */
        if (s > 0)
            dub_menu_rskank = (uint8_t)((dub_menu_rskank + 1u) % DUB_RIDDIM_COUNT);
        else if (s < 0)
            dub_menu_rskank = (uint8_t)((dub_menu_rskank + DUB_RIDDIM_COUNT - 1u) % DUB_RIDDIM_COUNT);
        else
            dub_menu_riddim_load(DUB_TRK_SKANK);
        break;
    case MI_RD_DRUM:                                   /* the drum motifs, round; OCT+ loads the track */
        if (s > 0)
            dub_menu_rdrum = (uint8_t)((dub_menu_rdrum + 1u) % DUB_RIDDIM_COUNT);
        else if (s < 0)
            dub_menu_rdrum = (uint8_t)((dub_menu_rdrum + DUB_RIDDIM_COUNT - 1u) % DUB_RIDDIM_COUNT);
        else
            dub_menu_riddim_load(DUB_TRK_DRUM);
        break;
    case MI_PS_BASS:                                   /* the bass sounds, round; OCT+ loads into track 1 */
        if (s > 0)
            dub_menu_pbass = (uint8_t)((dub_menu_pbass + 1u) % DUB_BASS_N);
        else if (s < 0)
            dub_menu_pbass = (uint8_t)((dub_menu_pbass + DUB_BASS_N - 1u) % DUB_BASS_N);
        else
            dub_menu_sound_load(0);
        break;
    case MI_PS_SKANK:                                  /* the skank's sounds, round; OCT+ into track 2 */
        if (s > 0)
            dub_menu_pskank = (uint8_t)((dub_menu_pskank + 1u) % DUB_SKANK_N);
        else if (s < 0)
            dub_menu_pskank = (uint8_t)((dub_menu_pskank + DUB_SKANK_N - 1u) % DUB_SKANK_N);
        else
            dub_menu_sound_load(1);
        break;
    case MI_PS_MEL:                                    /* the melody's sounds, round; OCT+ into track 3 */
        if (s > 0)
            dub_menu_pmel = (uint8_t)((dub_menu_pmel + 1u) % DUB_MEL_N);
        else if (s < 0)
            dub_menu_pmel = (uint8_t)((dub_menu_pmel + DUB_MEL_N - 1u) % DUB_MEL_N);
        else
            dub_menu_sound_load(2);
        break;
    case MI_PS_KIT:                                    /* the reggae dub kits, round; OCT+ swaps the kit */
        if (s > 0)
            dub_menu_pkit = (uint8_t)((dub_menu_pkit + 1u) % DUB_DK_N);
        else if (s < 0)
            dub_menu_pkit = (uint8_t)((dub_menu_pkit + DUB_DK_N - 1u) % DUB_DK_N);
        else
            dub_menu_sound_load(3);
        break;
    case MI_DUB_SUB:
    case MI_DUB_BASS:
    case MI_DUB_MIDS:
    case MI_DUB_TOPS:
        dub_menu_band(i - MI_DUB_SUB, s, !s);
        break;
    case MI_PANEL:                                     /* actions: OCT+ only */
        if (!s) {
            panel_setup();
            ui.force = 1;
        }
        break;
    case MI_ABOUT:
        if (!s) {
            ui.menu = 2;
            ui.force = 1;
        }
        break;
    default:
        break;
    }
}

/* menu: SELECT the page, KNOB 1..3 its settings, PRESETS the cursor, OCT+ ok, OCT- close (ABOUT -> the page) */
UI_SMALL static void menu_input(uint32_t pressed)
{
    int32_t s;
    uint32_t k, ok = (pressed >> panel.btn[B_OCTUP]) & 1u;
    uint32_t back = (pressed >> panel.btn[B_OCTDN]) & 1u;
    uint32_t sel = ui.menu_sel % MI_COUNT, sec = mi_sec(sel), n = MS_FIRST[sec + 1u] - MS_FIRST[sec];
    /* OCT- is the menu's universal escape.  Read the physical debounced
     * button as well as the edge mask: this keeps the escape reliable when
     * a host/emulator sends a held button across two scan frames. */
    if ((fm1_in.buttons >> panel.btn[B_OCTDN]) & 1u)
        back = 1u;
    if (back) {
        if (ui.menu == 2)
            ui.menu = 1, ui.force = 1;
        else
            menu_close();
        return;
    }
    if (ui.menu != 1) {
        enc_drop();
        return;
    }
    if ((s = panel_enc(EN_SELECT)) != 0) {             /* the page before / after (stops at the ends) */
        int32_t to = clamp((int32_t)sec + (s > 0 ? 1 : -1), 0, MS_COUNT - 1);
        if ((uint32_t)to != sec) {
            ui.menu_sel = MS_FIRST[to];
            ui.force = 1;
        }
        enc_drop();
        return;
    }
    if ((s = panel_enc(EN_PRESET)) != 0)               /* the cursor, round the page's rows */
        ui.menu_sel = (uint8_t)(MS_FIRST[sec] + (sel - MS_FIRST[sec] + (s > 0 ? 1u : n - 1u)) % n);
    for (k = 0; k < 4u; k++)
        if ((s = panel_enc(EN_K1 + k)) != 0 && k < n) {
            ui.menu_sel = (uint8_t)(MS_FIRST[sec] + k);   /* (the cursor follows the knob turned) */
            mi_set(MS_FIRST[sec] + k, s);
        }
    if (ok)
        mi_set(ui.menu_sel % MI_COUNT, 0);
    enc_drop();                                        /* swallow the rest while the menu is up */
}
