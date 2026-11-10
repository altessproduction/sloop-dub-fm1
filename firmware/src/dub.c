/* SPDX-License-Identifier: GPL-3.0-only
 * First playable reggae / dub modules for SLOOP on M-VAVE FM-1.
 */
#include <stdint.h>
#include "dub.h"
#include "dub_riddim.h"

#ifndef FS
#define FS 44100u
#endif

#define DUB_Q15 32767
#define DUB_PI2 0x6487ED51u

static int32_t dub_clamp(int32_t x, int32_t lo, int32_t hi)
{
    return x < lo ? lo : x > hi ? hi : x;
}

static int32_t dub_mul15(int32_t a, int32_t b)
{
    return (int32_t)(((int64_t)a * b) >> 15);
}

static int32_t dub_sine(uint32_t phase)
{
    uint32_t q = phase >> 30;
    uint32_t x = (phase >> 15) & 0x7FFFu;
    int32_t y = (int32_t)x;
    if (q & 1u)
        y = 32767 - y;
    if (q & 2u)
        y = -y;
    return (int32_t)((uint32_t)y << 1);            /* the shift unsigned: y is negative half
                                                    * the time and a signed left shift is
                                                    * none of the standard's business */
}

static uint32_t dub_hz_inc(uint32_t hz)
{
    return (uint32_t)(((uint64_t)hz << 32) / FS);
}

void dub_isolator_init(dub_isolator_t *d)
{
    static const int32_t xo[3] = {90, 420, 2600};
    static const int16_t cuts[4] = {90, 180, 1000, 4200};
    uint32_t i;
    d->enabled = 0;
    d->mix = 127;
    for (i = 0; i < 3; i++)
        d->xover[i] = xo[i];
    for (i = 0; i < DUB_BANDS; i++) {
        d->p[i].cutoff_hz = cuts[i];
        d->p[i].gain_db = 0;
        d->p[i].eq_freq = 64;
        d->p[i].eq_q = 64;
        d->p[i].eq_db = 0;
        d->p[i].mute = 0;
        d->eq_fast[i] = d->eq_slow[i] = 0;
        d->lp[i] = 0;
    }
}

void dub_isolator_set_band(dub_isolator_t *d, uint32_t band, dub_band_param_t p)
{
    if (band >= DUB_BANDS)
        return;
    d->p[band] = p;
    d->p[band].gain_db = (int8_t)dub_clamp(d->p[band].gain_db, -24, 12);
    d->p[band].eq_db = (int8_t)dub_clamp(d->p[band].eq_db, -12, 12);
    d->p[band].eq_q = (uint8_t)dub_clamp(d->p[band].eq_q, 1, 127);
}

static int32_t dub_gain(int8_t db)
{
    int32_t g = 32767;
    int32_t i;
    if (db > 0)
        for (i = 0; i < db; i++)
            g = (g * 36700) >> 15;
    else
        for (i = 0; i > db; i--)
            g = (g * 29200) >> 15;
    return g;
}

static int32_t dub_lowpass(int32_t x, int32_t *state, int32_t hz)
{
    int32_t a = dub_clamp((hz * 205887) / (int32_t)FS, 1, 32700);   /* 2 pi in Q15 a hertz: 90/420/2600 Hz
                                                                     * land where the crossovers say (2.9.17:
                                                                     * 2100 put them a hundred times lower,
                                                                     * the SUB BASS MIDS bands stood empty
                                                                     * and TOPS carried the whole signal) */
    *state += dub_mul15(x - *state, a);
    return *state;
}

