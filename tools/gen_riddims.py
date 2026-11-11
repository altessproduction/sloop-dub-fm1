#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Generates firmware/src/dub_riddim.h: twenty-two 64-step sound-system riddims, four
# tracks each (BASS, SKANK, MEL, DRUM = DUB_TRK_* in dub.h), one step a sixteenth,
# four bars. Reggae / dub / roots first (ONE DROP .. ZION), then ska (SKA, TWO TONE,
# ROCKSTDY), dancehall (DANCEHALL, DEMBOW) and the UK bass music (UK STEPPA, DNB STEP,
# JUNGLE, RAGGA JGL, DUBSTEP, UK 2STEP, BASSLINE).
# Run from the repo root:  python3 tools/gen_riddims.py
# The table is committed: the firmware builds need no Python.

import os

STEPS = 64          # 4 bars x 16 sixteenths
REST = 255          # DUB_SEQ_REST

# track order = DUB_TRK_BASS, DUB_TRK_SKANK, DUB_TRK_MEL, DUB_TRK_DRUM
BASS, SKANK, MEL, DRUM = 0, 1, 2, 3

# GM notes the drum track uses (seq.c midi_drum_lane / drums.c LANE_OF_GM):
# 36 kick, 37 rim, 38 snare, 39 clap, 40 second snare, 42 closed hat, 46 open hat
K, R, S, P, S2, CH, OH = 36, 37, 38, 39, 40, 42, 46


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
    # the ska / rocksteady walks
    "walk":     {0: (0, 116), 4: (7, 104), 8: (0, 112), 12: (7, 104), 14: (0, 100)},
    "octave":   {0: (0, 118), 2: (12, 100), 4: (0, 112), 6: (12, 100), 8: (0, 118), 10: (12, 100), 12: (7, 108), 14: (12, 100)},
    "rockst":   {0: (0, 116), 3: (0, 104), 6: (7, 108), 8: (0, 114), 11: (10, 104), 14: (0, 106)},
    # the dancehall / ragga pockets
    "dembo":    {0: (0, 120), 7: (0, 100), 10: (0, 112), 14: (12, 104)},
    # the UK bass music subs
    "deepstep": {0: (0, 122), 4: (0, 106), 8: (0, 120), 12: (0, 106)},
    "roll":     {0: (0, 122), 8: (0, 104), 10: (7, 112), 14: (12, 102)},
    "roll_b":   {0: (0, 122), 6: (7, 104), 10: (10, 108), 12: (0, 110)},
    "junglesub":{0: (0, 122), 6: (0, 98), 10: (0, 112), 14: (3, 100)},
    "junglesub_b": {0: (0, 122), 7: (0, 100), 10: (12, 106), 14: (0, 104)},
    "wobble":   {0: (0, 120), 6: (0, 104), 10: (0, 112)},
    "wobble_b": {0: (0, 120), 6: (7, 106), 10: (10, 104), 14: (0, 102)},
    "garage":   {0: (0, 118), 3: (12, 100), 6: (0, 110), 10: (7, 106), 12: (0, 114), 14: (10, 100)},
    "off16":    {2: (0, 112), 6: (12, 104), 10: (0, 112), 14: (12, 104)},
    "off16_b":  {2: (0, 112), 7: (12, 104), 10: (0, 112), 15: (7, 100)},
}

