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
    uint8_t notes[3];
    int32_t left[256], right[256];
    uint32_t i;
    int64_t energy = 0;

    dub_isolator_init(&iso);
    check(iso.xover[0] == 90 && iso.xover[1] == 420 && iso.xover[2] == 2600,
          "isolator crossover defaults");
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
    iso.p[DUB_BASS].mute = 1;
    check(iso.p[DUB_BASS].mute == 1, "per-band mute state");

    dub_siren_init(&siren);
    memset(left, 0, sizeof left);
    memset(right, 0, sizeof right);
    dub_siren_trigger(&siren, 96);
    dub_siren_render(&siren, left, right, 256);
    for (i = 0; i < 256; i++)
        energy += llabs((long long)left[i]);
    check(energy > 0 && left[32] == right[32], "dub siren renders stereo signal");

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

    check(dub_skank_build(&skank, 2, notes, 3) == 3 && notes[0] == 50 && notes[1] == 54,
          "one-key major skank chord");
    check(DUB_PRESET_COUNT >= 5 && strcmp(DUB_PRESETS[2].name, "DUB SIREN") == 0,
          "reggae/dub preset bank");
    return fails ? 1 : 0;
}