void dub_isolator_process(dub_isolator_t *d, int32_t *left, int32_t *right, uint32_t n)
{
    uint32_t i, b, live = 0;
    if (!d->enabled || !d->mix)
        return;
    for (b = 0; b < DUB_BANDS; b++)                /* (2.9.11) every knob at rest: the module stands
                                                    * aside and the original passes bit for bit —
                                                    * the stereo kept, no smoother's colour */
        if (d->p[b].gain_db || d->p[b].eq_db || d->p[b].mute) {
            live = 1;
            break;
        }
    if (!live)
        return;
    for (i = 0; i < n; i++) {
        int32_t in_l = left[i], in_r = right[i];
        int32_t mono = (in_l + in_r) >> 1;
        int32_t low = dub_lowpass(mono, &d->lp[DUB_SUB], d->xover[0]);
        int32_t low_mid = dub_lowpass(mono - low, &d->lp[DUB_BASS], d->xover[1]);
        int32_t mid = dub_lowpass(mono - low - low_mid, &d->lp[DUB_MIDS], d->xover[2]);
        int32_t bands[DUB_BANDS];
        int32_t wet_l = 0, wet_r = 0;
        bands[DUB_SUB] = low;
        bands[DUB_BASS] = low_mid;
        bands[DUB_MIDS] = mid;
        bands[DUB_TOPS] = mono - low - low_mid - mid;
        for (b = 0; b < DUB_BANDS; b++) {
            int32_t out = bands[b];                /* (2.9.11) the band out: itself, or its EQ laid on
                                                    * once — the smoothers shape the EQ's reference
                                                    * only, they never filter the sound again */
            int32_t q = d->p[b].eq_q + 1;
            d->eq_fast[b] += (bands[b] - d->eq_fast[b]) / q;
            d->eq_slow[b] += (d->eq_fast[b] - d->eq_slow[b]) >> 4;
            if (d->p[b].eq_db)
                out += (bands[b] - d->eq_slow[b]) * d->p[b].eq_db / 24;
            if (!d->p[b].mute)
                wet_l += dub_mul15(out, dub_gain(d->p[b].gain_db));
        }
        wet_r = wet_l;
        left[i] = in_l + ((wet_l - in_l) * d->mix >> 7);
        right[i] = in_r + ((wet_r - in_r) * d->mix >> 7);
    }
}

/* ------------------------------------- 2.9.7: the DUB page's filter and throw --- */
/* KNOB 2: a bipolar filter on the module's output — 0..63 lowpass (the deeper the
 * lower), 64 neutral (the center detent: the untouched signal, no filter run),
 * 65..127 highpass (the deeper the higher). One state-variable filter a channel; the
 * cutoff and the dry/wet amount glide block to block, so a sweep slides and crossing
 * the center never clicks. KNOB 4: the throw — the module's output added into the
 * project's delay send bus, its gain gliding too (dub_send_feed). The DLY page runs
 * that bus tape while DUB is on (fx.c): SYNC off the free ms (dub_dly_ms) rules, SYNC
 * on the project's division (song.g[G_DTIME]) as the delay always did. */

uint8_t dub_send;
uint8_t dub_dly_sync = 1;
uint16_t dub_dly_ms = 400;

static int32_t dub_exp2(int32_t x);              /* (below, with the siren's sweep table) */

typedef struct { int32_t low, band; } dub_svf_t;

static struct {
    int16_t v;                       /* the knob, 0..127, 64 neutral */
    int32_t amt, amt_t;              /* the dry/wet share, Q15, gliding to amt_t */
    int32_t hz, hz_t;                /* the cutoff, gliding to hz_t */
    int32_t lp;                      /* 1 lowpass, 0 highpass (where the amount > 0) */
    int32_t send, send_t;            /* the throw's gain, Q15, gliding to send_t */
} dub_flt = {64, 0, 0, 16000, 16000, 1, 0, 0};
static dub_svf_t dub_flt_ch[2];

void dub_filter_set(int16_t v)
{
    int32_t d;                       /* the depth out of neutral, Q15 */
    int16_t was = dub_flt.v;
    dub_flt.v = (int16_t)dub_clamp(v, 0, 127);
    if (dub_flt.v < 64) {
        d = ((int32_t)(63 - dub_flt.v) << 15) / 64;
        dub_flt.lp = 1;
        dub_flt.hz_t = (16000 * dub_exp2(-7 * d)) >> 15;    /* 16 kHz down to 125 Hz */
    } else if (dub_flt.v > 64) {
        d = ((int32_t)(dub_flt.v - 64) << 15) / 63;
        dub_flt.lp = 0;
        dub_flt.hz_t = (30 * dub_exp2(7 * d)) >> 15;        /* 30 Hz up to 3.8 kHz */
    } else {
        d = 0;
        dub_flt.hz_t = 16000;
    }
    dub_flt.amt_t = d;
    if (dub_flt.v != was && !dub_flt.amt_t)          /* woke the filter: it starts on its
                                                      * target, not from a stale cutoff */
        dub_flt.hz = dub_flt.hz_t;
}

