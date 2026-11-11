/* SPDX-License-Identifier: GPL-3.0-only
 * Copyright (C) 2026 Leo Kuroshita (@kurogedelic), Hügelton Instruments */
/* DIGITAL: four-operator FM. */
/* Four sine operators, eight classic 4-operator algorithms (ALG = P_E0, EDIT 1 KNOB 1),
 * op 4 with feedback, one modulation INDEX shaped by a modulator envelope.
 * Phase modulation wraps naturally in the 32-bit phase. */
static const char *const N_FMALG[] = {"1", "2", "3", "4", "5", "6", "7", "8"};
static const char *const N_RATIO[] = {".5", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "14", "16"};
static const uint16_t RATIO_Q8[15] = {128, 256, 512, 768, 1024, 1280, 1536, 1792, 2048, 2304, 2560, 2816,
                                      3072, 3584, 4096};

static void digital_note_on(track_t *t, voice_t *v)
{
    (void)t;
    v->ph[0] = v->ph[1] = v->ph[2] = 0;
    v->s[7] = 0;                 /* op 4 phase */
    v->s[4] = 1 << 24;           /* modulator envelope, Q24 */
    v->s[5] = v->s[6] = 0;       /* feedback history */
}

/* operator increment = carrier * ratio (Q8) without 32-bit overflow; kept below Nyquist */
static inline uint32_t fm_ratio_inc(uint32_t inc, uint32_t r)
{
    uint32_t lim = 0x73000000u / r;                      /* (inc >> 8) * r must stay < 0x73000000 */
    return (inc >> 8) > lim ? 0x73000000u : (inc >> 8) * r;
}

static inline uint32_t digital_mod(int32_t x, int32_t idx) { return (uint32_t)(x * idx) * 2065u; }

static void digital_render(track_t *t, voice_t *v, int32_t *out, uint32_t n, const vmod_t *m)
{
    const int16_t *p = t->p;
    uint32_t alg = (uint32_t)p[P_E0] & 7u, i;
    uint32_t i1 = m->inc;
    uint32_t i2 = fm_ratio_inc(m->inc, RATIO_Q8[p[P_E1] % 15]), i3 = fm_ratio_inc(m->inc, RATIO_Q8[p[P_E2] % 15]);
    uint32_t i4 = fm_ratio_inc(m->inc, RATIO_Q8[p[P_E3] % 15]);
    int32_t me, idx, fb = p[P_E6], fb1, fb2;                 /* fb1, fb2: op 4 feedback history */
    uint32_t ph0, ph1, ph2, ph4;
    /* modulator envelope: decays (MODDEC) towards 25 %, per block */
    v->s[4] += mulq16((1 << 22) - v->s[4], ENV_EXP[p[P_E5] & 127]);
    me = v->s[4] >> 9;                                         /* Q15 */
    idx = (p[P_E4] * me) >> 15;                                 /* 0..127 */
    idx = clamp(idx + ((m->cutoff + m->shape - (64 << 8)) >> 8) + (v->vel - 96) / 4, 0, 127);
    ph0 = v->ph[0];                                             /* state in locals: out[] may alias v->s[] */
    ph1 = v->ph[1];
    ph2 = v->ph[2];
    ph4 = (uint32_t)v->s[7];
    fb1 = v->s[5];
    fb2 = v->s[6];
    for (i = 0; i < n; i++) {
        int32_t o1, o2, o3, o4, s;
        o4 = sine_i((ph4 + digital_mod((fb1 + fb2) >> 1, fb)));
        fb2 = fb1;
        fb1 = o4;
        switch (alg) {
        case 0:
            o3 = sine_i((ph2 + digital_mod(o4, idx)));
            o2 = sine_i((ph1 + digital_mod(o3, idx)));
            s = sine_i((ph0 + digital_mod(o2, idx)));
            break;
        case 1:
            o3 = sine_i(ph2);
            o2 = sine_i((ph1 + digital_mod((o3 + o4) >> 1, idx)));
            s = sine_i((ph0 + digital_mod(o2, idx)));
            break;
        case 2:
            o3 = sine_i(ph2);
            o2 = sine_i((ph1 + digital_mod(o3, idx)));
            s = sine_i((ph0 + digital_mod((o2 + o4) >> 1, idx)));
            break;
        case 3:
            o3 = sine_i((ph2 + digital_mod(o4, idx)));
            o2 = sine_i(ph1);
            s = sine_i((ph0 + digital_mod((o2 + o3) >> 1, idx)));
            break;
        case 4:
            o3 = sine_i((ph2 + digital_mod(o4, idx)));
            o2 = sine_i(ph1);
            o1 = sine_i((ph0 + digital_mod(o2, idx)));
            s = (o1 + o3) >> 1;
            break;
        case 5:
            o3 = sine_i((ph2 + digital_mod(o4, idx)));
            o2 = sine_i((ph1 + digital_mod(o4, idx)));
            o1 = sine_i((ph0 + digital_mod(o4, idx)));
            s = mulq15(o1 + o2 + o3, 10923);           /* / 3 without a divide */
            break;
        case 6:
            o3 = sine_i((ph2 + digital_mod(o4, idx)));
            o2 = sine_i(ph1);
            o1 = sine_i(ph0);
            s = mulq15(o1 + o2 + o3, 10923);           /* / 3 without a divide */
            break;
        default:
            o3 = sine_i(ph2);
            o2 = sine_i(ph1);
            o1 = sine_i(ph0);
            s = (o1 + o2 + o3 + o4) >> 2;
            break;
        }
        ph0 += i1;
        ph1 += i2;
        ph2 += i3;
        ph4 += i4;
        out[i] += mulq15(mulq15(s, amp_at(m, i)), VOICE_FS);   /* full-scale sines: 6 dB below the others */
    }
    v->ph[0] = ph0;
    v->ph[1] = ph1;
    v->ph[2] = ph2;
    v->s[7] = (int32_t)ph4;
    v->s[5] = fb1;
    v->s[6] = fb2;
}

