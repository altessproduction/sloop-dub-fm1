#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Generates firmware/src/dub_riddim.h: twenty-eight 64-step sound-system riddims, four
# tracks each (BASS, SKANK, MEL, DRUM = DUB_TRK_* in dub.h), one step a sixteenth,
# four bars. Reggae / dub / roots first (ONE DROP .. ZION, SKA), then the classic
# riddims every sound system grew up on, rebuilt by hand from the records' feel: the
# Studio One / rocksteady family (HEAVENLESS, TONIGHT, GET IN GROOVE, HOT MILK, ANSWER,
# PROMISED LAND), the band and digital dancehall of the early eighties (GUNMAN, HERE I
# COME, SLENG TENG, TEMPO, PEANY PEANY), then DANCEHALL, DEMBOW, the UK bass music
# (JUNGLE, DUBSTEP) and the Casio MT-40's other five auto-rhythms (POPS, SLOWRK, SWING,
# WALTZ, SAMBA; SLENG TENG above is the machine's famous Rock preset).
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
    "dubcut":   {0: (0, 120), 7: (12, 100), 10: (0, 112), 14: (7, 104)},
    "zion":     {0: (0, 118), 4: (0, 108), 6: (7, 112), 8: (0, 116), 12: (12, 104), 14: (7, 110)},
    # the ska / rocksteady walks
    "walk":     {0: (0, 116), 4: (7, 104), 8: (0, 112), 12: (7, 104), 14: (0, 100)},
    "octave":   {0: (0, 118), 2: (12, 100), 4: (0, 112), 6: (12, 100), 8: (0, 118), 10: (12, 100), 12: (7, 108), 14: (12, 100)},
    "rockst":   {0: (0, 116), 3: (0, 104), 6: (7, 108), 8: (0, 114), 11: (10, 104), 14: (0, 106)},
    # the dancehall / ragga pockets
    "dembo":    {0: (0, 120), 7: (0, 100), 10: (0, 112), 14: (12, 104)},
    # the UK bass music: the jungle's subs
    "junglesub":{0: (0, 122), 6: (0, 98), 10: (0, 112), 14: (3, 100)},
    "junglesub_b": {0: (0, 122), 7: (0, 100), 10: (12, 106), 14: (0, 104)},
    "wobble":   {0: (0, 120), 6: (0, 104), 10: (0, 112)},
    "wobble_b": {0: (0, 120), 6: (7, 106), 10: (10, 104), 14: (0, 102)},
    # the classic riddims' bass lines, rebuilt by hand from the records' feel: the
    # Roots Radics' heavy minor march (Gunman), the Studio One root-fifth walk
    # (Heavenless), the Peanie Peany / Fade Away digital bounce
    "gunman":   {0: (0, 122), 6: (0, 100), 8: (0, 118), 14: (10, 102)},
    "gunman_b": {0: (0, 122), 6: (3, 100), 8: (0, 118), 12: (10, 102), 14: (7, 100)},
    "hvn":      {0: (0, 116), 6: (7, 100), 8: (0, 112), 14: (0, 100)},
    "hvn_b":    {0: (0, 116), 6: (7, 100), 8: (0, 112), 12: (10, 100), 14: (7, 100)},
    "peany":    {0: (0, 118), 3: (0, 100), 6: (12, 104), 8: (0, 118), 11: (7, 100), 14: (0, 104)},
    "peany_b":  {0: (0, 118), 3: (12, 100), 6: (0, 110), 8: (0, 118), 11: (0, 100), 14: (10, 104)},
    # the MT-40's auto-bass patterns, rebuilt by hand (the machine plays one measure per chord:
    # major, minor or seventh, bass + drums only). The Rock one is the Sleng Teng: the bounce
    # Hiroko Okuda heard as reggae, the octave pop and the flat-seventh turnaround.
    "sleng":    {0: (0, 120), 3: (0, 102), 4: (0, 114), 6: (12, 102), 8: (0, 118), 11: (0, 100), 12: (0, 112), 14: (10, 104)},
    "sleng_b":  {0: (12, 104), 2: (10, 100), 4: (7, 106), 6: (0, 116), 8: (0, 118), 11: (0, 100), 12: (0, 112), 14: (7, 102)},
    "mtpops":   {0: (0, 116), 2: (0, 98), 4: (7, 108), 6: (0, 112), 8: (0, 116), 10: (0, 98), 12: (7, 108), 14: (12, 102)},
    "mtpops_b": {0: (0, 116), 4: (7, 106), 6: (0, 112), 8: (10, 108), 10: (7, 102), 12: (5, 100), 14: (0, 108)},
    "mtslow":   {0: (0, 116), 6: (7, 100), 8: (0, 112), 12: (10, 100), 14: (7, 96)},
    "mtslow_b": {0: (0, 116), 6: (0, 100), 8: (7, 108), 12: (12, 100), 14: (10, 96)},
    "mtwalk":   {0: (0, 114), 4: (7, 102), 8: (10, 108), 12: (7, 102), 14: (10, 98)},
    "mtwalk_b": {0: (0, 114), 4: (7, 102), 8: (12, 100), 12: (10, 102), 14: (7, 98)},
    "mtwaltz":  {0: (0, 118), 8: (7, 104), 12: (12, 100)},
    "mtwaltz_b": {0: (0, 118), 8: (7, 104), 12: (10, 98), 14: (12, 100)},
    "mtsamba":  {0: (0, 120), 3: (12, 98), 6: (0, 112), 10: (0, 116), 13: (10, 98)},
    "mtsamba_b": {0: (0, 120), 3: (0, 98), 6: (7, 108), 10: (0, 116), 13: (12, 98)},
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
    "dark":     {8: 96},
    "staba":    {7: 102, 15: 96},
    # the MT-40's player's chords: the machine gave none, the session played the offbeat
    # upstroke over the Rock preset; the waltz's oom-pah-pah lands on beats two and three
    "mtup":     {2: 100, 6: 96, 10: 100, 14: 96},
    "waltz":    {4: 106, 8: 106},
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
    "meditate":  [D((0, K, 124), (8, S, 108), (4, CH, 64), (12, CH, 64)) for _ in range(4)],
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
    "jungle":    [D((0, K, 124), (4, S, 118), (6, S, 60), (10, K, 118), (12, S, 114), (15, S, 50), (2, CH, 70), (8, CH, 74)) for _ in range(2)]
               + [D((0, K, 124), (4, S, 118), (6, S, 64), (7, S, 48), (10, K, 118), (12, S, 114), (13, S, 56), (15, S, 44), (2, CH, 70), (8, CH, 74)) for _ in range(2)],
    "dubstep":   [D((0, K, 124), (8, S, 118), (6, CH, 86), (10, CH, 86), (14, OH, 96)) for _ in range(2)]
               + [D((0, K, 124), (6, K, 100), (8, S, 118), (10, CH, 86), (14, OH, 96)),
                  D((0, K, 124), (8, S, 118), (15, S, 48), (6, CH, 86), (10, CH, 86), (14, OH, 96))],
    # ---- the classic riddims' drums, rebuilt by hand: Jackie Mittoo's mellow backbeat
    # (Hot Milk), Dennis Brown's one drop (Promised Land), the Roots Radics' deep rockers
    # (Gunman — the kick breathes, the fill arrives on the fourth bar)
    "milk_d":    [D((0, K, 116), (4, S, 96), (8, K, 110), (12, S, 96), (2, CH, 70), (6, CH, 78), (10, CH, 70), (14, OH, 90)) for _ in range(4)],
    "pland":     [D((0, K, 120), (8, S, 108), (2, CH, 74), (6, CH, 82), (10, CH, 74), (14, OH, 92)) for _ in range(3)]
               + [D((0, K, 120), (8, S, 108), (2, CH, 74), (6, CH, 82), (10, CH, 74), (14, S, 96), (15, S, 80))],
    "radics":    [D((0, K, 122), (8, S, 112), (2, CH, 72), (6, CH, 80), (10, CH, 72), (14, OH, 90)) for _ in range(3)]
               + [D((0, K, 122), (8, S, 112), (11, K, 96), (14, S, 96), (15, S, 80), (2, CH, 72), (6, CH, 80), (10, CH, 72))],
    # ---- the MT-40's rhythm unit, rebuilt: the Rock's straight beat with the thin digital
    # snare, the fills its FILL-IN switch dropped at the bar ends (a drum fill, or a snare
    # roll), the samba's agogo on the rim, the waltz's oom-pah-pah on a four-four grid
    "mt_rock":   [D((0, K, 118), (4, S, 108), (8, K, 112), (12, S, 108), (2, CH, 84), (6, CH, 84), (10, CH, 84), (14, CH, 84)) for _ in range(3)]
               + [D((0, K, 118), (4, S, 108), (8, K, 112), (12, S, 112), (14, S, 100), (15, S, 90), (2, CH, 84), (6, CH, 84), (10, CH, 84))],
    "mt_pops":   [D((0, K, 114), (4, S, 100), (6, K, 98), (12, S, 100), (2, CH, 80), (8, CH, 80), (10, CH, 80), (14, CH, 84)) for _ in range(2)]
               + [D((0, K, 114), (4, S, 100), (6, K, 98), (12, S, 100), (2, CH, 80), (8, CH, 80), (10, CH, 80), (14, OH, 92))]
               + [D((0, K, 114), (4, S, 104), (6, K, 98), (12, S, 108), (14, S, 96), (15, S, 84), (2, CH, 80), (8, CH, 80), (10, CH, 80))],
    "mt_slow":   [D((0, K, 120), (8, S, 102), (2, CH, 70), (6, CH, 76), (10, CH, 70), (14, CH, 76)) for _ in range(3)]
               + [D((0, K, 120), (6, K, 96), (8, S, 102), (12, S, 96), (14, S, 88), (2, CH, 70), (10, CH, 70))],
    "mt_swing":  [D((0, K, 110), (4, S, 92), (8, K, 106), (12, S, 92), (7, R, 56), (15, R, 56), (2, CH, 72), (6, CH, 72), (10, CH, 72), (14, CH, 72)) for _ in range(3)]
               + [D((0, K, 110), (4, S, 92), (8, K, 106), (12, S, 96), (14, S, 86), (15, S, 74), (7, R, 56), (2, CH, 72), (6, CH, 72), (10, CH, 72))],
    "mt_waltz":  [D((0, K, 114), (4, CH, 80), (8, CH, 80), (12, R, 70)) for _ in range(3)]
               + [D((0, K, 114), (4, CH, 80), (8, CH, 80), (12, S, 88), (15, S, 76))],
    "mt_samba":  [D((0, K, 118), (6, K, 100), (10, K, 112), (13, K, 96), (3, R, 72), (7, R, 66), (11, R, 72), (15, R, 66), (2, CH, 78), (8, CH, 78), (14, OH, 88)) for b in range(2)]
               + [D((0, K, 118), (6, K, 100), (10, K, 112), (13, K, 96), (3, R, 72), (7, R, 66), (11, R, 72), (15, R, 66), (2, CH, 78), (8, CH, 78), (14, CH, 78))]
               + [D((0, K, 118), (6, K, 100), (10, K, 112), (12, K, 104), (14, K, 100), (3, R, 72), (7, R, 66), (11, R, 72), (2, CH, 78), (8, CH, 78))],
}