int16_t dub_filter_get(void) { return dub_flt.v; }

uint32_t dub_filter_hz(int16_t v)                /* the knob's cutoff, for the UI */
{
    int32_t d;
    if (v == 64)
        return 16000;                            /* the neutral: flat, nothing filtered */
    if (v < 64) {
        d = ((int32_t)(63 - v) << 15) / 64;
        return (uint32_t)((16000 * dub_exp2(-7 * d)) >> 15);
    }
    d = ((int32_t)(v - 64) << 15) / 63;
    return (uint32_t)((30 * dub_exp2(7 * d)) >> 15);
}

void dub_filter_process(int32_t *left, int32_t *right, uint32_t n)
{
    uint32_t i;
    int32_t amt, f, q = 29491;       /* the damping: a mild resonance, stable for f < q */
    if (!dub_flt.amt && !dub_flt.amt_t)
        return;                      /* the neutral: the untouched signal, no filter run */
    if (dub_flt.amt != dub_flt.amt_t) {
        int32_t st = (dub_flt.amt_t - dub_flt.amt) >> 3;
        if (!st)
            st = dub_flt.amt_t > dub_flt.amt ? 1 : -1;
        dub_flt.amt += st;
    }
    if (dub_flt.hz != dub_flt.hz_t) {
        int32_t st = (dub_flt.hz_t - dub_flt.hz) >> 3;
        if (!st)
            st = dub_flt.hz_t > dub_flt.hz ? 16 : -16;
        dub_flt.hz += st;
    }
    f = (int32_t)(((int64_t)dub_flt.hz * 205887) / FS);    /* 2 sin(pi fc/fs) ~ 2 pi fc/fs, Q15 */
    if (f < 1)
        f = 1;
    if (f > 8000)
        f = 8000;
    amt = dub_flt.amt;
    for (i = 0; i < n; i++) {
        int32_t inl = left[i], inr = right[i], outl, outh, outr, our;
        outl = dub_flt_ch[0].low + dub_mul15(dub_flt_ch[0].band, f);
        outh = inl - outl - dub_mul15(dub_flt_ch[0].band, q);
        dub_flt_ch[0].band += dub_mul15(outh, f);
        dub_flt_ch[0].low = outl;
        outr = dub_flt_ch[1].low + dub_mul15(dub_flt_ch[1].band, f);
        our = inr - outr - dub_mul15(dub_flt_ch[1].band, q);
        dub_flt_ch[1].band += dub_mul15(our, f);
        dub_flt_ch[1].low = outr;
        if (dub_flt.lp) {
            left[i] = inl + dub_mul15(outl - inl, amt);
            right[i] = inr + dub_mul15(outr - inr, amt);
        } else {
            left[i] = inl + dub_mul15(outh - inl, amt);
            right[i] = inr + dub_mul15(our - inr, amt);
        }
    }
}

void dub_send_set(uint8_t v) { dub_send = v > 127u ? 127u : v; }

void dub_send_feed(const int32_t *left, const int32_t *right, int32_t *dly_bus, uint32_t n)
{
    uint32_t i;
    int32_t g, st;
    dub_flt.send_t = (int32_t)dub_send * 258;            /* 0..127 -> Q15 */
    if (dub_flt.send != dub_flt.send_t) {
        st = (dub_flt.send_t - dub_flt.send) >> 3;
        if (!st)
            st = dub_flt.send_t > dub_flt.send ? 1 : -1;
        dub_flt.send += st;
    }
    g = dub_flt.send;
    if (!g)
        return;
    for (i = 0; i < n; i++)
        dly_bus[i] += dub_mul15((left[i] + right[i]) >> 1, g);
}