# ---- the skanks: {step: vel}, the chord's root follows the bar (the glue builds the
# chord with the SKANK page's quality). The classic stabs the upbeats: 2, 6, 10, 14.
SKANKS = {
    "upbeats":  {2: 108, 6: 104, 10: 108, 14: 104},
    "upbeat2":  {2: 112, 5: 96, 6: 104, 10: 112, 13: 96, 14: 104},
    "two_four": {4: 112, 12: 112},
    "pushed":   {2: 110, 6: 106, 9: 96, 10: 108, 14: 106},
    "sparse":   {6: 108, 14: 104},
    # the sound system's stabs: the dancehall doubles the clap's 3+3+2, the 2-step
    # pushes, the dubstep keeps one mid-bar stab, the jungle hits the "e" sixteenths
    "toast":    {3: 106, 6: 98, 11: 106, 14: 98},
    "shuf":     {2: 106, 7: 98, 10: 106, 14: 98},
    "dark":     {8: 96},
    "staba":    {7: 102, 15: 96},
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
    # the new banks' voices: the jungle's high blips, the dubstep's low phrase,
    # the dancehall's horn calls
    "blip":     [{4: (69, 88)}, {8: (72, 92), 14: (76, 84)}, {4: (64, 88), 12: (69, 86)}, {8: (67, 90)}],
    "dark":     [{0: (57, 92), 10: (60, 86)}, {8: (55, 90)}, {0: (60, 92), 10: (62, 86)}, {8: (57, 90)}],
    "brass":    [{0: (64, 100), 6: (67, 96)}, {4: (72, 100), 12: (67, 92)},
                 {0: (65, 100), 6: (69, 96)}, {4: (74, 100), 12: (69, 92)}],
}

# ---- the drums: per bar {step: (gm, vel)}; a bar list of four repeats or varies.
def D(*hits):
    return {s: (gm, v) for s, gm, v in hits}