# ---- the twenty-eight riddims. roots: the four bars' bass roots (MIDI). skank: the stabs.
# bass: the groove, bass_alt: the groove the 3rd and 4th bars swap to (a dub's B half).
# Genre order: reggae / dub / roots, ska, then the classics every sound system grew up
# on (the Studio One / rocksteady family, the early-eighties band and digital dancehall),
# dancehall, the UK bass music, the MT-40's other five.
# BPMs for the docs: ONE DROP 72, STEPPERS 76, ROCKERS 80, DUBWALK 70, MEDITATE 66,
# DUB CUT 74, ZION 68, SKA 88, HEAVENLESS 80, TONIGHT 84, GET IN GROOVE 88, HOT MILK 92,
# ANSWER 82, PROMISED LAND 78, GUNMAN 78, HERE I COME 95, SLENG TENG 82 (the tune's own
# tempo), TEMPO 88, PEANY PEANY 92, DANCEHALL 95, DEMBOW 100, JUNGLE 172, DUBSTEP 140,
# MT40 POPS 96, MT40 SLOWRK 66, MT40 SWING 84, MT40 WALTZ 90, MT40 SAMBA 100.
RIDDIM_NAMES = ["ONE DROP", "STEPPERS", "ROCKERS", "DUBWALK", "MEDITATE", "DUB CUT", "ZION",
                "SKA",
                "HEAVENLESS", "TONIGHT", "GET IN GROOVE", "HOT MILK", "ANSWER", "PROMISED LAND",
                "GUNMAN", "HERE I COME", "SLENG TENG", "TEMPO", "PEANY PEANY",
                "DANCEHALL", "DEMBOW",
                "JUNGLE", "DUBSTEP",
                "MT40 POPS", "MT40 SLOWRK", "MT40 SWING", "MT40 WALTZ", "MT40 SAMBA"]