void dub_dly_set_ms(uint16_t ms) { dub_dly_ms = ms < 40u ? 40u : ms > 1400u ? 1400u : ms; }
void dub_dly_set_sync(uint8_t on) { dub_dly_sync = on ? 1u : 0u; }

const char *const DUB_SIR_TYPE_NAMES[DUB_SIR_TYPES] = {"WAIL", "HILO", "RAMP", "SWEEP", "SPACE"};
const char *const DUB_SIW_NAMES[DUB_SIW_N] = {"SQR", "PLS", "SAW", "TRI", "SIN"};

/* 2^(i/32) in Q15, i = 0..31: the exponential pitch sweep's fractional table (dub_exp2) */
static const int32_t DUB_EXP2[32] = {
    32768, 33486, 34219, 34968, 35734, 36516, 37316, 38133,
    38968, 39821, 40693, 41584, 42495, 43425, 44376, 45348,
    46341, 47356, 48393, 49452, 50535, 51642, 52773, 53928,
    55109, 56316, 57549, 58809, 60097, 61413, 62757, 64132
};

/* 2^x, x in Q15 octaves (-2.00..2.00 -> 8192..131072 in Q15 scale, the caller shifts) */
static int32_t dub_exp2(int32_t x)
{
    int32_t i = x >> 15;                           /* arithmetic shift: the floor, also for x < 0 */
    uint32_t f = ((uint32_t)x & 0x7FFFu) >> 10;    /* the fraction, 0..31: x - floor(x) is x's
                                                    * low fifteen bits, so no shift of a
                                                    * negative i (2.9.17: the UBsan saw one) */
    return i >= 0 ? (int32_t)DUB_EXP2[f] << i : (int32_t)DUB_EXP2[f] >> -i;
}

void dub_siren_init(dub_siren_t *s)
{
    s->phase = 0;
    s->lfo_phase = 0;
    s->phase_inc = dub_hz_inc(740);
    s->lfo_inc = dub_hz_inc(2);
    s->lfo_val = 0;
    s->lfo_target = 0;
    s->rnd = 0x1234567u;
    s->level = 0;
    s->level_cur = 0;
    s->freq_hz = 740;
    s->depth = 96;
    s->rate = 8;                                   /* rate 8 of 0..127 = 2 Hz, as the first build had */
    s->type = DUB_SIR_WAIL;                        /* the NJD's slow up and down, by default */
    s->wave = DUB_SIW_SQR;                         /* the NJD's harsh square, by default */
    s->sym = 64;
    s->send = 0;
    s->active = 0;
}

void dub_siren_trigger(dub_siren_t *s, uint8_t level)
{
    s->level = level > 127 ? 127 : level;
    s->active = s->level != 0;
}

uint32_t dub_siren_rate_hz(uint8_t rate)           /* 0..127 -> 1..16 Hz, rounded, the UI shows the same */
{
    return 1u + ((uint32_t)(rate > 127u ? 127u : rate) * 15u + 63u) / 127u;
}

void dub_siren_set_freq(dub_siren_t *s, uint16_t hz)
{
    if (hz < 220u)
        hz = 220u;
    else if (hz > 1200u)
        hz = 1200u;
    s->freq_hz = hz;
    s->phase_inc = dub_hz_inc(hz);
}

void dub_siren_set_rate(dub_siren_t *s, uint8_t rate)
{
    s->rate = rate > 127u ? 127u : rate;
    s->lfo_inc = dub_hz_inc(dub_siren_rate_hz(s->rate));
}

void dub_siren_set_type(dub_siren_t *s, uint8_t type)
{
    s->type = type >= DUB_SIR_TYPES ? (uint8_t)(DUB_SIR_TYPES - 1u) : type;
    if (s->type == DUB_SIR_SPACE && s->lfo_val == 0)
        s->lfo_val = s->lfo_target;                /* pick up where the S and H stands */
}

void dub_siren_set_wave(dub_siren_t *s, uint8_t wave)
{
    s->wave = wave >= DUB_SIW_N ? (uint8_t)(DUB_SIW_N - 1u) : wave;
}