static const preset_t DIGITAL_PRESETS[] = {
    /* SLOOP DUB FM bank. {ALG R2 R3 R4 INDEX MODDEC FDBK -} ; ALG 5 (4 here) = two stacks: 2 -> 1 and
     * 4 -> 3 (the tine). Keys skank on the tine stack, stabs and horns on the brass-ish ratios, the
     * FM subs on ALG 1 (op 4 a sub-octave modulator into the stack). */
    /* skank keys: bright tine, round roots tine, the rub-a-dub piano */
    {"DX SKANK", {4, 1, 1, 14, 58, 30, 0, 0}, {0, 80, 40, 50}, 0, 0, FX(0, 25, 16, 26), XP(P_LD_AMP + 1, 22, P_LRATE + 1, 84)},
    {"SKA PIANO", {4, 1, 2, 13, 84, 22, 8, 0}, {0, 72, 26, 40}, 0, 0, FX(0, 15, 12, 22)},
    {"DUB TINE", {4, 1, 1, 14, 30, 42, 0, 0}, {0, 84, 44, 58}, 0, 0, FX(0, 28, 24, 32), XP(P_LD_AMP + 1, 24, P_LRATE + 1, 80)},
    {"ROOTS CLAV", {3, 1, 3, 5, 88, 26, 22, 0}, {0, 58, 36, 18}, 0, 0, FX(12, 10, 8, 12)},
    {"NITE EP", {4, 1, 2, 3, 66, 34, 10, 0}, {0, 78, 34, 46}, 0, 0, FX(0, 20, 14, 22)},
    /* bells: the amen drop bell, the dub bell into the delay, the ragga bell */
    {"AMEN BELL", {4, 8, 1, 4, 74, 72, 0, 0}, {0, 92, 0, 72}, 0, 0, FX(0, 0, 30, 40), XP(P_TRANS + 1, 12)},
    {"DUB BELL", {4, 6, 1, 13, 50, 86, 0, 0}, {0, 100, 0, 88}, 0, 0, FX(0, 10, 36, 50)},
    /* FM subs: pure, punchy, the steppers one, the jungle one (a metallic modulator) */
    {"FM SUB", {0, 1, 1, 1, 30, 44, 8, 0}, {0, 60, 72, 25}, 0, 1, FX(0, 0, 0, 6), XP(P_GLIDE + 1, 38, P_TRANS + 1, -24)},
    {"DX BASS", {0, 1, 1, 2, 42, 40, 6, 0}, {0, 64, 66, 24}, 0, 1, FX(0, 0, 0, 6), XP(P_TRANS + 1, -24)},
    {"STEPPA FM", {0, 1, 1, 1, 36, 36, 14, 0}, {0, 62, 110, 26}, 0, 1, FX(10, 0, 0, 6), XP(P_GLIDE + 1, 30, P_TRANS + 1, -24)},
    {"JUNGLE FM", {0, 1, 2, 7, 58, 50, 20, 0}, {0, 66, 64, 24}, 0, 1, FX(8, 0, 10, 8), XP(P_GLIDE + 1, 26, P_TRANS + 1, -12)},
    {"RAGGA BELL", {4, 4, 3, 9, 48, 76, 0, 0}, {0, 90, 0, 76}, 0, 0, FX(0, 10, 30, 44)},
    {"GONG FM", {4, 4, 3, 6, 80, 90, 4, 0}, {30, 90, 110, 90}, 0, 0, FX(0, 20, 26, 60), XP(P_TRANS + 1, -12)},
    /* mallets: marimba, kalimba, the FM pluck */
    {"MARIMBAS", {4, 4, 1, 1, 60, 30, 0, 0}, {0, 80, 0, 60}, 0, 0, FX(0, 0, 22, 30)},
    {"KALIMBAS", {4, 4, 1, 6, 52, 26, 0, 0}, {0, 78, 0, 58}, 0, 0, FX(0, 0, 26, 38)},
    {"FM PLUCK", {4, 2, 1, 3, 70, 16, 0, 0}, {0, 78, 0, 54}, 0, 0, FX(0, 10, 28, 30)},
    /* horn stabs: ska (bright, high), dub (dark, low), the rave one, the steel pan, the DnB stab */
    {"SKA BRASS", {4, 6, 1, 10, 58, 50, 0, 0}, {4, 70, 92, 36}, 0, 0, FX(0, 15, 16, 24)},
    {"DUB BRASS", {4, 6, 1, 9, 44, 58, 0, 0}, {10, 70, 92, 40}, 0, 0, FX(6, 15, 18, 26), XP(P_TRANS + 1, -12)},
    {"RAVE STAB", {4, 8, 1, 4, 86, 64, 0, 0}, {0, 64, 28, 34}, 40, 0, FX(18, 20, 26, 30), XP(P_TRANS + 1, -12)},
    {"STEEL PAN", {4, 2, 2, 2, 46, 44, 0, 0}, {0, 88, 0, 66}, 0, 0, FX(0, 12, 18, 30)},
    {"DNB STAB", {4, 6, 2, 4, 78, 42, 6, 0}, {0, 62, 30, 30}, 30, 0, FX(10, 12, 20, 24)},
    /* a vox-ish pad to sit behind the chords */
    {"VOX FM", {4, 2, 1, 5, 34, 96, 0, 0}, {62, 92, 112, 92}, 0, 0, FX(0, 50, 26, 62), XP(P_LD_PIT + 1, 1, P_LRATE + 1, 40)},
};