DRUMS = {
    # the reggae / dub drums, fixed to their intended grooves: a track holds one lane
    # per step, so the one drop's kick rides a sixteenth before its snare (the roots'
    # pickup into the drop) and a four-on-the-floor steppers carries no layered snare
    "one_drop":  [D((8, S, 116))] + [D((0, CH, 72), (2, CH, 84), (4, CH, 72), (6, CH, 84), (7, K, 112), (8, S, 116), (10, CH, 72), (12, CH, 84), (14, OH, 96) if b % 2 else (14, CH, 72)) for b in (1, 2, 3)],
    "steppers":  [D((0, K, 122), (2, CH, 84), (4, K, 114), (6, CH, 84), (8, K, 122), (10, CH, 84), (12, K, 114), (14, CH, 84)) for _ in range(3)]
               + [D((0, K, 122), (2, CH, 84), (4, K, 114), (6, CH, 84), (8, K, 122), (10, CH, 84), (12, K, 114), (14, S, 88), (15, S, 72))],
    "rockers":   [D((0, K, 122), (4, S, 104), (8, K, 118), (11, K, 96), (12, S, 104), (2, CH, 80), (6, CH, 88), (10, CH, 80), (14, CH, 88)) for _ in range(4)],
    "digital":   [D((0, K, 120), (6, K, 108), (8, K, 118), (4, S, 106), (12, S, 106), (2, CH, 84), (10, CH, 84), (14, CH, 90)) for _ in range(4)],
    "dubwalk":   [D((0, K, 124), (8, K, 118), (4, CH, 72), (12, CH, 76)) for _ in range(4)],
    "lovers":    [D((0, K, 116), (8, K, 112), (4, S, 84), (12, S, 84), (2, CH, 72), (6, CH, 80), (10, CH, 72), (14, OH, 88)) for _ in range(4)],
    "meditate":  [D((0, K, 124), (8, S, 108), (4, CH, 64), (12, CH, 64)) for _ in range(4)],
    "skankin":   [D((0, K, 120), (4, S, 100), (8, K, 116), (12, S, 100), (2, CH, 84), (6, OH, 96), (10, CH, 84), (14, OH, 96)) for _ in range(4)],
    "dubcut":    [D((0, K, 124), (8, S, 108), (2, CH, 68), (6, CH, 76), (10, CH, 68), (14, CH, 76)) for _ in range(3)] + [D((0, K, 124), (8, S, 108), (11, K, 100), (14, S, 88), (15, S, 72))],
    "zion":      [D((0, K, 124), (8, S, 112), (2, CH, 76), (6, CH, 84), (10, OH, 96) if b % 2 else (10, CH, 76), (14, CH, 84)) for b in range(4)],
    # ---- the sound system's drums. One note per step (a track holds one lane), so a
    # kick and a hat never share a step: the hats live on the offbeats, the ghost
    # snares at low velocity between the backbeats.
    "ska":       [D((0, K, 112), (4, R, 112), (8, K, 106), (12, R, 112), (2, CH, 90), (6, CH, 90), (10, CH, 90), (14, CH, 90)) for _ in range(4)],
    "two_tone":  [D((0, K, 118), (4, S, 110), (8, K, 112), (12, S, 110), (2, CH, 84), (6, CH, 84), (10, CH, 84), (14, OH, 96)) for _ in range(3)]
               + [D((0, K, 118), (4, S, 110), (8, K, 112), (12, S, 104), (15, S, 76), (2, CH, 84), (6, CH, 84), (10, CH, 84), (14, OH, 96))],
    "rockstdy":  [D((0, K, 120), (4, S, 102), (8, K, 112), (12, S, 102), (2, CH, 72), (6, CH, 80), (10, CH, 72), (14, CH, 80)) for _ in range(4)],
    "dancehall": [D((0, K, 122), (8, K, 112), (10, K, 104), (3, P, 108), (6, P, 100), (11, P, 108), (14, P, 96), (2, CH, 76), (7, CH, 80)) for _ in range(3)]
               + [D((0, K, 122), (8, K, 112), (10, K, 104), (3, P, 108), (6, P, 100), (11, P, 108), (14, P, 96), (12, P, 88), (15, P, 72))],
    "dembow":    [D((0, K, 122), (8, K, 116), (3, S, 108), (6, S, 100), (11, S, 108), (14, S, 96), (2, CH, 80), (10, CH, 80)) for _ in range(4)],
    "uksteppa":  [D((0, K, 124), (4, K, 116), (8, K, 124), (12, K, 116), (2, R, 72), (6, R, 76), (10, R, 72), (14, R, 76)) for _ in range(3)]
               + [D((0, K, 124), (4, K, 116), (8, K, 124), (12, K, 116), (14, S, 84), (15, S, 68), (2, R, 72), (6, R, 76), (10, R, 72))],
    "dnb":       [D((0, K, 124), (4, S, 116), (7, S, 52), (10, K, 118), (12, S, 112), (15, S, 46), (2, CH, 76), (6, CH, 72), (8, CH, 76), (14, CH, 72)) for _ in range(3)]
               + [D((0, K, 124), (4, S, 116), (7, S, 56), (10, K, 118), (12, S, 112), (13, S, 48), (15, S, 40), (2, CH, 76), (6, CH, 72), (8, CH, 76), (14, CH, 72))],
    "jungle":    [D((0, K, 124), (4, S, 118), (6, S, 60), (10, K, 118), (12, S, 114), (15, S, 50), (2, CH, 70), (8, CH, 74)) for _ in range(2)]
               + [D((0, K, 124), (4, S, 118), (6, S, 64), (7, S, 48), (10, K, 118), (12, S, 114), (13, S, 56), (15, S, 44), (2, CH, 70), (8, CH, 74)) for _ in range(2)],
    "ragjgl":    [D((0, K, 124), (4, P, 112), (7, S, 56), (10, K, 118), (12, P, 110), (15, S, 46), (2, CH, 72), (8, CH, 74)) for _ in range(2)]
               + [D((0, K, 124), (4, P, 112), (6, S, 60), (7, S, 48), (10, K, 118), (12, P, 110), (13, S, 52), (15, S, 42), (2, CH, 72), (8, CH, 74)) for _ in range(2)],
    "dubstep":   [D((0, K, 124), (8, S, 118), (6, CH, 86), (10, CH, 86), (14, OH, 96)) for _ in range(2)]
               + [D((0, K, 124), (6, K, 100), (8, S, 118), (10, CH, 86), (14, OH, 96)),
                  D((0, K, 124), (8, S, 118), (15, S, 48), (6, CH, 86), (10, CH, 86), (14, OH, 96))],
    "uk2step":   [D((0, K, 118), (10, K, 112), (4, P, 108), (12, P, 108), (2, CH, 82), (3, CH, 68), (6, CH, 78), (7, CH, 66), (11, CH, 68), (14, CH, 78), (15, CH, 66)) for _ in range(4)],
    "bassline":  [D((0, K, 122), (4, K, 116), (8, K, 122), (12, K, 116), (6, P, 104), (14, P, 100), (2, CH, 84), (10, CH, 84)) for _ in range(4)],
}