void dub_siren_set_sym(dub_siren_t *s, uint8_t sym)
{
    s->sym = sym > 127u ? 127u : sym;
}

void dub_siren_set_send(dub_siren_t *s, uint8_t send)
{
    s->send = send > 127u ? 127u : send;
}

/* the LFO's curve at t = 0..255 (the high LFO phase byte): every type has its symmetry's say */
static int32_t dub_sir_shape(dub_siren_t *s, uint32_t t)
{
    uint32_t a = 32u + ((uint32_t)s->sym * 191u >> 7);   /* the symmetry, 32..223 of 256 */
    switch (s->type) {
    case DUB_SIR_HILO:                                 /* the two tone: the square's duty is the symmetry */
        return t < a ? 32767 : -32767;
    case DUB_SIR_RAMP:                                 /* the yelp: it charges up over the symmetry, snaps back */
        return t < a ? (int32_t)(-32767 + (int32_t)((t * 65534u) / a)) : -32767;
    case DUB_SIR_SWEEP:                                /* the fall: it falls over the symmetry, snaps up */
        return t < a ? (int32_t)(32767 - (int32_t)((t * 65534u) / a)) : -32767;
    default:                                           /* WAIL: the triangle, its peak where the symmetry puts it */
        return t < a ? (int32_t)(-32767 + (int32_t)((t * 65534u) / a))
                     : (int32_t)(32767 - (int32_t)(((t - a) * 65534u) / (256u - a)));
    }
}

/* the oscillator's curve, Q15 signed: the NJD's square and its softer friends */
static int32_t dub_sir_osc(dub_siren_t *s, uint32_t ph)
{
    switch (s->wave) {
    case DUB_SIW_SQR:
        return ph >> 31 ? -32767 : 32767;
    case DUB_SIW_PLS:                                  /* the 25% pulse: a thinner, buzzier square */
        return (ph >> 30) == 0u ? 32767 : -32767;
    case DUB_SIW_SAW:
        return (int32_t)(ph >> 16) - 32768;
    case DUB_SIW_TRI: {
        uint32_t x = ph >> 16;
        int32_t y = (ph >> 30) & 1u ? (int32_t)(65535u - x) : (int32_t)x;
        return y - 32768;
    }
    default:
        return dub_sine(ph) >> 1;                      /* SIN */
    }
}

void dub_siren_render(dub_siren_t *s, int32_t *left, int32_t *right, int32_t *send_bus, uint32_t n)
{
    uint32_t i;
    int32_t lev = (int32_t)s->level_cur, tgt = (int32_t)s->level;
    if (!s->active && lev == 0)
        return;
    for (i = 0; i < n; i++) {
        int32_t lfo, oct, y;
        uint32_t inc;
        if (s->type == DUB_SIR_SPACE) {                /* the S and H: a new value every LFO cycle, glided */
            if (s->lfo_phase < s->lfo_inc)
                s->lfo_target = (int32_t)(s->rnd = s->rnd * 1664525u + 1013904223u) >> 16;
            s->lfo_val += (s->lfo_target - s->lfo_val) >> (10u - (uint32_t)(s->sym >> 5));
        } else
            s->lfo_val = dub_sir_shape(s, s->lfo_phase >> 24);
        lfo = s->lfo_val;
        /* the pitch: the base times 2^(depth * LFO), the sweep the real sirens sweep with */
        oct = (int32_t)(((int64_t)lfo * ((int32_t)s->depth * 516)) >> 15);
        inc = (uint32_t)(((uint64_t)s->phase_inc * (uint64_t)dub_exp2(oct)) >> 15);
        s->phase += inc;
        s->lfo_phase += s->lfo_inc;
        lev += tgt > lev ? 1 : tgt < lev ? -1 : 0;     /* the level's slew: no click on trigger or off */
        y = (dub_sir_osc(s, s->phase) * lev) >> 6;     /* the same hot scale the first siren had */
        left[i] += y;
        right[i] += y;
        if (send_bus && s->send)
            send_bus[i] += (y * (int32_t)s->send) >> 7;
    }
    s->level_cur = (uint16_t)lev;
}

