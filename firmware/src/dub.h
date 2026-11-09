/* SPDX-License-Identifier: GPL-3.0-only
 * Reggae / dub extension API for the FM-1 SLOOP base.
 * The first tranche is deliberately independent from SLOOP's project format.
 */
#ifndef SLOOP_DUB_H
#define SLOOP_DUB_H

#include <stdint.h>

enum {
    DUB_SUB = 0,
    DUB_BASS = 1,
    DUB_MIDS = 2,
    DUB_TOPS = 3,
    DUB_BANDS = 4
};

typedef struct {
    int16_t cutoff_hz;
    int8_t gain_db;
    int8_t eq_freq;
    uint8_t eq_q;
    int8_t eq_db;
    uint8_t mute;
} dub_band_param_t;

typedef struct {
    dub_band_param_t p[DUB_BANDS];
    int32_t xover[3];
    int32_t eq_fast[DUB_BANDS];
    int32_t eq_slow[DUB_BANDS];
    int32_t lp[DUB_BANDS];
    uint8_t enabled;
    uint8_t mix;
} dub_isolator_t;

/* the siren's LFO curves (TYPE), the way the NJD boxes sweep: WAIL the slow up/down,
 * HI-LO the two tone, RAMP the yelp's charge and snap, SWEEP the fall, SPACE the sample and hold */
enum { DUB_SIR_WAIL = 0, DUB_SIR_HILO, DUB_SIR_RAMP, DUB_SIR_SWEEP, DUB_SIR_SPACE, DUB_SIR_TYPES };
extern const char *const DUB_SIR_TYPE_NAMES[DUB_SIR_TYPES];
/* the oscillator's curves (WAVE): the NJD's harsh square, a 25% pulse, the ramp, the soft ones */
enum { DUB_SIW_SQR = 0, DUB_SIW_PLS, DUB_SIW_SAW, DUB_SIW_TRI, DUB_SIW_SIN, DUB_SIW_N };
extern const char *const DUB_SIW_NAMES[DUB_SIW_N];

typedef struct {
    uint32_t phase;
    uint32_t lfo_phase;
    uint32_t phase_inc;
    uint32_t lfo_inc;
    int32_t lfo_val;           /* the LFO's last value, Q15 signed */
    int32_t lfo_target;        /* SPACE's sampled value, the one lfo_val glides toward */
    uint32_t rnd;              /* SPACE's noise state */
    uint16_t level;            /* the level the trigger / OCT+ set (the target) */
    uint16_t level_cur;        /* the rendered level, slewed so triggers and offs don't click */
    uint16_t freq_hz;          /* the siren's base pitch, 220..1200 (set_freq keeps it) */
    uint8_t depth;             /* the pitch sweep, 0..127 = 0..2 octaves each way (exponential) */
    uint8_t rate;              /* the LFO's speed, 0..127 = 1..16 Hz (dub_siren_rate_hz) */
    uint8_t type;              /* DUB_SIR_*, the LFO's curve */
    uint8_t wave;              /* DUB_SIW_*, the oscillator's curve */
    uint8_t sym;               /* the LFO's symmetry / duty / glide, 0..127 */
    uint8_t send;              /* the delay send, 0..127 */
    uint8_t active;
} dub_siren_t;

/* the dub sequence's tracks: the bass line, the skanks, the melody, the drums */
enum { DUB_TRK_BASS = 0, DUB_TRK_SKANK, DUB_TRK_MEL, DUB_TRK_DRUM, DUB_TRK_N };
extern const char *const DUB_TRK_NAMES[DUB_TRK_N];   /* "BASS", "SKNK", "MEL", "DRUM" */

typedef struct {
    uint8_t length;
    uint8_t step;
    uint8_t notes[DUB_TRK_N][64];
    uint8_t velocity[DUB_TRK_N][64];
} dub_seq_t;

/* the riddim bank (dub_riddim.h, tools/gen_riddims.py): ten 64-step sequences, four
 * tracks each. A step's note DUB_SEQ_REST (255) is a rest. The RIDDIM page loads a
 * whole riddim (OCT+ on KNOB 1) or one track's motif (OCT+ on KNOB 2..4) into the
 * dub sequence; seq.c plays it on the transport's sixteenths. */
#define DUB_SEQ_REST 255u
#define DUB_RIDDIM_STEPS 64u
typedef struct {
    const char *name;                              /* "ONE DROP", the LCD and the web tab */
    uint8_t note[DUB_TRK_N][DUB_RIDDIM_STEPS];
    uint8_t vel[DUB_TRK_N][DUB_RIDDIM_STEPS];
} dub_riddim_t;
extern const dub_riddim_t DUB_RIDDIMS[];

/* quality: 0 MAJ, 1 MIN, 2 DIM, 3 AUG, 4 7TH, 5 MIN7, 6 9TH, 7 PWR (root + fifth).
 * The build writes up to five note numbers, the count it wrote is returned. */