/* (after Clipper 1.2) UNISON (voice.c unison_spread): the four operators moved together by r (Q32) of a turn of
 * the note, each by its ratio's share (phases 0 at each note: every voice in phase) */
static void digital_spread(track_t *t, voice_t *v, uint32_t r)
{
    const int16_t *p = t->p;
    v->ph[0] += r;
    v->ph[1] += (uint32_t)(((uint64_t)r * RATIO_Q8[p[P_E1] % 15]) >> 8);
    v->ph[2] += (uint32_t)(((uint64_t)r * RATIO_Q8[p[P_E2] % 15]) >> 8);
    v->s[7] = (int32_t)((uint32_t)v->s[7] + (uint32_t)(((uint64_t)r * RATIO_Q8[p[P_E3] % 15]) >> 8));
}

static const engine_t ENG_DIGITAL = {
    "DIGITAL", {"OPS", "MOD"},
    {
        {"ALG", F_ENUM, 0, 7, 0, N_FMALG, 0},
        {"R2", F_ENUM, 0, 14, 1, N_RATIO, 0},
        {"R3", F_ENUM, 0, 14, 1, N_RATIO, 0},
        {"R4", F_ENUM, 0, 14, 1, N_RATIO, 0},
        {"IDX", F_PCT, 0, 127, 60, 0, 0},
        {"MDEC", F_TIME, 0, 127, 60, 0, 0},
        {"FB", F_PCT, 0, 127, 0, 0, 0},
        {"-", F_INT, 0, 0, 0, 0, 0},
    },
    DIGITAL_PRESETS, sizeof(DIGITAL_PRESETS) / sizeof(DIGITAL_PRESETS[0]), -1, digital_note_on, digital_render,
    0xFD20, {P_E4, P_E5, P_E6, P_REL},
};
