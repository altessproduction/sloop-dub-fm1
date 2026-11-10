/* SPDX-License-Identifier: GPL-3.0-only
 *
 * SLOOP web emulator: the real SLOOP/FELUCCA firmware sources compiled to
 * wasm32, with a browser HAL in place of the FM-1 hardware (as tests/hostsim.c
 * does for the DSP alone, but with the whole UI: screen, layers, LEDs).
 *
 * The firmware is one compilation unit (firmware/src/felucca.c); this file
 * plays that role for the web: the HAL below replaces the fm1_*.h headers,
 * then the same sources are included in the same order. No firmware source is
 * modified.
 *
 *   audio   emu_render(n): mix_block into a float buffer (an AudioWorklet)
 *   screen  an ST7789 panel model behind lcd.c: 240x240 RGB565 framebuffer
 *   input   emu_input(notes, buttons) / emu_enc(e, steps) from JS events
 *   boot    emu_init (splash) then emu_start, emu_frame() ~60/s (ui loop)
 */
#include <stdint.h>

#define WASM_EXPORT(n) __attribute__((export_name(n), used))

/* ------------------------------------------------------------- time HAL --- */
#define FM1_TICKS_PER_US 24u
static uint64_t emu_samples;                   /* total frames rendered */
static uint32_t fm1_ticks(void) { return (uint32_t)(emu_samples * 544u); } /* ~24 MHz */
static void fm1_delay_ms(uint32_t ms) { (void)ms; }   /* never busy-wait in a worklet */
static void fm1_wdt_feed(void) {}

/* -------------------------------------------------------------- irq HAL --- */
static uint32_t irq_save(void) { return 0; }
static void irq_restore(uint32_t f) { (void)f; }
static void fm1_irq_off(void) {}
static void fm1_irq_on(void) {}

/* ------------------------------------------------------------ input HAL --- */
/* as hal/fm1_input.h, without the matrix scan: JS writes the debounced state */
#define FM1_NCOL 11u
#define FM1_NKEY 41u              /* ids: 0..13 buttons, 14..40 note keys */
#define FM1_NENC 7u
enum { FM1_BTN_OCT_DOWN = 0, FM1_BTN_OCT_UP = 1 };