typedef struct {
    uint8_t root;
    uint8_t quality;
    uint8_t octave;
    uint8_t velocity;
} dub_skank_t;

/* the skank chords the SKANK page and the riddim's skank track both sound */
extern dub_skank_t dub_skank_conf;
extern const uint32_t DUB_RIDDIM_COUNT;                /* the bank's size, dub.c computes it */

/* 2.9.3: the dub sound banks, the PRESET page's lists. Each entry is a real engine preset
 * (its name), by ENGINES[] index and preset number: loading it is an engine switch then an
 * apply_preset_to, so the level trims and the rest of the patch come along as ever. */
typedef struct {
    const char *name;                              /* the engine preset's name, the LCD value */
    uint8_t engine;                                /* the ENGINES[] index (0 ANALOG, 6 TRIO...) */
    uint8_t preset;                                /* the preset's number in that engine */
} dub_sound_t;
extern const dub_sound_t DUB_BASS_SOUNDS[];            /* the bass line's sounds, track 1 */
extern const uint32_t DUB_BASS_N;
extern const dub_sound_t DUB_SKANK_SOUNDS[];           /* the skank's sounds, track 2 */
extern const uint32_t DUB_SKANK_N;
extern const dub_sound_t DUB_MEL_SOUNDS[];             /* the melody's sounds, track 3 */
extern const uint32_t DUB_MEL_N;
extern const uint8_t DUB_DK_KITS[];                    /* the drum kits (the drum track's P_E0) */
extern const char *const DUB_DK_NAMES[];               /* the kits' names, in DUB_DK_KITS's order */
extern const uint32_t DUB_DK_N;

#define DUB_SKANK_QUALITIES 8u
#define DUB_SKANK_MAX_NOTES 5u
extern const char *const DUB_SKANK_NAMES[DUB_SKANK_QUALITIES];   /* "MAJ", "MIN", ... */

typedef struct {
    const char *name;
    uint8_t engine;
    uint8_t preset;
    int8_t level;
    int8_t cutoff;
    int8_t resonance;
    int8_t delay;
    int8_t reverb;
    uint8_t chord;
} dub_preset_t;

void dub_isolator_init(dub_isolator_t *d);
void dub_isolator_process(dub_isolator_t *d, int32_t *left, int32_t *right, uint32_t n);
void dub_isolator_set_band(dub_isolator_t *d, uint32_t band, dub_band_param_t p);

void dub_siren_init(dub_siren_t *s);
void dub_siren_trigger(dub_siren_t *s, uint8_t level);
void dub_siren_set_freq(dub_siren_t *s, uint16_t hz);      /* 220..1200, clamped */
void dub_siren_set_rate(dub_siren_t *s, uint8_t rate);     /* 0..127 -> 1..16 Hz */
void dub_siren_set_type(dub_siren_t *s, uint8_t type);     /* DUB_SIR_*, clamped */
void dub_siren_set_wave(dub_siren_t *s, uint8_t wave);     /* DUB_SIW_*, clamped */
void dub_siren_set_sym(dub_siren_t *s, uint8_t sym);       /* the LFO's symmetry, 0..127 */
void dub_siren_set_send(dub_siren_t *s, uint8_t send);     /* the delay send, 0..127 */
uint32_t dub_siren_rate_hz(uint8_t rate);                  /* the rate's LFO speed, for the UI */
void dub_siren_render(dub_siren_t *s, int32_t *left, int32_t *right, int32_t *send_bus, uint32_t n);
                                                           /* send_bus may be NULL: no send rendered */

void dub_seq_init(dub_seq_t *s);
void dub_seq_set_length(dub_seq_t *s, uint8_t length);
void dub_seq_set_step(dub_seq_t *s, uint8_t track, uint8_t step, uint8_t note, uint8_t velocity);
void dub_seq_advance(dub_seq_t *s);
void dub_riddim_load(dub_seq_t *s, uint32_t riddim);                       /* the four tracks, 64 steps */
void dub_riddim_load_track(dub_seq_t *s, uint32_t riddim, uint32_t track); /* one track only */
const char *dub_riddim_name(uint32_t riddim);                              /* "ONE DROP", clamped */
/* 2.9.6 (seq.c): the load's commit — the staged sequence's steps written into the SLOOP
 * sequencer's tracks (the PATTERN / NOTES pages', the SEQ layer's, the transport's).
 * mask: a bit per track (DUB_TRK_*), len: the steps (64 a riddim). The one sequencer:
 * what loads is what plays and what the user edits afterwards. */
void dub_tracks_load(const dub_seq_t *s, uint32_t mask, uint8_t len);

uint8_t dub_skank_build(const dub_skank_t *s, uint8_t key, uint8_t *notes, uint8_t max_notes);

extern const dub_preset_t DUB_PRESETS[];
extern const uint32_t DUB_PRESET_COUNT;
extern dub_isolator_t dub_isolator;
extern dub_siren_t dub_siren;
extern dub_seq_t dub_sequence;
extern uint8_t dub_enabled;

#endif
