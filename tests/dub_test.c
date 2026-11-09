/* SPDX-License-Identifier: GPL-3.0-only */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "../firmware/src/dub.h"
#include "../firmware/src/dub.c"

static int fails;
static void check(int ok, const char *name)
{
    printf("dub: %-48s %s\n", name, ok ? "ok" : "FAIL");
    if (!ok)
        fails++;
}

int main(void)
{
    dub_isolator_t iso;
    dub_siren_t siren;
    dub_seq_t seq;
    dub_skank_t skank = {0, 0, 4, 100};
    dub_band_param_t band = {180, 6, 64, 32, 6, 0};
    uint8_t notes[DUB_SKANK_MAX_NOTES];
    int32_t left[256], right[256];
    uint32_t i;
    int64_t energy = 0;

    dub_isolator_init(&iso);
    check(iso.xover[0] == 90 && iso.xover[1] == 420 && iso.xover[2] == 2600,
          "isolator crossover defaults");
    check(iso.mix == 127, "isolator wet mix defaults to full");
    dub_isolator_set_band(&iso, DUB_BASS, band);
    check(iso.p[DUB_BASS].gain_db == 6 && iso.p[DUB_BASS].eq_db == 6,
          "band gain and parametric values");
    memset(left, 0, sizeof left);
    memset(right, 0, sizeof right);
    for (i = 0; i < 256; i++)
        left[i] = right[i] = (int32_t)(i * 80);
    iso.enabled = 1;
    dub_isolator_process(&iso, left, right, 256);
    check(left[255] != 255 * 80, "isolator processes enabled audio");
    iso.mix = 0;
    for (i = 0; i < 256; i++)
        left[i] = right[i] = (int32_t)(i * 80);
    dub_isolator_process(&iso, left, right, 256);
    check(left[255] == 255 * 80, "mix 0 leaves the mix dry");
    iso.mix = 127;
    iso.p[DUB_BASS].mute = 1;
    check(iso.p[DUB_BASS].mute == 1, "per-band mute state");

    dub_siren_init(&siren);
    check(siren.freq_hz == 740 && siren.depth == 96 && siren.rate == 8,
          "siren defaults 740 Hz depth 96 rate 2 Hz");
    check(siren.type == DUB_SIR_WAIL && siren.wave == DUB_SIW_SQR && siren.sym == 64 && siren.send == 0,
          "siren defaults: WAIL, SQR, sym 64, no send (the NJD's voice)");
    check(dub_siren_rate_hz(0) == 1 && dub_siren_rate_hz(127) == 16 && dub_siren_rate_hz(8) == 2,
          "siren rate maps 0..127 to 1..16 Hz");
    dub_siren_set_freq(&siren, 740);
    check(siren.freq_hz == 740, "siren set_freq keeps the shown hz");
    dub_siren_set_freq(&siren, 100);
    check(siren.freq_hz == 220, "siren freq clamps low to 220 Hz");
    dub_siren_set_freq(&siren, 4000);
    check(siren.freq_hz == 1200, "siren freq clamps high to 1200 Hz");
    dub_siren_set_freq(&siren, 660);
    check(siren.freq_hz == 660, "siren freq takes the middle range");
    dub_siren_set_rate(&siren, 200);
    check(siren.rate == 127 && dub_siren_rate_hz(siren.rate) == 16, "siren rate clamps to 127");
    dub_siren_set_type(&siren, 200);
    check(siren.type == DUB_SIR_SPACE, "siren type clamps to the last curve");
    dub_siren_set_type(&siren, DUB_SIR_WAIL);
    dub_siren_set_wave(&siren, 200);
    check(siren.wave == DUB_SIW_SIN, "siren wave clamps to the last curve");
    dub_siren_set_wave(&siren, DUB_SIW_SQR);
    dub_siren_set_sym(&siren, 250);
    check(siren.sym == 127, "siren sym clamps to 127");
    dub_siren_set_sym(&siren, 64);
    dub_siren_set_send(&siren, 200);                   /* (the API takes a byte: 200 arrives, clamps to 127) */
    check(siren.send == 127, "siren send clamps to 127");
    {
        int32_t send_b[256];
        for (i = 0; i < 256; i++)
            send_b[i] = 0;
        memset(left, 0, sizeof left);
        memset(right, 0, sizeof right);
        dub_siren_trigger(&siren, 96);
        dub_siren_render(&siren, left, right, send_b, 256);
        for (i = 0; i < 256; i++)
            energy += llabs((long long)left[i]);
        check(energy > 0 && left[32] == right[32], "dub siren renders stereo signal");
        for (i = 0; i < 256; i++)
            if (left[i] <= -70000 || left[i] >= 70000)
                break;
        check(i == 256, "dub siren stays in range");
        check(send_b[200] != 0, "siren send 127 feeds the delay bus");
    }
    dub_siren_set_send(&siren, 0);
    {
        int32_t send_b[256];
        for (i = 0; i < 256; i++)
            send_b[i] = 0;
        dub_siren_render(&siren, left, right, send_b, 256);
        check(send_b[200] == 0, "siren send 0 keeps the delay bus dry");
    }
    memset(left, 0, sizeof left);
    memset(right, 0, sizeof right);
    dub_siren_trigger(&siren, 0);
    dub_siren_render(&siren, left, right, NULL, 256);
    check(left[128] == 0, "siren level 0 stays silent (the slew's tail over)");
    {   /* every LFO curve and oscillator curve renders, bounded and non-silent */
        uint32_t t, w;
        for (t = 0; t < DUB_SIR_TYPES; t++) {
            long long e = 0;
            dub_siren_set_type(&siren, (uint8_t)t);
            dub_siren_set_wave(&siren, DUB_SIW_SQR);
            dub_siren_trigger(&siren, 100);
            for (i = 0; i < 256; i++) {
                left[i] = right[i] = 0;
            }
            dub_siren_render(&siren, left, right, NULL, 256);
            for (i = 0; i < 256; i++) {
                e += llabs((long long)left[i]);
                if (left[i] <= -70000 || left[i] >= 70000)
                    break;
            }
            check(i == 256 && e > 0, DUB_SIR_TYPE_NAMES[t]);
        }
        for (w = 0; w < DUB_SIW_N; w++) {
            long long e = 0;
            dub_siren_set_type(&siren, DUB_SIR_HILO);
            dub_siren_set_wave(&siren, (uint8_t)w);
            dub_siren_trigger(&siren, 100);
            for (i = 0; i < 256; i++)
                left[i] = right[i] = 0;
            dub_siren_render(&siren, left, right, NULL, 256);
            for (i = 0; i < 256; i++) {
                e += llabs((long long)left[i]);
                if (left[i] <= -70000 || left[i] >= 70000)
                    break;
            }
            check(i == 256 && e > 0, DUB_SIW_NAMES[w]);
        }
        dub_siren_set_type(&siren, DUB_SIR_WAIL);
        dub_siren_set_wave(&siren, DUB_SIW_SQR);
    }

    dub_seq_init(&seq);
    dub_seq_set_length(&seq, 64);
    dub_seq_set_step(&seq, DUB_TRK_BASS, 63, 36, 100);
    for (i = 0; i < 63; i++)
        dub_seq_advance(&seq);
    check(seq.length == 64 && seq.step == 63 && seq.notes[DUB_TRK_BASS][63] == 36,
          "64-step sequence");
    dub_seq_set_length(&seq, 32);
    dub_seq_advance(&seq);
    check(seq.step == 0, "sequence wraps at selected length");
    dub_seq_set_length(&seq, 17);
    check(seq.length == 32, "rejects unsupported sequence length");
    {   /* 2.9.2: the four tracks, the rests, the riddim bank */
        uint32_t r, tr, st;
        check(seq.notes[DUB_TRK_SKANK][63] == DUB_SEQ_REST && seq.notes[DUB_TRK_MEL][0] == DUB_SEQ_REST,
              "dub_seq_init: every track starts at rest");
        seq.notes[DUB_TRK_MEL][7] = 60;                /* load_track touches only its track */
        dub_riddim_load_track(&seq, 0, DUB_TRK_BASS);
        check(seq.notes[DUB_TRK_MEL][7] == 60 && seq.length == 64,
              "riddim load_track: the other tracks keep their steps");
        check(seq.notes[DUB_TRK_BASS][0] == DUB_RIDDIMS[0].note[DUB_TRK_BASS][0] &&
              seq.velocity[DUB_TRK_BASS][0] == DUB_RIDDIMS[0].vel[DUB_TRK_BASS][0],
              "riddim load_track: the bass steps land in the sequence");
        dub_riddim_load(&seq, 1);
        for (tr = 0; tr < DUB_TRK_N; tr++)
            for (st = 0; st < 64; st++)
                if (seq.notes[tr][st] != DUB_RIDDIMS[1].note[tr][st] ||
                    seq.velocity[tr][st] != DUB_RIDDIMS[1].vel[tr][st])
                    break;
        check(tr == DUB_TRK_N && st == 64 && seq.length == 64 && seq.step == 0,
              "riddim load: the four tracks whole, 64 steps, the head at 0");
        for (r = 0; r < DUB_RIDDIM_COUNT; r++) {
            uint32_t hits = 0, bad = 0;
            const dub_riddim_t *d = &DUB_RIDDIMS[r];
            for (tr = 0; tr < DUB_TRK_N; tr++) {
                check(d->name && d->name[0], "riddim: its name");
                for (st = 0; st < DUB_RIDDIM_STEPS; st++) {
                    if (d->note[tr][st] != DUB_SEQ_REST && d->note[tr][st] > 127u)
                        bad++;
                    if (d->vel[tr][st] > 127u)
                        bad++;
                    if (d->note[tr][st] != DUB_SEQ_REST)
                        hits++;
                }
            }
            check(!bad, "riddim: every note and velocity in range");
            check(hits > 40, "riddim: it has music on its tracks");
        }
        check(DUB_RIDDIM_COUNT == 10 && !strcmp(dub_riddim_name(0), "ONE DROP") &&
              !strcmp(dub_riddim_name(9), "ZION") && strcmp(dub_riddim_name(0), dub_riddim_name(1)),
              "riddim bank: ten, named, different");
        dub_seq_set_step(&seq, 9, 0, 60, 100);         /* the bounds: a bad track, a bad note */
        check(seq.notes[0][0] == DUB_RIDDIMS[1].note[DUB_TRK_BASS][0], "seq_set_step: track >= DUB_TRK_N ignored");
        dub_seq_set_step(&seq, DUB_TRK_DRUM, 200, 60, 100);
        dub_seq_set_step(&seq, DUB_TRK_DRUM, 0, 200, 100);
        check(seq.notes[DUB_TRK_DRUM][0] == DUB_SEQ_REST, "seq_set_step: note > 127 becomes a rest");
    }
    {   /* 2.9.3: the dub sound banks: eight a role, named, distinct, the kits plausible */
        uint32_t i, j;
        check(DUB_BASS_N == 8 && DUB_SKANK_N == 8 && DUB_MEL_N == 8 && DUB_DK_N == 8,
              "sound banks: eight a role");
        for (i = 0; i < DUB_BASS_N; i++)
            check(DUB_BASS_SOUNDS[i].name && DUB_BASS_SOUNDS[i].name[0], "bass bank: a name per sound");
        for (i = 0; i < DUB_SKANK_N; i++)
            check(DUB_SKANK_SOUNDS[i].name && DUB_SKANK_SOUNDS[i].name[0], "skank bank: a name per sound");
        for (i = 0; i < DUB_MEL_N; i++)
            check(DUB_MEL_SOUNDS[i].name && DUB_MEL_SOUNDS[i].name[0], "melody bank: a name per sound");
        for (i = 0; i < DUB_BASS_N; i++)
            for (j = 0; j < i; j++)
                check(strcmp(DUB_BASS_SOUNDS[i].name, DUB_BASS_SOUNDS[j].name), "bass bank: names distinct");
        for (i = 0; i < DUB_DK_N; i++)
            check(DUB_DK_NAMES[i] && DUB_DK_NAMES[i][0] && DUB_DK_KITS[i] < 37u, "kit bank: named, a real kit index");
    }

    skank.quality = 0;                                       /* MAJ */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 3 &&
          notes[0] == 50 && notes[1] == 54 && notes[2] == 57,
          "one-key major skank chord");
    skank.quality = 1;                                       /* MIN */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 3 && notes[1] == 53,
          "minor skank chord");
    skank.quality = 2;                                       /* DIM */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 3 && notes[1] == 53 && notes[2] == 56,
          "diminished skank chord");
    skank.quality = 3;                                       /* AUG */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 3 && notes[2] == 58,
          "augmented skank chord");
    skank.quality = 4;                                       /* 7TH */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 4 && notes[3] == 60,
          "seventh skank chord, four notes");
    skank.quality = 5;                                       /* MIN7 */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 4 && notes[1] == 53 && notes[3] == 60,
          "minor seventh skank chord");
    skank.quality = 6;                                       /* 9TH */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 5 && notes[4] == 64,
          "ninth skank chord, five notes");
    check(dub_skank_build(&skank, 2, notes, 3) == 3, "ninth chord truncated by max_notes");
    skank.quality = 7;                                       /* PWR */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 2 && notes[1] == 57,
          "power skank chord, root and fifth");
    skank.quality = 8;                                       /* wraps round the eight qualities */
    check(dub_skank_build(&skank, 2, notes, DUB_SKANK_MAX_NOTES) == 3 && notes[1] == 54,
          "skank quality wraps to major");
    check(DUB_SKANK_QUALITIES == 8 && DUB_SKANK_NAMES[0] && strcmp(DUB_SKANK_NAMES[4], "7TH") == 0,
          "skank quality names for the UI");
    check(DUB_PRESET_COUNT >= 5 && strcmp(DUB_PRESETS[2].name, "DUB SIREN") == 0,
          "reggae/dub preset bank");
    return fails ? 1 : 0;
}
