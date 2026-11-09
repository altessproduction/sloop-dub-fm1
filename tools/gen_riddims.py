#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Generates firmware/src/dub_riddim.h: ten 64-step reggae / dub riddims, four tracks
# each (BASS, SKANK, MEL, DRUM = DUB_TRK_* in dub.h), one step a sixteenth, four bars.
# Run from the repo root:  python3 tools/gen_riddims.py
# The table is committed: the firmware builds need no Python.

import os

STEPS = 64          # 4 bars x 16 sixteenths
REST = 255          # DUB_SEQ_REST

# track order = DUB_TRK_BASS, DUB_TRK_SKANK, DUB_TRK_MEL, DUB_TRK_DRUM
BASS, SKANK, MEL, DRUM = 0, 1, 2, 3

# GM notes the drum track uses (seq.c midi_drum_lane / drums.c LANE_OF_GM):
# 36 kick, 38 snare, 39 clap, 42 closed hat, 46 open hat
K, S, P, CH, OH = 36, 38, 39, 42, 46


def blank():
    return [[REST] * STEPS for _ in range(4)], [[0] * STEPS for _ in range(4)]


def put(notes, vels, track, step, note, vel):
    assert 0 <= step < STEPS, step
    assert note == REST or 0 <= note <= 127, note
    assert 0 <= vel <= 127, vel
    assert notes[track][step] == REST, f"step {step} of track {track} hit twice"
    notes[track][step] = note
    vels[track][step] = vel


def bar_roots(roots, bars=None):
    """the four bars' roots, repeated if fewer given"""
    return [roots[i % len(roots)] for i in (bars or range(4))]


# ---- the bass grooves. Every groove is {step: (degree, vel)} per bar, the degree
# resolved on the bar's root: 0 the root, +7 the fifth, +12 the octave, +3 the minor
# third, +10 the flat seventh. A rest ends the note (the glue legatos equal notes).
GROOVES = {
    "drop":     {0: (0, 116), 3: (0, 108), 6: (7, 112), 8: (0, 116), 11: (0, 104), 14: (12, 110)},
    "drop_b":   {0: (0, 116), 3: (0, 108), 6: (0, 112), 8: (7, 114), 11: (5, 104), 14: (0, 110)},
    "steppers": {0: (0, 118), 2: (0, 100), 4: (0, 112), 6: (7, 108), 8: (0, 118), 10: (0, 100), 12: (0, 112), 14: (7, 108)},
    "rockers":  {0: (0, 118), 4: (7, 108), 6: (0, 112), 8: (0, 116), 12: (7, 108), 14: (3, 100)},
    "dubwalk":  {0: (0, 120), 6: (0, 104), 8: (7, 116), 14: (0, 104)},
    "digital":  {0: (0, 118), 3: (12, 106), 6: (0, 112), 8: (0, 118), 11: (7, 106), 14: (12, 110)},
    "lovers":   {0: (0, 112), 4: (7, 100), 8: (0, 112), 12: (10, 104)},
    "meditate": {0: (0, 120), 8: (3, 104), 12: (0, 112)},
    "skankin":  {0: (0, 114), 2: (7, 100), 4: (0, 112), 6: (12, 104), 8: (0, 114), 10: (7, 100), 12: (0, 112), 14: (12, 104)},
    "dubcut":   {0: (0, 120), 7: (12, 100), 10: (0, 112), 14: (7, 104)},
    "zion":     {0: (0, 118), 4: (0, 108), 6: (7, 112), 8: (0, 116), 12: (12, 104), 14: (7, 110)},
}

# ---- the skanks: {step: vel}, the chord's root follows the bar (the glue builds the
# chord with the SKANK page's quality). The classic stabs the upbeats: 2, 6, 10, 14.
SKANKS = {
    "upbeats":  {2: 108, 6: 104, 10: 108, 14: 104},
    "upbeat2":  {2: 112, 5: 96, 6: 104, 10: 112, 13: 96, 14: 104},
    "two_four": {4: 112, 12: 112},
    "pushed":   {2: 110, 6: 106, 9: 96, 10: 108, 14: 106},
    "sparse":   {6: 108, 14: 104},
}

