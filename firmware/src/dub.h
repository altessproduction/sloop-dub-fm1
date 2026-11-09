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

typedef struct {
    uint32_t phase;
    uint32_t lfo_phase;
    uint32_t phase_inc;
    uint32_t lfo_inc;
    uint16_t level;
    uint16_t freq_hz;          /* the siren's base pitch, 220..1200 (set_freq keeps it) */
    uint8_t depth;             /* the LFO's amplitude depth, 0..127 */
    uint8_t rate;              /* the LFO's speed, 0..127 = 1..16 Hz (dub_siren_rate_hz) */
    uint8_t active;
} dub_siren_t;

typedef struct {
    uint8_t length;
    uint8_t step;
    uint8_t notes[64];
    uint8_t velocity[64];
} dub_seq_t;

/* quality: 0 MAJ, 1 MIN, 2 DIM, 3 AUG, 4 7TH, 5 MIN7, 6 9TH, 7 PWR (root + fifth).
 * The build writes up to five note numbers, the count it wrote is returned. */
typedef struct {
    uint8_t root;
    uint8_t quality;
    uint8_t octave;
    uint8_t velocity;
} dub_skank_t;

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
uint32_t dub_siren_rate_hz(uint8_t rate);                  /* the rate's LFO speed, for the UI */
void dub_siren_render(dub_siren_t *s, int32_t *left, int32_t *right, uint32_t n);

void dub_seq_init(dub_seq_t *s);
void dub_seq_set_length(dub_seq_t *s, uint8_t length);
void dub_seq_set_step(dub_seq_t *s, uint8_t step, uint8_t note, uint8_t velocity);
void dub_seq_advance(dub_seq_t *s);

uint8_t dub_skank_build(const dub_skank_t *s, uint8_t key, uint8_t *notes, uint8_t max_notes);

extern const dub_preset_t DUB_PRESETS[];
extern const uint32_t DUB_PRESET_COUNT;
extern dub_isolator_t dub_isolator;
extern dub_siren_t dub_siren;
extern dub_seq_t dub_sequence;
extern uint8_t dub_enabled;

#endif
