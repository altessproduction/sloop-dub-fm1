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
    memset(left, 0, sizeof left);
    memset(right, 0, sizeof right);
    dub_siren_trigger(&siren, 96);
    dub_siren_render(&siren, left, right, 256);
    for (i = 0; i < 256; i++)
        energy += llabs((long long)left[i]);
    check(energy > 0 && left[32] == right[32], "dub siren renders stereo signal");
    memset(left, 0, sizeof left);
    memset(right, 0, sizeof right);
    dub_siren_trigger(&siren, 0);
    dub_siren_render(&siren, left, right, 256);
    check(left[128] == 0, "siren level 0 stays silent");

    dub_seq_init(&seq);
    dub_seq_set_length(&seq, 64);
    dub_seq_set_step(&seq, 63, 36, 100);
    for (i = 0; i < 63; i++)
        dub_seq_advance(&seq);
    check(seq.length == 64 && seq.step == 63 && seq.notes[63] == 36,
          "64-step sequence");
    dub_seq_set_length(&seq, 32);
    dub_seq_advance(&seq);
    check(seq.step == 0, "sequence wraps at selected length");
    dub_seq_set_length(&seq, 17);
    check(seq.length == 32, "rejects unsupported sequence length");

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
