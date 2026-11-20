/* SPDX-License-Identifier: GPL-3.0-only */
/* The riddim bank's proof (tools/verify_riddims.sh builds and runs it): the
 * compressed streams of dub_riddim.h, loaded through dub.c's own loader, must
 * come back exactly the raw grids the generator kept (build/riddim_golden.h,
 * from the same run) -- seventy-five riddims, four tracks, sixty-four steps,
 * notes and velocities. The one-track loads must write their lane only, and a
 * riddim index past the bank's end must wrap back to itself. */
#include <stdio.h>
#include <string.h>

#include "dub.h"
#include "dub_riddim.h"
#include "riddim_golden.h"
#include "../firmware/src/dub.c"       /* the loader under test, one translation unit */

#define FAILF(...) do { printf("FAIL: " __VA_ARGS__); return 1; } while (0)

int main(void)
{
    static dub_seq_t seq, t, w;
    uint32_t r, tr, o, st, i;
    if (DUB_RIDDIM_COUNT != GOLDEN_N)
        FAILF("the bank holds %u riddims, the golden %u\n",
              (unsigned)DUB_RIDDIM_COUNT, (unsigned)GOLDEN_N);
    for (r = 0; r < DUB_RIDDIM_COUNT; r++) {
        const char *name = dub_riddim_name(r);
        if (!name[0])
            FAILF("riddim %u: no name\n", (unsigned)r);
        for (i = 0; i < r; i++)                  /* the LCD rows stay distinct */
            if (!strcmp(name, dub_riddim_name(i)))
                FAILF("riddim %u: \"%s\" twice\n", (unsigned)r, name);
        memset(&seq, 0x5A, sizeof seq);          /* garbage: the load rewrites all */
        dub_riddim_load(&seq, r);
        if (seq.length != DUB_RIDDIM_STEPS || seq.step != 0)
            FAILF("%s: the load leaves length %u step %u\n",
                  name, seq.length, seq.step);
        if (memcmp(seq.notes, GOLDEN_NOTES[r], sizeof seq.notes) ||
            memcmp(seq.velocity, GOLDEN_VELS[r], sizeof seq.velocity))
            FAILF("%s: the expansion is not the grid\n", name);
        for (tr = 0; tr < DUB_TRK_N; tr++) {     /* the one-track loads */
            memset(&t, 0x5A, sizeof t);
            t.length = 32;                       /* a shorter seq keeps its length */
            t.step = 7;
            dub_riddim_load_track(&t, r, tr);
            if (memcmp(t.notes[tr], GOLDEN_NOTES[r][tr], DUB_RIDDIM_STEPS) ||
                memcmp(t.velocity[tr], GOLDEN_VELS[r][tr], DUB_RIDDIM_STEPS))
                FAILF("%s track %s: the motif load is not the grid\n",
                      name, DUB_TRK_NAMES[tr]);
            if (t.length != DUB_RIDDIM_STEPS)
                FAILF("%s track %s: the motif load leaves length %u\n",
                      name, DUB_TRK_NAMES[tr], t.length);
            for (o = 0; o < DUB_TRK_N; o++) {    /* no spilling into the other lanes */
                if (o == tr)
                    continue;
                for (st = 0; st < DUB_RIDDIM_STEPS; st++)
                    if (t.notes[o][st] != 0x5A || t.velocity[o][st] != 0x5A)
                        FAILF("%s track %s: the load spills into %s\n",
                              name, DUB_TRK_NAMES[tr], DUB_TRK_NAMES[o]);
            }
        }
        w = seq;                                 /* past the bank's end: it wraps */
        dub_riddim_load(&w, r + DUB_RIDDIM_COUNT * 3);
        if (memcmp(&w, &seq, sizeof seq))
            FAILF("%s: the wrap does not come back to itself\n", name);
    }
    printf("riddim_check: %u riddims x %u tracks x %u steps, notes and velocities: OK\n",
           (unsigned)DUB_RIDDIM_COUNT, (unsigned)DUB_TRK_N, (unsigned)DUB_RIDDIM_STEPS);
    return 0;
}