# ---- the twenty-two riddims. roots: the four bars' bass roots (MIDI). skank: the stabs.
# bass: the groove, bass_alt: the groove the 3rd and 4th bars swap to (a dub's B half).
# Genre order: reggae / dub / roots, ska, dancehall, the UK bass music. BPMs for the
# docs: ONE DROP 72, STEPPERS 76, ROCKERS 80, DUBWALK 70, DIGITAL 92, LOVERS 84,
# MEDITATE 66, SKANKIN 88, DUB CUT 74, ZION 68, SKA 88, TWO TONE 92, ROCKSTDY 76,
# DANCEHALL 95, DEMBOW 100, UK STEPPA 84, DNB STEP 174, JUNGLE 172, RAGGA JGL 170,
# DUBSTEP 140, UK 2STEP 134, BASSLINE 132.
RIDDIM_NAMES = ["ONE DROP", "STEPPERS", "ROCKERS", "DUBWALK", "DIGITAL",
                "LOVERS", "MEDITATE", "SKANKIN", "DUB CUT", "ZION",
                "SKA", "TWO TONE", "ROCKSTDY", "DANCEHALL", "DEMBOW",
                "UK STEPPA", "DNB STEP", "JUNGLE", "RAGGA JGL", "DUBSTEP",
                "UK 2STEP", "BASSLINE"]

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
    # ---- ska: the walking bass, the octave pump, the rocksteady's bounce
    ("SKA", [45, 45, 41, 43], ("walk", "walk"), "upbeats", "offbeat"),
    ("TWO TONE", [45, 41, 43, 43], ("octave", "octave"), "upbeats", "offbeat"),
    ("ROCKSTDY", [33, 38, 41, 43], ("rockst", "drop_b"), "upbeats", "sigh"),
    # ---- dancehall / ragga: the 3+3+2 clap, the dembow's boom-ch-boom-chick
    ("DANCEHALL", [33, 38, 33, 43], ("dembo", "dembo"), "pushed", "brass"),
    ("DEMBOW", [33, 33, 40, 40], ("meditate", "dembo"), "toast", "rest"),
    # ---- the UK bass music: the steppers' drone, the DnB / jungle subs, the
    # dubstep's half-time, the 2-step's syncopation, the bassline's offbeats
    ("UK STEPPA", [33, 33, 40, 40], ("deepstep", "deepstep"), "sparse", "deep"),
    ("DNB STEP", [33, 36, 33, 31], ("roll", "roll_b"), "sparse", "blip"),
    ("JUNGLE", [33, 33, 36, 31], ("junglesub", "junglesub_b"), "staba", "blip"),
    ("RAGGA JGL", [33, 33, 38, 38], ("dembo", "dembo"), "toast", "brass"),
    ("DUBSTEP", [33, 33, 31, 31], ("wobble", "wobble_b"), "dark", "dark"),
    ("UK 2STEP", [33, 38, 43, 45], ("garage", "garage"), "shuf", "sigh"),
    ("BASSLINE", [40, 40, 43, 45], ("off16", "off16_b"), "two_four", "offbeat"),
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
        for st, (gm, vel) in DRUMS[drum_key(defn[0])][b].items():
            put(notes, vels, DRUM, b * 16 + st, gm, vel)
    return notes, vels