void dub_seq_init(dub_seq_t *s)
{
    uint32_t t, i;
    s->length = 16;
    s->step = 0;
    for (t = 0; t < DUB_TRK_N; t++)
        for (i = 0; i < 64u; i++) {
            s->notes[t][i] = DUB_SEQ_REST;             /* a rest: nothing plays until written */
            s->velocity[t][i] = 0;
        }
}

void dub_seq_set_length(dub_seq_t *s, uint8_t length)
{
    if (length == 16 || length == 32 || length == 64)
        s->length = length;
}

void dub_seq_set_step(dub_seq_t *s, uint8_t track, uint8_t step, uint8_t note, uint8_t velocity)
{
    if (track >= DUB_TRK_N || step >= 64)
        return;
    s->notes[track][step] = note > 127u ? DUB_SEQ_REST : note;
    s->velocity[track][step] = velocity;
}

void dub_seq_advance(dub_seq_t *s)
{
    s->step++;
    if (s->step >= s->length)
        s->step = 0;
}

const char *const DUB_TRK_NAMES[DUB_TRK_N] = {"BASS", "SKNK", "MEL", "DRUM"};

void dub_riddim_load(dub_seq_t *s, uint32_t riddim)            /* the whole riddim: four tracks, 64 steps */
{
    uint32_t tr, st;
    if (riddim >= DUB_RIDDIM_COUNT)
        riddim %= DUB_RIDDIM_COUNT;
    for (tr = 0; tr < DUB_TRK_N; tr++) {
        for (st = 0; st < DUB_RIDDIM_STEPS; st++) {
            s->notes[tr][st] = DUB_RIDDIMS[riddim].note[tr][st];
            s->velocity[tr][st] = DUB_RIDDIMS[riddim].vel[tr][st];
        }
    }
    s->length = 64;                                            /* a riddim plays its four bars whole */
    s->step = 0;
}

void dub_riddim_load_track(dub_seq_t *s, uint32_t riddim, uint32_t track)   /* one track's motif only */
{
    uint32_t st;
    if (riddim >= DUB_RIDDIM_COUNT)
        riddim %= DUB_RIDDIM_COUNT;
    if (track >= DUB_TRK_N)
        return;
    for (st = 0; st < DUB_RIDDIM_STEPS; st++) {
        s->notes[track][st] = DUB_RIDDIMS[riddim].note[track][st];
        s->velocity[track][st] = DUB_RIDDIMS[riddim].vel[track][st];
    }
    if (s->length < DUB_RIDDIM_STEPS) {
        s->length = 64;                                        /* the motif's bars need the four */
        s->step = 0;
    }
}

const char *dub_riddim_name(uint32_t riddim)
{
    return DUB_RIDDIMS[riddim >= DUB_RIDDIM_COUNT ? 0u : riddim].name;
}

const char *const DUB_SKANK_NAMES[DUB_SKANK_QUALITIES] =
    {"MAJ", "MIN", "DIM", "AUG", "7TH", "MIN7", "9TH", "PWR"};

uint8_t dub_skank_build(const dub_skank_t *s, uint8_t key, uint8_t *notes, uint8_t max_notes)
{
    /* the chord's intervals from the root; 9TH reaches its ninth an octave up */
    static const uint8_t chord[DUB_SKANK_QUALITIES][5] = {
        {0, 4, 7, 255, 255},           /* MAJ  */
        {0, 3, 7, 255, 255},           /* MIN  */
        {0, 3, 6, 255, 255},           /* DIM  */
        {0, 4, 8, 255, 255},           /* AUG  */
        {0, 4, 7, 10, 255},            /* 7TH  */
        {0, 3, 7, 10, 255},            /* MIN7 */
        {0, 4, 7, 10, 14},             /* 9TH  */
        {0, 7, 255, 255, 255}          /* PWR  */
    };
    uint8_t q = s->quality & (DUB_SKANK_QUALITIES - 1u);
    uint8_t root = (uint8_t)(s->root + key + 12u * s->octave);
    uint8_t i, count = 0;
    for (i = 0; i < DUB_SKANK_MAX_NOTES && count < max_notes; i++) {
        if (chord[q][i] == 255u)
            break;
        notes[count++] = (uint8_t)(root + chord[q][i]);
    }
    return count;
}