static const int8_t FM1_KEYMAP[6][FM1_NCOL] = {
    {-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
    { 5, 11,  4, 10,  3,  9,  2,  8, -1, -1, -1},
    {34, 35, 36, 37, 38, 40, 39, 13,  7,  6, 12},
    {23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33},
    { 0,  1, 15, 14, 17, 16, 19, 18, 20, 21, 22},
    {-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1},
};

static volatile struct {
    uint32_t notes;              /* bit n = note key n (0 = F3 .. 26 = G5) */
    uint32_t buttons;            /* bit i = matrix button i (0..13) */
    uint32_t pressed, released;  /* button edges since the last fm1_input_edges() */
    uint32_t notes_pressed;      /* note-key press edges */
    uint8_t raw[FM1_NCOL];
    uint8_t cnt[FM1_NKEY];
    uint8_t enc_prev[FM1_NENC], enc_last[FM1_NENC];
    uint8_t enc_rest[FM1_NENC];
    uint16_t enc_still[FM1_NENC];
    int8_t enc_sub[FM1_NENC];
    int16_t enc_steps[FM1_NENC];
    uint32_t frames;
} fm1_in;
/* Held MIDI-remote buttons are part of the real FM-1 input HAL. */
static volatile uint32_t fm1_remote_btn;

static uint8_t fm1_led[FM1_NCOL];
static uint8_t fm1_led_dim[FM1_NCOL];
static uint8_t fm1_led_bg[FM1_NCOL];
static volatile uint16_t fm1_led_bg_ns;

static void fm1_input_init(void) {}

static int32_t fm1_enc_take(uint32_t e)
{
    int32_t s = fm1_in.enc_steps[e];
    fm1_in.enc_steps[e] = 0;
    return s;
}

static uint32_t fm1_input_edges(uint32_t *released)
{
    uint32_t p = fm1_in.pressed;
    if (released)
        *released = fm1_in.released;
    fm1_in.pressed = fm1_in.released = 0;
    return p;
}

static uint32_t fm1_input_note_edges(void)
{
    uint32_t p = fm1_in.notes_pressed;
    fm1_in.notes_pressed = 0;
    return p;
}

static void fm1_led_key(uint32_t id, int on)
{
    uint32_t p, r;
    for (p = 0; p < FM1_NCOL; p++)
        for (r = 1; r < 5u; r++)
            if (FM1_KEYMAP[r][p] == (int8_t)id) {
                if (on)
                    fm1_led[p] |= (uint8_t)(1u << r);
                else
                    fm1_led[p] &= (uint8_t)~(1u << r);
            }
}

/* -------------------------------------------------------------- adc HAL --- */
enum { FM1_ADC_BATT = 3, FM1_ADC_MASTER = 4 };
static volatile int32_t emu_adc_v[8] = {0, 0, 0, 800, 1023, 0, 0, 0};
static int32_t fm1_adc_read(uint32_t ch) { return emu_adc_v[ch & 7u]; }
static void fm1_adc_init(void) {}

/* -------------------------------------------------- lcd HAL (ST7789 model) */
/* lcd.c speaks the real panel protocol; this consumes it into a framebuffer.
 * Only CASET (2A), RASET (2B) and RAMWR (2C) matter; init commands are
 * ignored. Pixels arrive RGB565 big-endian (gfx.c pre-swaps). */
static uint16_t emu_fb[240 * 240];
static volatile uint32_t emu_fb_gen;           /* bumped on every pixel write */
static uint32_t fm1_lcd_timeouts;
static uint8_t st_cmd;
static uint32_t st_argn;
static uint8_t st_arg[4];
static uint16_t st_x0, st_x1 = 239, st_y0, st_y1 = 239, st_cx, st_cy;

static void fm1_lcd_hw_init(void) {}
static void fm1_lcd_baud(uint32_t b) { (void)b; }
static void fm1_lcd_wait(void) {}
static void fm1_lcd_deselect(void) {}

static void fm1_lcd_send_cmd(uint8_t c)
{
    st_cmd = c;
    st_argn = 0;
    if (c == 0x2Cu) {                           /* RAMWR resets the cursor */
        st_cx = st_x0;
        st_cy = st_y0;
    }
}

static void fm1_lcd_send_data(const void *p, uint32_t n)
{
    const uint8_t *b = p;
    if (st_cmd == 0x2Au || st_cmd == 0x2Bu) {
        while (n-- && st_argn < 4u)
            st_arg[st_argn++] = *b++;
        if (st_argn == 4u) {
            uint16_t a = (uint16_t)(st_arg[0] << 8 | st_arg[1]);
            uint16_t e = (uint16_t)(st_arg[2] << 8 | st_arg[3]);
            if (st_cmd == 0x2Au) {
                st_x0 = a;
                st_x1 = e;
            } else {
                st_y0 = a;
                st_y1 = e;
            }
        }
        return;
    }
    if (st_cmd != 0x2Cu && st_cmd != 0x3Cu)
        return;
    for (; n >= 2u; n -= 2u, b += 2u) {
        if (st_cx < 240u && st_cy < 240u)
            emu_fb[st_cy * 240u + st_cx] = (uint16_t)(b[0] << 8 | b[1]);
        if (++st_cx > st_x1) {
            st_cx = st_x0;
            if (++st_cy > st_y1)
                st_cy = st_y0;
        }
    }
    emu_fb_gen++;
}

/* ------------------------------------------------------------ audio HAL --- */
/* audio.c's ISR glue compiles against these but is never driven; the worklet
 * pulls mix_block through emu_render instead. */
#define FM1_AUDIO_HALF 0x80u
static void fm1_audio_init(int32_t *b, uint32_t n, void (*i)(void), uint32_t p)
{
    (void)b; (void)n; (void)i; (void)p;
}
static uint8_t fm1_audio_pending(void) { return 0; }
static void fm1_audio_ack_aux(uint8_t p) { (void)p; }
static uint32_t fm1_audio_free_half(void) { return 0; }
static void fm1_audio_ack_half(void) {}
static void fm1_audio_stop(void) {}
void isr_alnk0(void) {}

/* ----------------------------------------------------------- system HAL --- */
static void fm1_reboot(void) {}
static void fm1_enter_uboot(void) {}

/* ------------------------------------------------------ firmware sources --- */
#include "felucca_tables.h"
#include "libc.c"
#include "lcd.c"
#include "gfx.c"
#include "core.h"
/* The FM-1 has a second DSP core; WebAssembly runs the exact same render
 * synchronously on one core. Keep the firmware's CPU1 call sites intact while
 * making the browser HAL deterministic and avoiding pthreads/shared memory. */
#define FELUCCA_CPU1 0
#include "cpu1.h"
static int cpu1_run(cpu1_job_t fn, uint32_t arg) { (void)fn; (void)arg; return 0; }
static int cpu1_wait(void) { return 0; }
static int cpu1_on(void) { return 0; }
static uint32_t cpu1_ticks(void) { return 0; }
/* Dub extension is part of the same firmware unity root. Its DSP is invoked
 * by fx.c after the normal SLOOP mix, never by a separate JavaScript synth. */
#include "dub.h"
#include "dub.c"

/* the flash image (declared before engines.c: eng_sample.c reads the user
 * sample slots through SMP_USER_XIP, which on hardware is the memory-mapped
 * XIP window — here it points into the same RAM image the storage uses) */
#define EMU_FLASH_BASE 0x90000u
#define EMU_FLASH_SIZE 0x70000u
static uint8_t emu_flash[EMU_FLASH_SIZE];
static volatile uint32_t emu_flash_gen;
#define SMP_USER_XIP(k) (emu_flash + (SMP_USER_BASE - EMU_FLASH_BASE) + (k) * SMP_USER_SIZE)

#include "engines.c"
#include "drums.c"
#include "params.c"
#include "voice.c"
#include "slicer.c"
#include "fx.c"
#define FELUCCA_OTA 0
#define FELUCCA_CDC 0
#define FELUCCA_UAC 0
#include "usb.c"
#define FELUCCA_ARRANGER 1
#include "arranger.c"
#include "seq.c"
#include "audio.c"
#include "panel.c"
#include "ui.c"
#include "ui_song.c"
#include "ui_studio.c"
#include "icons.c"
#include "ui_draw.c"
#include "ui_vis.c"
#include "ui_layers.c"
#include "ui_menu.c"
#include "ui_input.c"
/* ---- flash: a RAM image of the FM-1's persisted areas ----
 * storage.c's A/B sector scheme runs unchanged on this array; JS loads a
 * saved image into it before boot and writes it back to IndexedDB whenever
 * emu_flash_gen moves, so projects, autosave, settings and user presets
 * survive a reload. Offsets are the real flash map (0x97000..0xFEFFF). */
#define FELUCCA_FLASH 1
#include "fm1_flash_id.h"
static uint8_t flash_ok;
#define FL_FAR(f) f
#define ST_XIP_PTR(off) (emu_flash + ((uint32_t)(off) - EMU_FLASH_BASE))
static uint32_t fl_jedec_ram(void) { return 0x856014u; }   /* the expected part: flash_ok */
static void fl_plain_window_init(void) {}
static int emu_fl_ok(uint32_t off, uint32_t n)
{
    return off >= EMU_FLASH_BASE && n <= EMU_FLASH_SIZE && off - EMU_FLASH_BASE <= EMU_FLASH_SIZE - n;
}
static int st_read(uint32_t off, void *dst, uint32_t n)
{
    if (!emu_fl_ok(off, n))
        return -8;
    memcpy(dst, emu_flash + (off - EMU_FLASH_BASE), n);
    return 0;
}
static int st_erase(uint32_t off)
{
    if (!emu_fl_ok(off, 4096u))
        return -8;
    memset(emu_flash + (off - EMU_FLASH_BASE), 0xFF, 4096u);
    emu_flash_gen++;
    return 0;
}
static int st_prog(uint32_t off, const void *src, uint32_t n)
{
    if (!emu_fl_ok(off, n))
        return -8;
    memcpy(emu_flash + (off - EMU_FLASH_BASE), src, n);
    emu_flash_gen++;
    return 0;
}
#include "storage.c"
#include "upreset.c"
#include "project.c"
#include "splash.c"

/* ------------------------------------------------------------- web entry --- */
static float emu_audio_f[2u * 512u];
static int32_t emu_mix[2u * CTL];
static uint32_t emu_ms_acc;

/* power-on defaults, as main.c felucca_init() */
static void emu_felucca_init(void)
{
    uint32_t i;
    for (i = 0; i < G_COUNT; i++)
        song.g[i] = GP[i].def;
    for (i = 0; i < NTRK; i++) {
        track_t *t = &trk[i];
        track_defaults(t);
        if (i < NPART) {
            set_engine_of(t, TRK_DEF[i][0]);
            apply_preset_to(t, TRK_DEF[i][1]);
            t->engine = t->eng_req;
        }
        track_defaults_steps(t);
    }
    TDRUM->p[P_E0] = DRUM_DEFAULT_KIT;
    song.sel = 0;
    song.master_q12 = 2048;
    dub_isolator_init(&dub_isolator);            /* the Dub extension: bypassed until a page turns it on,
                                                  * with the mix at full wet as main.c felucca_init does */
    dub_siren_init(&dub_siren);
    dub_seq_init(&dub_sequence);
    autosave_resume();
    song.g[G_SYNC] = (int16_t)lights_sync;
    layers_init();
    go_home();
    ui.force = 1;
}

WASM_EXPORT("emu_init") void emu_init(void)
{
    persist_boot();
    settings_init();
    lcd_init();
    sloop_splash();
    fm1_input_init();
    fm1_adc_init();
    panel_init();
    emu_felucca_init();
}

WASM_EXPORT("emu_start") void emu_start(void)   /* after the splash has shown */
{
    lcd_fill(0, 0, 240, 240, C_BLACK);
    ui.force = 1;
}

WASM_EXPORT("emu_frame") void emu_frame(void)   /* the main loop's UI pass */
{
    {   /* master volume as the pot in fm1_main */
        uint32_t k10 = (uint32_t)fm1_adc_read(FM1_ADC_MASTER);
        song.master_q12 = (k10 * k10) >> 8;
    }
    {   /* battery: a steady healthy reading */
        int32_t b = fm1_adc_read(FM1_ADC_BATT);
        song.batt_raw = song.batt_raw ? song.batt_raw + (b - song.batt_raw) / 32 : b;
    }
    ui_input();
    ui_leds();
    ui_draw();
    autosave_tick();
    sections_flush();
}

WASM_EXPORT("emu_render") void emu_render(uint32_t n)
{
    uint32_t k, i;
    if (n > 512u)
        n = 512u;
    for (k = 0; k + CTL <= n; k += CTL) {
        mix_block(emu_mix, CTL);
        for (i = 0; i < CTL; i++) {
            int32_t l = emu_mix[2u * i], r = emu_mix[2u * i + 1u];
            if (i & 1u)
                scope_buf[scope_w++ & (SCOPE_N - 1u)] = (int16_t)(l > 32767 ? 32767 : l < -32768 ? -32768 : l);
            emu_audio_f[2u * (k + i)] = (float)l * (1.0f / 32768.0f);
            emu_audio_f[2u * (k + i) + 1u] = (float)r * (1.0f / 32768.0f);
        }
    }
    emu_samples += n;
    emu_ms_acc += n * 1000u;
    while (emu_ms_acc >= FS) {
        emu_ms_acc -= FS;
        fm1_ms++;
    }
}

WASM_EXPORT("emu_input") void emu_input(uint32_t notes, uint32_t buttons)
{
    uint32_t pn = fm1_in.notes, pb = fm1_in.buttons;
    fm1_in.notes = notes & 0x7FFFFFFu;
    fm1_in.buttons = buttons & 0x3FFFu;
    fm1_in.notes_pressed |= notes & ~pn;
    fm1_in.pressed |= buttons & ~pb;
    fm1_in.released |= pb & ~buttons;
}

WASM_EXPORT("emu_enc") void emu_enc(uint32_t e, int32_t steps)
{
    if (e < FM1_NENC)
        fm1_in.enc_steps[e] = (int16_t)(fm1_in.enc_steps[e] + steps);
}

WASM_EXPORT("emu_dbg") uint32_t emu_dbg(uint32_t idx)
{   /* the console's state probe for the tests: 0 playing, 1 tick, 2 bpm, 3 dly div,
     * 4 dly fdbk, 5 dly mix, 6 sir level, 7 sir active, 8 sir send, 9 dub send,
     * 10 dly ms, 11 dly sync, 12 dub module on, 13..16 the tracks' sends (2.9.12:
     * 13 bass, 14 skank, 15 melody, 16 drums), 17 the menu open (2.9.16: the web
     * page reads the firmware's own state instead of mirroring it), 18 the menu's
     * row cursor, 19 the siren's level setting (the SR2 row's), 20 the OCT+ hold
     * armed (the momentary's state), 21 a 24-bit hash of the tracks' first steps,
     * 22 the menu page the cursor stands on (0..13, ui_menu.c MS_*) */
    switch (idx) {
    case 0: return song.playing;
    case 1: return song.tick;
    case 2: return (uint32_t)song.g[G_BPM];
    case 3: return (uint32_t)song.g[G_DTIME];
    case 4: return (uint32_t)song.g[G_DFDBK];
    case 5: return (uint32_t)song.g[G_DMIX];
    case 6: return dub_siren.level;
    case 7: return dub_siren.active;
    case 8: return dub_siren.send;
    case 9: return dub_send;
    case 10: return dub_dly_ms;
    case 11: return dub_dly_sync;
    case 13: return (uint32_t)trk[0].p[P_DLY];
    case 14: return (uint32_t)trk[1].p[P_DLY];
    case 15: return (uint32_t)trk[2].p[P_DLY];
    case 16: return (uint32_t)song.g[G_DRDLY];
    case 17: return ui.menu;
    case 18: return ui.menu_sel;
    case 19: return dub_menu_siren;
    case 20: return dub_menu_siren_held;
    case 21: {
        uint32_t t, i, h = 0;
        for (t = 0; t < 4u; t++)
            for (i = 0; i < 16u; i++)
                h = h * 131u + (trk[t].step[i].n ? trk[t].step[i].note[0] : 255u);
        return h & 0xFFFFFFu;
    }
    case 22: return mi_sec(ui.menu_sel % MI_COUNT);
    default: return (uint32_t)dub_enabled;
    }
}

WASM_EXPORT("emu_adc_set") void emu_adc_set(uint32_t ch, int32_t v)
{
    emu_adc_v[ch & 7u] = v;
}

WASM_EXPORT("emu_midi") void emu_midi(uint32_t pkt)   /* a USB-MIDI event packet */
{
    midi_in_q[mi_w++ % MQ] = pkt;
}

WASM_EXPORT("emu_fb_ptr") uint32_t emu_fb_ptr(void) { return (uint32_t)(uintptr_t)emu_fb; }
WASM_EXPORT("emu_fb_gen") uint32_t emu_fb_gen_get(void) { return emu_fb_gen; }
WASM_EXPORT("emu_audio_ptr") uint32_t emu_audio_ptr(void) { return (uint32_t)(uintptr_t)emu_audio_f; }
WASM_EXPORT("emu_led_ptr") uint32_t emu_led_ptr(void) { return (uint32_t)(uintptr_t)fm1_led; }
WASM_EXPORT("emu_led_dim_ptr") uint32_t emu_led_dim_ptr(void) { return (uint32_t)(uintptr_t)fm1_led_dim; }
WASM_EXPORT("emu_flash_ptr") uint32_t emu_flash_ptr(void) { return (uint32_t)(uintptr_t)emu_flash; }
WASM_EXPORT("emu_flash_size") uint32_t emu_flash_size(void) { return EMU_FLASH_SIZE; }
WASM_EXPORT("emu_flash_gen") uint32_t emu_flash_gen_get(void) { return emu_flash_gen; }

/* ----------------------------------------------------------- Dub controls ---
 * These entry points are deliberately small firmware commands.  The page only
 * sends parameters; all sound generation and filtering remains in dub.c/fx.c.
 * (2.9.10) none of them engages the module: emu_dub_enable alone does — the
 * K1 rule, the same one switch the menu's DUB page turns. */
WASM_EXPORT("emu_dub_enable") void emu_dub_enable(uint32_t on)
{
    dub_enabled = on ? 1 : 0;
    dub_isolator.enabled = dub_enabled;
}

WASM_EXPORT("emu_dub_siren") void emu_dub_siren(uint32_t level, uint32_t frequency, uint32_t depth)
{
    dub_siren_set_freq(&dub_siren, (uint16_t)(frequency < 220u ? 220u : frequency > 1200u ? 1200u : frequency));
    dub_siren.depth = (uint8_t)(depth > 127u ? 127u : depth);
    dub_siren_trigger(&dub_siren, (uint8_t)(level > 127u ? 127u : level));
}

WASM_EXPORT("emu_dub_siren_rate") void emu_dub_siren_rate(uint32_t rate)   /* 0..127 = 1..16 Hz; older wasm builds have none */
{
    dub_siren_set_rate(&dub_siren, (uint8_t)(rate > 127u ? 127u : rate));
}

WASM_EXPORT("emu_dub_siren_type") void emu_dub_siren_type(uint32_t type)   /* the LFO's curve, DUB_SIR_* */
{
    dub_siren_set_type(&dub_siren, (uint8_t)type);
}

WASM_EXPORT("emu_dub_siren_wave") void emu_dub_siren_wave(uint32_t wave)   /* the oscillator's curve, DUB_SIW_* */
{
    dub_siren_set_wave(&dub_siren, (uint8_t)wave);
}

WASM_EXPORT("emu_dub_siren_sym") void emu_dub_siren_sym(uint32_t sym)      /* the LFO's symmetry / duty / glide */
{
    dub_siren_set_sym(&dub_siren, (uint8_t)(sym > 127u ? 127u : sym));
}

WASM_EXPORT("emu_dub_siren_send") void emu_dub_siren_send(uint32_t send)   /* the delay send, 0 dry .. 127 full */
{
    dub_siren_set_send(&dub_siren, (uint8_t)(send > 127u ? 127u : send));
}

WASM_EXPORT("emu_dub_siren_level") void emu_dub_siren_level(uint32_t level)   /* the siren's level, 0 off */
{
    dub_siren_trigger(&dub_siren, (uint8_t)(level > 127u ? 127u : level));
}

WASM_EXPORT("emu_dub_siren_freq") void emu_dub_siren_freq(uint32_t frequency)   /* the base pitch, 220..1200 Hz */
{
    dub_siren_set_freq(&dub_siren, (uint16_t)(frequency < 220u ? 220u : frequency > 1200u ? 1200u : frequency));
}

WASM_EXPORT("emu_dub_siren_depth") void emu_dub_siren_depth(uint32_t depth)   /* the pitch sweep, 0..2 octaves */
{
    dub_siren.depth = (uint8_t)(depth > 127u ? 127u : depth);
}

WASM_EXPORT("emu_dub_mix") void emu_dub_mix(uint32_t mix)                  /* the isolator's wet blend, 0 dry .. 127 wet */
{
    dub_isolator.mix = (uint8_t)(mix > 127u ? 127u : mix);
}

WASM_EXPORT("emu_dub_band") void emu_dub_band(uint32_t band, int32_t gain, uint32_t mute)
{
    dub_band_param_t p;
    if (band >= DUB_BANDS)
        return;
    p = dub_isolator.p[band];
    p.gain_db = (int8_t)(gain < -24 ? -24 : gain > 12 ? 12 : gain);
    p.mute = mute ? 1 : 0;
    dub_isolator_set_band(&dub_isolator, band, p);
}

/* 2.9.7: the DUB page's filter and throw, the DLY page's tape delay — the same state the
 * menu rows hold, so the console and the hardware stay one machine */
WASM_EXPORT("emu_dub_filter") void emu_dub_filter(uint32_t v)
{
    dub_filter_set((int16_t)(v > 127u ? 127u : v));
}

WASM_EXPORT("emu_dub_filter_get") uint32_t emu_dub_filter_get(void)
{
    return (uint32_t)dub_filter_get();
}

WASM_EXPORT("emu_dub_send") void emu_dub_send(uint32_t v)
{
    dub_send_set((uint8_t)(v > 127u ? 127u : v));
}

WASM_EXPORT("emu_dub_send_get") uint32_t emu_dub_send_get(void)
{
    return dub_send;
}

WASM_EXPORT("emu_track_send") void emu_track_send(uint32_t track, uint32_t v)
{   /* (2.9.12) the SEND page: a sequencer track's throw into the delay — 0 the bass,
     * 1 the skank, 2 the melody (their P_DLY), 3 the drums (the GLO > DRUMS DLY) */
    if (track < 3u)
        trk[track].p[P_DLY] = (int16_t)(v > 127u ? 127u : v);
    else if (track == 3u)
        song.g[G_DRDLY] = (int16_t)(v > 127u ? 127u : v);
}

WASM_EXPORT("emu_track_send_get") uint32_t emu_track_send_get(uint32_t track)
{
    if (track < 3u)
        return (uint32_t)trk[track].p[P_DLY];
    if (track == 3u)
        return (uint32_t)song.g[G_DRDLY];
    return 0;
}

WASM_EXPORT("emu_dub_dly_time") void emu_dub_dly_time(uint32_t ms)
{
    dub_dly_set_ms((uint16_t)(ms > 1400u ? 1400u : ms));
}

WASM_EXPORT("emu_dub_dly_time_get") uint32_t emu_dub_dly_time_get(void)
{
    return dub_dly_ms;
}

WASM_EXPORT("emu_dub_dly_rel") void emu_dub_dly_rel(uint32_t v)
{
    song.g[G_DFDBK] = (int16_t)(v > 120u ? 120u : v);
}

WASM_EXPORT("emu_dub_dly_rel_get") uint32_t emu_dub_dly_rel_get(void)
{
    return (uint32_t)song.g[G_DFDBK];
}

WASM_EXPORT("emu_dub_dly_mix") void emu_dub_dly_mix(uint32_t v)   /* (2.9.11) the echo's wet level, the project's MIX */
{
    song.g[G_DMIX] = (int16_t)(v > 127u ? 127u : v);
}

WASM_EXPORT("emu_dub_dly_mix_get") uint32_t emu_dub_dly_mix_get(void)
{
    return (uint32_t)song.g[G_DMIX];
}

WASM_EXPORT("emu_dub_dly_sync") void emu_dub_dly_sync(uint32_t on)
{
    dub_dly_set_sync((uint8_t)(on ? 1u : 0u));
}

WASM_EXPORT("emu_dub_dly_sync_get") uint32_t emu_dub_dly_sync_get(void)
{
    return dub_dly_sync;
}

WASM_EXPORT("emu_dub_dly_div") void emu_dub_dly_div(uint32_t d)
{
    song.g[G_DTIME] = (int16_t)(d > 8u ? 8u : d);
}

WASM_EXPORT("emu_dub_dly_div_get") uint32_t emu_dub_dly_div_get(void)
{
    return (uint32_t)song.g[G_DTIME];
}

WASM_EXPORT("emu_dub_seq_length") void emu_dub_seq_length(uint32_t length)   /* 2.9.6: every track's LEN */
{
    uint32_t i;
    if (length < 1u)
        length = 1u;
    if (length > NSTEP)
        length = NSTEP;
    for (i = 0; i < DUB_TRK_N; i++)
        trk[i].p[P_SLEN] = (int16_t)length;
}

WASM_EXPORT("emu_dub_seq_step") void emu_dub_seq_step(uint32_t track, uint32_t step, uint32_t note, uint32_t velocity)
{
    if (track >= DUB_TRK_N || step >= NSTEP)
        return;
    if (track == DUB_TRK_DRUM) {                   /* the web DSQ's cell: a lane hit / cleared */
        if (!velocity || note > 127u)
            dstep_clr(&trk[track].dstep[step], lane_of_note(note));
        else
            dstep_set(&trk[track].dstep[step], lane_of_note(note), vel_lvl(velocity), 0);
        return;
    }
    if (!velocity || note > 127u) {                /* the web DSQ's clear: the step empties */
        trk[track].step[step].n = 0;
        trk[track].step[step].time = ST_REST;
        return;
    }
    trk[track].step[step].note[0] = (uint8_t)note;
    trk[track].step[step].n = 1;
    trk[track].step[step].time = ST_NOTE;
    trk[track].step[step].flags = 0;
    trk[track].step[step].vel = (uint8_t)velocity;
    trk[track].seq_active = 1;
}

WASM_EXPORT("emu_dub_riddim_count") uint32_t emu_dub_riddim_count(void)
{
    return DUB_RIDDIM_COUNT;
}

/* 2.9.6: the sequencer's readback, the web console's DSQ view: what a load left in the
 * SLOOP sequencer's tracks — the steps themselves, each track's LEN, the playhead.
 * 255 (DUB_SEQ_REST) an empty step, 254 a TIE (the load's held note going on). */
WASM_EXPORT("emu_dub_seq_len") uint32_t emu_dub_seq_len(void)     /* the longest track's LEN */
{
    uint32_t i, n = 0;
    for (i = 0; i < DUB_TRK_N; i++)
        if (trk[i].p[P_SLEN] > (int16_t)n)
            n = (uint32_t)trk[i].p[P_SLEN];
    return n;
}

WASM_EXPORT("emu_dub_seq_track_len") uint32_t emu_dub_seq_track_len(uint32_t track)
{
    return track < DUB_TRK_N ? (uint32_t)trk[track].p[P_SLEN] : 0u;
}

WASM_EXPORT("emu_dub_seq_note") uint32_t emu_dub_seq_note(uint32_t track, uint32_t step)
{
    const step_t *sp;
    if (track >= DUB_TRK_N || step >= NSTEP)
        return DUB_SEQ_REST;
    if (track == DUB_TRK_DRUM) {
        const dstep_t *d = &trk[track].dstep[step];
        uint32_t m = dstep_mask(d), l = 0;
        if (!m)
            return DUB_SEQ_REST;
        while (!(m >> l & 1u))
            l++;                                   /* the step's first lane, its note out */
        return LANE_NOTE[l & 15u];
    }
    sp = &trk[track].step[step];
    if (sp->time == ST_TIE)
        return 254u;                               /* the hold the load wrote, going on */
    if (sp->time == ST_NOTE && sp->n)
        return sp->note[0];
    return DUB_SEQ_REST;
}

WASM_EXPORT("emu_dub_seq_pos") uint32_t emu_dub_seq_pos(void)      /* the playhead's sixteenth */
{
    uint32_t q = BEAT_U / 4u, len = emu_dub_seq_len();
    uint32_t now = (uint32_t)(((uint64_t)clk_beat * BEAT_U + clk_pos) / q);
    return len ? now % len : 0u;
}

WASM_EXPORT("emu_dub_seq_playing") uint32_t emu_dub_seq_playing(void)
{
    return song.playing ? 1u : 0u;                 /* the tracks play the steps, DUB or not */
}

WASM_EXPORT("emu_dub_riddim_name") uint32_t emu_dub_riddim_name(uint32_t riddim)   /* const char *, a wasm offset */
{
    return (uint32_t)(uintptr_t)dub_riddim_name(riddim);
}

WASM_EXPORT("emu_dub_riddim_load") void emu_dub_riddim_load(uint32_t riddim)   /* the whole riddim, the RIDDIM
                                                            * page's OCT+: the staging, then the tracks */
{
    dub_riddim_load(&dub_sequence, riddim);
    dub_tracks_load(&dub_sequence, (1u << DUB_TRK_N) - 1u, DUB_RIDDIM_STEPS);
}

WASM_EXPORT("emu_dub_riddim_track") void emu_dub_riddim_track(uint32_t riddim, uint32_t track)   /* one track's motif */
{
    dub_riddim_load_track(&dub_sequence, riddim, track);
    dub_tracks_load(&dub_sequence, track < DUB_TRK_N ? 1u << track : 0u, DUB_RIDDIM_STEPS);
}

WASM_EXPORT("emu_dub_sound_count") uint32_t emu_dub_sound_count(uint32_t role)   /* 0 bass, 1 skank, 2 melody, 3 kits */
{
    return role == 0u ? DUB_BASS_N : role == 1u ? DUB_SKANK_N : role == 2u ? DUB_MEL_N : DUB_DK_N;
}

WASM_EXPORT("emu_dub_sound_name") uint32_t emu_dub_sound_name(uint32_t role, uint32_t index)   /* const char *, a wasm offset */
{
    const char *n = role == 0u ? DUB_BASS_SOUNDS[index % DUB_BASS_N].name
                  : role == 1u ? DUB_SKANK_SOUNDS[index % DUB_SKANK_N].name
                  : role == 2u ? DUB_MEL_SOUNDS[index % DUB_MEL_N].name
                               : DUB_DK_NAMES[index % DUB_DK_N];
    return (uint32_t)(uintptr_t)n;
}

WASM_EXPORT("emu_dub_sound_load") void emu_dub_sound_load(uint32_t role, uint32_t index)
{                                   /* the PRESET page's OCT+: the engine switch, then the preset */
    const dub_sound_t *s;
    if (role == 3u) {
        TDRUM->p[P_E0] = (int16_t)DUB_DK_KITS[index % DUB_DK_N];
        return;
    }
    s = role == 0u ? &DUB_BASS_SOUNDS[index % DUB_BASS_N]
      : role == 1u ? &DUB_SKANK_SOUNDS[index % DUB_SKANK_N]
                   : &DUB_MEL_SOUNDS[index % DUB_MEL_N];
    set_engine_of(&trk[role % 3u], s->engine);
    apply_preset_to(&trk[role % 3u], s->preset);
}

static uint8_t emu_dub_skank_notes[DUB_SKANK_MAX_NOTES];
static uint8_t emu_dub_skank_count;
WASM_EXPORT("emu_dub_skank") void emu_dub_skank(uint32_t root, uint32_t quality, uint32_t octave, uint32_t velocity)
{
    dub_skank_t s;
    uint8_t notes[DUB_SKANK_MAX_NOTES];
    uint8_t i;
    for (i = 0; i < emu_dub_skank_count; i++)
        input_off(&trk[0], emu_dub_skank_notes[i]);
    s.root = (uint8_t)(root > 11u ? 11u : root);
    s.quality = (uint8_t)(quality & (DUB_SKANK_QUALITIES - 1u));
    s.octave = (uint8_t)(octave > 7u ? 7u : octave);
    s.velocity = (uint8_t)(velocity > 127u ? 127u : velocity);
    emu_dub_skank_count = dub_skank_build(&s, 0, notes, DUB_SKANK_MAX_NOTES);
    for (i = 0; i < emu_dub_skank_count; i++) {
        emu_dub_skank_notes[i] = notes[i];
        input_on(&trk[0], notes[i], s.velocity);
    }
}

WASM_EXPORT("emu_dub_preset") void emu_dub_preset(uint32_t index)
{
    const dub_preset_t *p;
    uint32_t b;
    if (index >= DUB_PRESET_COUNT)
        return;
    p = &DUB_PRESETS[index];
    for (b = 0; b < DUB_BANDS; b++) {
        dub_band_param_t q = dub_isolator.p[b];
        q.gain_db = (int8_t)(p->level / 2);
        q.mute = 0;
        dub_isolator_set_band(&dub_isolator, b, q);
    }
    dub_siren_trigger(&dub_siren, index == 2u ? 88u : 0u);
}