# the drum pattern each riddim plays (its own name, lower case)
DRUM_MAP = {
    "ONE DROP": "one_drop", "STEPPERS": "steppers", "ROCKERS": "rockers",
    "DUBWALK": "dubwalk", "DIGITAL": "digital", "LOVERS": "lovers",
    "MEDITATE": "meditate", "SKANKIN": "skankin", "DUB CUT": "dubcut", "ZION": "zion",
    "SKA": "ska", "TWO TONE": "two_tone", "ROCKSTDY": "rockstdy",
    "DANCEHALL": "dancehall", "DEMBOW": "dembow", "UK STEPPA": "uksteppa",
    "DNB STEP": "dnb", "JUNGLE": "jungle", "RAGGA JGL": "ragjgl",
    "DUBSTEP": "dubstep", "UK 2STEP": "uk2step", "BASSLINE": "bassline",
}


def drum_key(name):
    return DRUM_MAP[name]


def check_bank():
    """every riddim: four bars, each track has music, roots in the dub bass' range;
    the drums lose no hit to a same-step overwrite"""
    for defn in RIDDIM_DEFS:
        name, roots, grooves, skank, mel = defn
        assert len(roots) == 4, f"{name}: the roots must be four"
        assert all(28 <= r <= 50 for r in roots), f"{name}: a root out of the bass' range"
        for g in grooves:
            assert g in GROOVES, f"{name}: no groove {g}"
        assert skank in SKANKS, f"{name}: no skank {skank}"
        assert mel in MELODIES and len(MELODIES[mel]) == 4, f"{name}: no melody {mel}"
        assert drum_key(name) in DRUMS, f"{name}: no drum pattern"
        assert len(DRUMS[drum_key(name)]) == 4, f"{name}: the drums must be four bars"
        notes, vels = build_riddim(defn)
        for tr in range(4):
            hits = sum(1 for n in notes[tr] if n != REST)
            assert hits > 0, f"{name}: track {tr} is empty"
            for st, n in enumerate(notes[tr]):
                assert n == REST or 0 <= n <= 127, f"{name}: track {tr} step {st}: note {n}"
                assert 0 <= vels[tr][st] <= 127, f"{name}: track {tr} step {st}: vel {vels[tr][st]}"
    assert len(set(d[0] for d in RIDDIM_DEFS)) == len(RIDDIM_DEFS), "a name twice"
    assert len(set(DRUM_MAP)) == len(RIDDIM_DEFS), "the drum map is not one to one"
    # every D() call in the source keeps all its hits: a same-step overwrite in the
    # dict comprehension would silently drop a drum
    import ast
    for node in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "D":
            steps = []
            for a in node.args:                        # a ternary bar picks one hit: count it once
                es = [a] if not isinstance(a, ast.IfExp) else [a.body, a.orelse]
                found = {ast.literal_eval(e.elts[0]) for e in es if isinstance(e, ast.Tuple)}
                assert len(found) == 1, f"drums line {node.lineno}: a ternary bar's branches differ"
                steps.append(found.pop())
            assert len(steps) == len(set(steps)), f"drums line {node.lineno}: step twice in {ast.unparse(node)[:80]}"


def emit():
    rows = []
    rows.append("/* SPDX-License-Identifier: GPL-3.0-only")
    rows.append(" * Generated by tools/gen_riddims.py -- do not edit by hand: change the generator")
    rows.append(" * and run it again. Twenty-two 64-step sound-system riddims (reggae, dub, roots,")
    rows.append(" * ska, dancehall, UK bass music), four tracks each")
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
    check_bank()
    preview()
    out = os.path.join(os.path.dirname(__file__), "..", "firmware", "src", "dub_riddim.h")
    with open(out, "w") as f:
        f.write(emit())
    print(f"written {os.path.normpath(out)}: {len(RIDDIM_DEFS)} riddims")