const dub_preset_t DUB_PRESETS[] = {
    {"ROOTS BASS", 1, 0, 0, -12, 8, 36, 18, 0},
    {"SKANK CHORD", 2, 2, -4, 8, 22, 28, 42, 1},
    {"DUB SIREN", 3, 1, -8, 22, 12, 54, 38, 0},
    {"STEPPERS", 4, 3, -2, -4, 16, 18, 28, 0},
    {"TAPE ECHO", 5, 0, -6, 4, 10, 82, 66, 0}
};
const uint32_t DUB_PRESET_COUNT = sizeof DUB_PRESETS / sizeof DUB_PRESETS[0];

dub_isolator_t dub_isolator;
dub_siren_t dub_siren;
dub_seq_t dub_sequence;
dub_skank_t dub_skank_conf = {45, 1, 3, 108};                  /* A MIN, octave 3, the SKANK page's chord too */
const uint32_t DUB_RIDDIM_COUNT = sizeof DUB_RIDDIMS / sizeof DUB_RIDDIMS[0];
uint8_t dub_enabled = 0;

/* 2.9.3: the dub sound banks (dub.h). Engine indices: 0 ANALOG, 1 DIGITAL, 2 PHASE,
 * 3 LOFI, 6 TRIO, 7 DRAWBAR, 10 PHYS. The preset numbers are the engines' own banks:
 * the names are theirs, the level trims and the patches come with apply_preset_to. */
const dub_sound_t DUB_BASS_SOUNDS[] = {
    {"SUB BASS", 0, 2}, {"808 BOOM", 0, 0}, {"FAT BASS", 6, 0}, {"REESE", 0, 6},
    {"WOBBLE", 0, 7}, {"ACID 303", 0, 4}, {"CZ BASS", 2, 0}, {"NES BASS", 3, 3},
};
const uint32_t DUB_BASS_N = sizeof DUB_BASS_SOUNDS / sizeof DUB_BASS_SOUNDS[0];
const dub_sound_t DUB_SKANK_SOUNDS[] = {
    {"DUB CHORD", 6, 4}, {"MIN STAB", 6, 1}, {"MIN7 STAB", 6, 2}, {"REGGAE ORG", 7, 7},
    {"DIRTY B3", 7, 3}, {"SOUL ORGAN", 7, 0}, {"AFRO KEYS", 1, 5}, {"CHIP CHORD", 3, 4},
};
const uint32_t DUB_SKANK_N = sizeof DUB_SKANK_SOUNDS / sizeof DUB_SKANK_SOUNDS[0];
const dub_sound_t DUB_MEL_SOUNDS[] = {
    {"PAN FLUTE", 0, 16}, {"STEELPAN", 10, 21}, {"STEEL DRUM", 1, 13}, {"KALIMBA", 1, 9},
    {"SQR LEAD", 6, 11}, {"SYNC LEAD", 6, 6}, {"FAT LEAD", 0, 17}, {"CZ LEAD", 2, 5},
};
const uint32_t DUB_MEL_N = sizeof DUB_MEL_SOUNDS / sizeof DUB_MEL_SOUNDS[0];
/* the drum kits, the drum track's P_E0 (drums.c DRUM_KIT_NAMES: 1 DEEP, 4 DUST, 9 VINTAGE,
 * 5 808, 23 DUBSTEP, 24 DEMBOW, 25 AMAPIANO, 26 AFRO) */
const uint8_t DUB_DK_KITS[] = {1, 4, 9, 5, 23, 24, 25, 26};
const char *const DUB_DK_NAMES[] = {"DEEP", "DUST", "VINTAGE", "808", "DUBSTEP", "DEMBOW", "AMAPIANO", "AFRO"};
const uint32_t DUB_DK_N = sizeof DUB_DK_KITS / sizeof DUB_DK_KITS[0];