# ---- the melodies: per bar {step: (note, vel)}, A minor pentatonic and chord tones.
MELODIES = {
    "call":     [{4: (69, 96), 10: (72, 92)}, {2: (74, 100), 8: (72, 92), 12: (69, 88)},
                 {4: (67, 96), 10: (64, 92)}, {6: (67, 92), 12: (69, 96)}],
    "deep":     [{8: (57, 92)}, {6: (60, 96), 14: (57, 88)}, {8: (62, 96)}, {4: (64, 100), 12: (62, 92)}],
    "offbeat":  [{2: (72, 92), 6: (69, 88), 10: (72, 92), 14: (74, 96)}, {2: (72, 92), 6: (69, 88), 10: (67, 92)},
                 {2: (69, 92), 6: (72, 96), 10: (74, 96), 14: (76, 100)}, {2: (74, 96), 10: (72, 92)}],
    "sigh":     [{0: (76, 92), 6: (74, 88), 8: (72, 96)}, {4: (72, 92), 12: (69, 88)},
                 {0: (72, 92), 6: (69, 88), 8: (67, 96)}, {4: (67, 92), 12: (64, 88)}],
    "rest":     [{}, {8: (69, 84)}, {}, {6: (64, 88)}],
}

# ---- the drums: per bar {step: (gm, vel)}; a bar list of four repeats or varies.
def D(*hits):
    return {s: (gm, v) for s, gm, v in hits}


DRUMS = {
    "one_drop":  [D((8, K, 122), (8, S, 116))] + [D((0, CH, 72), (2, CH, 84), (4, CH, 72), (6, CH, 84), (8, K, 122), (8, S, 116), (10, CH, 72), (12, CH, 84), (14, OH, 96) if b % 2 else (14, CH, 72)) for b in (1, 2, 3)],
    "steppers":  [D((0, K, 120), (4, K, 112), (4, S, 100), (8, K, 120), (12, K, 112), (12, S, 100)) for _ in range(4)],
    "rockers":   [D((0, K, 122), (4, S, 104), (8, K, 118), (11, K, 96), (12, S, 104), (2, CH, 80), (6, CH, 88), (10, CH, 80), (14, CH, 88)) for _ in range(4)],
    "digital":   [D((0, K, 120), (6, K, 108), (8, K, 118), (4, S, 106), (12, S, 106), (2, CH, 84), (10, CH, 84), (14, CH, 90)) for _ in range(4)],
    "dubwalk":   [D((0, K, 124), (8, K, 118), (8, S, 110), (4, CH, 72), (12, CH, 76)) for _ in range(4)],
    "lovers":    [D((0, K, 116), (8, K, 112), (4, S, 84), (12, S, 84), (2, CH, 72), (6, CH, 80), (10, CH, 72), (14, OH, 88)) for _ in range(4)],
    "meditate":  [D((0, K, 124), (8, K, 116), (8, S, 108), (0, CH, 64), (4, CH, 64), (8, CH, 64), (12, CH, 64)) for _ in range(4)],
    "skankin":   [D((0, K, 120), (4, K, 112), (8, K, 120), (12, K, 112), (4, S, 100), (12, S, 100), (2, CH, 84), (6, OH, 96), (10, CH, 84), (14, OH, 96)) for _ in range(4)],
    "dubcut":    [D((0, K, 124), (8, K, 116), (8, S, 108), (2, CH, 68), (6, CH, 76), (10, CH, 68), (14, CH, 76)) for _ in range(3)] + [D((0, K, 124), (8, K, 116), (8, S, 108), (11, K, 100), (14, S, 88), (15, S, 72))],
    "zion":      [D((0, K, 124), (8, K, 118), (8, S, 112), (2, CH, 76), (6, CH, 84), (10, OH, 96) if b % 2 else (10, CH, 76), (14, CH, 84)) for b in range(4)],
}

# ---- the ten riddims. roots: the four bars' bass roots (MIDI). skank: the stabs.
# bass: the groove, bass_alt: the groove the 3rd and 4th bars swap to (a dub's B half).
RIDDIM_NAMES = ["ONE DROP", "STEPPERS", "ROCKERS", "DUBWALK", "DIGITAL",
                "LOVERS", "MEDITATE", "SKANKIN", "DUB CUT", "ZION"]

RIDDIM_DEFS = [
    #  name         roots                bass groove pair   skank      melody
    ("ONE DROP", [33, 33, 38, 40], ("drop", "drop_b"), "upbeats", "call"),
    ("STEPPERS", [45, 43, 45, 43], ("steppers", "steppers"), "upbeats", "offbeat"),
    ("ROCKERS", [38, 38, 33, 33], ("rockers", "drop_b"), "upbeat2", "deep"),
    ("DUBWALK", [33, 41, 43, 40], ("dubwalk", "dubwalk"), "sparse", "rest"),
    ("DIGITAL", [40, 38, 40, 38], ("digital", "digital"), "two_four", "offbeat"),
    ("LOVERS", [41, 43, 45, 45], ("lovers", "drop_b"), "upbeats", "sigh"),
    ("MEDITATE", [45, 43, 41, 40], ("meditate", "meditate"), "sparse", "deep"),
    ("SKANKIN", [48, 45, 41, 43], ("skankin", "skankin"), "upbeat2", "offbeat"),
    ("DUB CUT", [33, 33, 41, 41], ("dubcut", "dubcut"), "pushed", "rest"),
    ("ZION", [38, 33, 38, 40], ("zion", "drop_b"), "upbeats", "call"),
]