RIDDIM_DEFS = [
    #  name         roots                bass groove pair   skank      melody
    ("ONE DROP", [33, 33, 38, 40], ("drop", "drop_b"), "upbeats", "call"),
    ("STEPPERS", [45, 43, 45, 43], ("steppers", "steppers"), "upbeats", "offbeat"),
    ("ROCKERS", [38, 38, 33, 33], ("rockers", "drop_b"), "upbeat2", "deep"),
    ("DUBWALK", [33, 41, 43, 40], ("dubwalk", "dubwalk"), "sparse", "rest"),
    ("MEDITATE", [45, 43, 41, 40], ("meditate", "meditate"), "sparse", "deep"),
    ("DUB CUT", [33, 33, 41, 41], ("dubcut", "dubcut"), "pushed", "rest"),
    ("ZION", [38, 33, 38, 40], ("zion", "drop_b"), "upbeats", "call"),
    # ---- ska
    ("SKA", [45, 45, 41, 43], ("walk", "walk"), "upbeats", "offbeat"),
    # ---- the classic riddims, rebuilt by hand from the records' feel. The Studio One /
    # rocksteady family: Vin Gordon's Heavenless (1968, Coxsone Dodd), Keith & Tex's
    # Tonight (1967, Derrick Harriott, the rolling bass), the Get in the Groove riddim
    # (1968, Studio One, aka Up Park Camp — John Holt's 1976 cut), Jackie Mittoo's Hot
    # Milk (1968, Studio One, the floating lead), the Answer's one-chord gallop (Slim
    # Smith & The Uniques, "I'll Never Let You Go", 1967) and Dennis Brown's Promised
    # Land (1981, with Aswad, cut on the UK side as "Love Fire").
    ("HEAVENLESS", [33, 41, 33, 43], ("hvn", "hvn_b"), "upbeats", "sigh"),
    ("TONIGHT", [40, 45, 43, 40], ("rockst", "drop_b"), "upbeats", "sigh"),
    ("GET IN GROOVE", [41, 45, 43, 41], ("walk", "walk"), "upbeats", "rest"),
    ("HOT MILK", [36, 41, 43, 36], ("lovers", "drop_b"), "upbeats", "call"),
    ("ANSWER", [33, 33, 33, 33], ("steppers", "steppers"), "upbeats", "rest"),
    ("PROMISED LAND", [41, 46, 36, 43], ("zion", "drop_b"), "upbeats", "call"),
    # ---- the band and digital dancehall of the early eighties: Michael Prophet's
    # Gunman (1980, Henry "Junjo" Lawes at Channel One, the Roots Radics' heavy march,
    # Scientist at the mix), Barrington Levy's Here I Come (1985, the bouncy octave
    # pump), the Sleng Teng (the MT-40's Rock preset — Wayne Smith, King Jammy's, 1985),
    # Anthony Red Rose's Tempo (1985, King Tubby's Firehouse) and the Peanie Peany /
    # Fade Away riddim (Bobby Digital, 1987; Little John voiced it first).
    ("GUNMAN", [36, 36, 32, 34], ("gunman", "gunman_b"), "sparse", "deep"),
    ("HERE I COME", [33, 36, 38, 40], ("octave", "octave"), "upbeats", "call"),
    ("SLENG TENG", [37, 35, 33, 35], ("sleng", "sleng_b"), "mtup", "rest"),
    ("TEMPO", [33, 36, 38, 33], ("digital", "digital"), "pushed", "rest"),
    ("PEANY PEANY", [33, 36, 33, 40], ("peany", "peany_b"), "mtup", "rest"),
    # ---- dancehall / ragga: the 3+3+2 clap, the dembow's boom-ch-boom-chick
    ("DANCEHALL", [33, 38, 33, 43], ("dembo", "dembo"), "pushed", "brass"),
    ("DEMBOW", [33, 33, 40, 40], ("meditate", "dembo"), "toast", "rest"),
    # ---- the UK bass music: the jungle's break, the dubstep's half-time
    ("JUNGLE", [33, 33, 36, 31], ("junglesub", "junglesub_b"), "staba", "blip"),
    ("DUBSTEP", [33, 33, 31, 31], ("wobble", "wobble_b"), "dark", "dark"),
    # ---- the Casio MT-40's other five auto-rhythms, rebuilt by hand (the Sleng Teng
    # above is the Rock one). The machine played one measure of bass and drums per chord
    # (major, minor, seventh) and nothing else: the skank is the player's offbeat, the
    # melody the toaster's.
    ("MT40 POPS", [40, 43, 45, 40], ("mtpops", "mtpops_b"), "upbeats", "rest"),
    ("MT40 SLOWRK", [33, 33, 40, 38], ("mtslow", "mtslow_b"), "sparse", "rest"),
    ("MT40 SWING", [45, 41, 43, 40], ("mtwalk", "mtwalk_b"), "two_four", "rest"),
    ("MT40 WALTZ", [45, 42, 38, 40], ("mtwaltz", "mtwaltz_b"), "waltz", "rest"),
    ("MT40 SAMBA", [45, 45, 43, 43], ("mtsamba", "mtsamba_b"), "toast", "rest"),
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


# the drum pattern each riddim plays (its own name, lower case; the classic riddims
# share the one-drop of the Studio One house band and the digital dancehall's beat)
DRUM_MAP = {
    "ONE DROP": "one_drop", "STEPPERS": "steppers", "ROCKERS": "rockers",
    "DUBWALK": "dubwalk", "MEDITATE": "meditate", "DUB CUT": "dubcut", "ZION": "zion",
    "SKA": "ska",
    "HEAVENLESS": "one_drop", "TONIGHT": "rockstdy", "GET IN GROOVE": "one_drop",
    "HOT MILK": "milk_d", "ANSWER": "one_drop", "PROMISED LAND": "pland",
    "GUNMAN": "radics", "HERE I COME": "two_tone",
    "SLENG TENG": "mt_rock", "TEMPO": "digital", "PEANY PEANY": "digital",
    "DANCEHALL": "dancehall", "DEMBOW": "dembow",
    "JUNGLE": "jungle", "DUBSTEP": "dubstep",
    "MT40 POPS": "mt_pops", "MT40 SLOWRK": "mt_slow", "MT40 SWING": "mt_swing",
    "MT40 WALTZ": "mt_waltz", "MT40 SAMBA": "mt_samba",
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
    rows.append(" * and run it again. Twenty-eight 64-step sound-system riddims (reggae, dub, roots,")
    rows.append(" * ska, the Studio One and early-digital classics, dancehall, UK bass music, the Casio")
    rows.append(" * MT-40), four tracks each")
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