def build_riddim(defn):
    name, roots, (g_a, g_b), skank, mel = defn
    notes, vels = blank()
    bar_roots_ = bar_roots(roots)
    for b, root in enumerate(bar_roots_):
        groove = GROOVES[g_a if b < 2 else g_b]
        for st, (deg, vel) in groove.items():
            put(notes, vels, BASS, b * 16 + st, root + deg, vel)
        for st, vel in SKANKS[skank].items():
            put(notes, vels, SKANK, b * 16 + st, (root % 12) + 57, vel)   # the chord's root, one octave up
        for st, (note, vel) in MELODIES[mel][b].items():
            put(notes, vels, MEL, b * 16 + st, note, vel)
        for st, (gm, vel) in DRUMS[[_d for _d in DRUMS][0] if False else drum_key(defn[0])][b].items():
            put(notes, vels, DRUM, b * 16 + st, gm, vel)
    return notes, vels


# the drum pattern each riddim plays (its own name, lower case)
DRUM_MAP = {
    "ONE DROP": "one_drop", "STEPPERS": "steppers", "ROCKERS": "rockers",
    "DUBWALK": "dubwalk", "DIGITAL": "digital", "LOVERS": "lovers",
    "MEDITATE": "meditate", "SKANKIN": "skankin", "DUB CUT": "dubcut", "ZION": "zion",
}


def drum_key(name):
    return DRUM_MAP[name]


def emit():
    rows = []
    rows.append("/* SPDX-License-Identifier: GPL-3.0-only")
    rows.append(" * Generated by tools/gen_riddims.py -- do not edit by hand: change the generator")
    rows.append(" * and run it again. Ten 64-step reggae / dub riddims, four tracks each")
    rows.append(" * (DUB_TRK_BASS, DUB_TRK_SKANK, DUB_TRK_MEL, DUB_TRK_DRUM), one step a sixteenth:")
    rows.append(" * four bars, DUB_SEQ_REST (255) is a rest. The dub_riddim_t struct is in dub.h. */")
    rows.append("#ifndef SLOOP_DUB_RIDDIM_H")
    rows.append("#define SLOOP_DUB_RIDDIM_H")
    rows.append('#include "dub.h"')
    rows.append("")
    rows.append("const dub_riddim_t DUB_RIDDIMS[] = {")
    for defn in RIDDIM_DEFS:
        notes, vels = build_riddim(defn)
        rows.append(f'    {{"{defn[0]}", {{')          # "{ {" opens the note[DUB_TRK_N][64] group
        for tr in range(4):
            n = ", ".join(str(x) for x in notes[tr])
            rows.append(f"        {{{n}}},")
        rows.append("        },")
        rows.append("        {")                       # the vel group
        for tr in range(4):
            v = ", ".join(str(x) for x in vels[tr])
            rows.append(f"        {{{v}}},")
        rows.append("        },")
        rows.append("    },")                          # the element's close; the array closes after the last
    rows.append("};")
    rows.append("")
    rows.append("#endif")
    return "\n".join(rows) + "\n"


def preview():
    """an ASCII grid of the first riddim's four tracks, for the eye"""
    notes, vels = build_riddim(RIDDIM_DEFS[0])
    names = ["BASS", "SKNK", "MEL ", "DRUM"]
    print("ONE DROP, steps 0..31 (x = a hit, o = a rest, | = a beat, + = a bar):")
    for tr in range(4):
        line = names[tr] + " "
        for st in range(32):
            line += "x" if notes[tr][st] != REST else "o"
            if st % 4 == 3:
                line += "|"
            if st % 16 == 15:
                line += "+"
        print(line)
    notes, vels = build_riddim(RIDDIM_DEFS[3])
    print("DUBWALK:")
    for tr in range(4):
        line = names[tr] + " "
        for st in range(32):
            line += "x" if notes[tr][st] != REST else "o"
            if st % 4 == 3:
                line += "|"
            if st % 16 == 15:
                line += "+"
        print(line)


if __name__ == "__main__":
    preview()
    out = os.path.join(os.path.dirname(__file__), "..", "firmware", "src", "dub_riddim.h")
    with open(out, "w") as f:
        f.write(emit())
    print("written", os.path.normpath(out))
