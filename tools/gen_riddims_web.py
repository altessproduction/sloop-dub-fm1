#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Generates firmware/src/dub_riddim.h from the Riddim-collection database
# (tools/riddims_db.js, window.RIDDB -- the data behind
# https://altessproduction.github.io/Riddim-collection/riddims.html).
# Twenty-seven 64-step riddims, four tracks each, one step a sixteenth, four
# bars; the tracks land as the machine's DUB_TRK_* order: BASS (track 1),
# SKANK (track 2), MEL -- the riddim's remaining instrument (track 3), DRUM
# (track 4). The database's own grid: 16 sixteenths a bar, events [step, midi
# note, length in steps]. Bass: the database's bars, cycled over the four bars,
# holds over the unwritten steps, CUT (253) where the note ends early. Skank:
# the database's own skank / guitar / chords stabs when the riddim has them
# (their chord root -- the SKANK page builds the chord around it), else the
# classic offbeats 2, 6, 10, 14 on the riddim's chord string. Melody: the
# remaining accompaniment (organ, brass, second chords, melody), its lead note.
# Drums: the riddim's own drm when it has one, else its style's pattern; the
# bank holds one drum a step, so a hit that lands with a stronger one shifts a
# sixteenth aside (the kick rides in before the snare, the sound system's
# pickup) or steps out for the hats. Run from the repo root:
#   python3 tools/gen_riddims_web.py
# The table is committed: the firmware builds need no Python.

import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = 64          # 4 bars x 16 sixteenths
BAR = 16
REST = 255          # DUB_SEQ_REST: a rest that holds (the TIE)
CUT = 253           # DUB_SEQ_CUT: the rest that cuts the held note

BASS, SKANK, MEL, DRUM = 0, 1, 2, 3          # = DUB_TRK_BASS..DRUM, tracks 1-4

# GM notes the drum track's lanes (seq.c midi_drum_lane / drums.c LANE_OF_GM)
GM = {"k": 36, "s": 38, "hc": 42, "hcg": 42, "ho": 46, "rm": 37}
# who keeps a step when two hits land together (the bank is one drum a step)
PRIORITY = {"s": 5, "ho": 4, "rm": 3, "k": 2, "hc": 1, "hcg": 0}
# the hits' levels (drums.c vel_lvl: <56 ghost, <88 soft, <116 norm, else hard).
# The loader keeps only the level a drum plays at, so the accents ride it: the
# downbeat kick and snare land hard, the hats stay soft, the ghosts whisper.
VEL = {"k": (120, 106), "s": (116, 100), "ho": (92, 92),
       "rm": (104, 104), "hc": (84, 76), "hcg": (40, 40)}

# the accompaniment roles and the track each lands on (the riddim's skank on
# track 2, its remaining instrument on track 3)
SKANK_ROLES = ("skank", "guitar", "chords", "organ", "piano")
MEL_ROLES = ("melody", "sax", "brass")

# the bank: the riddims of the Riddim-collection page, in the user's order.
# (db id, the name the LCD shows -- 14 characters fit the row)
BANK = [
    ("african-beat",            "AFRICAN BEAT"),
    ("answer",                  "ANSWER"),
    ("artibella",               "ARTIBELLA"),
    ("bam-bam",                 "BAM BAM"),
    ("billie-jean",             "BILLIE JEAN"),
    ("created-by-father",       "CREATED FATHER"),
    ("queen-majesty",           "QUEEN MAJESTY"),
    ("real-rock",               "REAL ROCK"),
    ("swing-easy",              "SWING EASY"),
    ("baba-boom",               "BABA BOOM"),
    ("chase-vampire",           "CHASE VAMPIRE"),
    ("drum-song",               "DRUM SONG"),
    ("dub-organizer",           "DUB ORGANIZER"),
    ("dubolitions",             "DUBOLITIONS"),
    ("every-tongue-shall-tell", "EVERY TONGUE"),
    ("fisherman",               "FISHERMAN"),
    ("ghetto-people-song",      "GHETTO PEOPLE"),
    ("grab-your-lass-and-come", "GRAB YR LASS"),
    ("heathen",                 "HEATHEN"),
    ("java",                    "JAVA"),
    ("liberation",              "LIBERATION"),
    ("mr-bassie",               "MR BASSIE"),
    ("revolution",              "REVOLUTION"),
    ("the-whip",                "THE WHIP"),
    ("warriors-dont-cry",       "WARRIORS CRY"),
    ("when-i-fall-in-love",     "WHEN I FALL"),
    ("sleng-teng",              "SLENG TENG"),
]

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def load_db():
    src = open(os.path.join(HERE, "riddims_db.js"), encoding="utf-8").read()
    m = re.search(r"window\.RIDDB\s*=\s*(\{.*\})\s*;?\s*$", src, re.S)
    return json.loads(m.group(1))


def chord_pcs(ch):
    """the chord string's roots' pitch classes, e.g. 'Dm · Am · Dm' -> (2, 9, 2)"""
    out = []
    for part in re.split(r"\s*·\s*", ch or ""):
        part = part.strip()
        part = re.sub(r"\(.*?\)", "", part).strip()      # 'C (Bb)' keeps its C
        m = re.match(r"^([A-G])([#b]?)", part)
        if not m:
            continue
        pc = NOTE_PC[m.group(1)]
        if m.group(2) == "#":
            pc += 1
        elif m.group(2) == "b":
            pc -= 1
        out.append(pc % 12)
    return tuple(out)


def blank():
    return [[REST] * STEPS for _ in range(4)], [[0] * STEPS for _ in range(4)]


def put(notes, vels, track, step, note, vel):
    assert notes[track][step] == REST, f"step {step} of track {track} hit twice"
    assert note == REST or note == CUT or 0 <= note <= 127, note
    assert 0 <= vel <= 127, vel
    notes[track][step] = note
    vels[track][step] = vel


def events_of(bar):
    """a bar's [step, note, len] events, grouped by step (a stab's chord = a group)"""
    groups = {}
    for ev in bar:
        s, m, l = ev[0], ev[1], (ev[2] if len(ev) > 2 else 1)
        groups.setdefault(s, []).append((m, max(1, l)))
    return groups


def melodic_track(notes, vels, track, site_bars, lead=False):
    """the database's bars onto the four (the note the lead carries when a step
    stacks several, else the chord's lowest root); holds over the unwritten
    steps, CUT where the note ends early. The bass leans on the page's own
    dynamics (112 the beat, 96 off it), the accompaniment plays 100."""
    for f in range(4):
        groups = events_of(site_bars[f % len(site_bars)])
        starts = sorted(groups)
        for i, s in enumerate(starts):
            notes_at = [m for m, _ in groups[s]]
            note = max(notes_at) if lead else min(notes_at)
            length = min(l for _, l in groups[s])
            nxt = starts[i + 1] if i + 1 < len(starts) else BAR
            vel = 112 if s % 8 == 0 else 96
            put(notes, vels, track, f * BAR + s, note, vel)
            for h in range(s + 1, min(s + length, nxt)):        # the hold (TIE)
                put(notes, vels, track, f * BAR + h, REST, 0)
            end = s + length
            if end < nxt and end < BAR:                          # it ends early: cut
                put(notes, vels, track, f * BAR + end, CUT, 0)


def generated_skank(notes, vels, db_entry):
    """no accompaniment in the database: the classic offbeats 2, 6, 10, 14 on
    the chord string's roots (two chords over the one bar: half a bar each)"""
    pcs = chord_pcs(db_entry.get("ch", ""))
    nbars = len(db_entry["bars"])
    for f in range(4):
        if len(pcs) == 2 * nbars:                    # the chords walk inside the bar
            root = pcs[(2 * (f % nbars)) % len(pcs)]
            root2 = pcs[(2 * (f % nbars) + 1) % len(pcs)]
            half = {2: root, 6: root, 10: root2, 14: root2}
        elif pcs:
            root = pcs[f % len(pcs)]
            half = {2: root, 6: root, 10: root, 14: root}
        else:                                        # no chord string: the fifth above the bar's first bass note
            first = events_of(db_entry["bars"][f % nbars])
            s0 = min(first) if first else 0
            n0 = min(m for m, _ in first[s0]) if first else 36
            root = (n0 + 7) % 12
            half = {2: root, 6: root, 10: root, 14: root}
        for st, pc in half.items():
            put(notes, vels, SKANK, f * BAR + st, (pc % 12) + 60,
                108 if st % 8 == 2 else 104)


def skank_of_ex(notes, vels, ex_bars):
    """the database's stabs: their chord root (the SKANK page's quality builds
    the chord around it), one stab a step"""
    for f in range(4):
        groups = events_of(ex_bars[f % len(ex_bars)])
        for s, notes_at in groups.items():
            root = min(m for m, _ in notes_at)
            put(notes, vels, SKANK, f * BAR + s, root, 100)


def drum_bar_hits(db_entry, b):
    """the bar's hits before the one-lane resolve: {step: [(lane, ...)]}, the
    riddim's own drm when it has one, else its style's"""
    dr = db_entry.get("drm") or DB["drums"][db_entry["st"]]
    out = {}
    for lane in ("k", "s", "hc", "hcg", "ho", "rm"):
        bars = dr.get(lane) or []
        steps = bars[b % len(bars)] if bars else []
        for s in steps:
            out.setdefault(s, []).append(lane)
    return out


def resolve_drum_bar(hits):
    """one drum a step: the stronger hit keeps the step; a kick that lands with
    the snare or the rim rides in a sixteenth before (or after); the hats it
    displaces step out"""
    winners = {}                                # step -> the lane that keeps it
    k_moved = []                                # the steps whose kick rides in
    for s in sorted(hits):
        lanes = sorted(hits[s], key=lambda l: -PRIORITY[l])
        winners[s] = lanes[0]
        if "k" in lanes[1:]:
            k_moved.append(s)
    grid = dict(winners)
    taken = set(winners)
    for s in k_moved:                           # the kick finds a spot beside the beat
        for c in (s - 1, s + 1, s - 2, s + 2):
            if not (0 <= c < BAR) or c in taken:
                continue
            w = winners.get(c)
            if w in ("s", "k", "rm", "ho"):     # never on top of the backbeat
                continue
            grid[c] = "k"                       # a hat's step or an empty one: it takes the step
            taken.add(c)
            break
    return grid


def drums_track(notes, vels, db_entry):
    for f in range(4):
        grid = resolve_drum_bar(drum_bar_hits(db_entry, f))
        for s, lane in sorted(grid.items()):
            on_beat = s % 8 == 0
            vel = VEL[lane][0] if on_beat else VEL[lane][1]
            put(notes, vels, DRUM, f * BAR + s, GM[lane], vel)


def assign_ex(ex):
    """the database's accompaniment tracks onto the machine's: the skank's stabs
    to track 2, the riddim's remaining instrument to track 3"""
    ex = list(ex or [])
    slots, used = {}, set()
    for k in ex:                            # the skank: its stabs first, then any stab role
        if k.get("r", "") in ("skank", "guitar"):
            slots["skank"] = k
            used.add(id(k))
            break
    if "skank" not in slots:
        for k in ex:
            if k.get("r", "") in SKANK_ROLES:
                slots["skank"] = k
                used.add(id(k))
                break
    for k in ex:                            # the lead roles carry the melody track
        if id(k) not in used and k.get("r", "") in MEL_ROLES:
            slots["mel"] = k
            used.add(id(k))
            break
    if "mel" not in slots:                  # else the accompaniment the skank left
        for k in ex:
            if id(k) not in used:
                slots["mel"] = k
                used.add(id(k))
                break
    return slots.get("skank"), slots.get("mel")


def build_riddim(db_entry, skank_ex, mel_ex):
    notes, vels = blank()
    melodic_track(notes, vels, BASS, db_entry["bars"], lead=False)
    if skank_ex:
        skank_of_ex(notes, vels, skank_ex["bars"])
    else:
        generated_skank(notes, vels, db_entry)
    if mel_ex:
        melodic_track(notes, vels, MEL, mel_ex["bars"], lead=True)
    drums_track(notes, vels, db_entry)
    return notes, vels


def check(notes, vels, name):
    for tr, hi in ((BASS, 127), (SKANK, 127), (MEL, 127), (DRUM, 127)):
        hits = sum(1 for n in notes[tr] if n not in (REST, CUT))
        assert hits > 0 or tr == MEL, f"{name}: track {tr} is empty"
        for st, n in enumerate(notes[tr]):
            assert n == REST or n == CUT or 0 <= n <= 127, f"{name}: t{tr} s{st}: note {n}"
            assert 0 <= vels[tr][st] <= hi, f"{name}: t{tr} s{st}: vel {vels[tr][st]}"
    for tr in (BASS, MEL):                      # a CUT ends a held note, never a bare rest
        held = False
        for st in range(STEPS):
            n = notes[tr][st]
            if n == CUT:
                assert held, f"{name}: track {tr} step {st}: a cut with nothing held"
                held = False
            elif n != REST:
                held = True
    for st in range(STEPS):                     # one drum a step
        n = notes[DRUM][st]
        assert n in (REST, 36, 37, 38, 42, 46), f"{name}: drum step {st}: gm {n}"


def emit():
    rows = []
    rows.append("/* SPDX-License-Identifier: GPL-3.0-only")
    rows.append(" * Generated by tools/gen_riddims_web.py from the Riddim-collection database")
    rows.append(" * (tools/riddims_db.js, the data of altessproduction.github.io/Riddim-collection)")
    rows.append(" * -- do not edit by hand: change the generator and run it again. Twenty-seven")
    rows.append(" * 64-step riddims, four tracks each (DUB_TRK_BASS, DUB_TRK_SKANK, DUB_TRK_MEL,")
    rows.append(" * DUB_TRK_DRUM -- the bass on track 1, the skank on track 2, the riddim's")
    rows.append(" * remaining instrument on track 3, the drums on track 4), one step a sixteenth:")
    rows.append(" * four bars, DUB_SEQ_REST (255) is a rest that holds, DUB_SEQ_CUT (253) the rest")
    rows.append(" * that cuts. The dub_riddim_t struct is in dub.h. */")
    rows.append("#ifndef SLOOP_DUB_RIDDIM_H")
    rows.append("#define SLOOP_DUB_RIDDIM_H")
    rows.append('#include "dub.h"')
    rows.append("")
    rows.append("const dub_riddim_t DUB_RIDDIMS[] = {")
    report = []
    for rid, name in BANK:
        e = BY_ID[rid]
        skank_ex, mel_ex = assign_ex(e.get("ex"))
        notes, vels = build_riddim(e, skank_ex, mel_ex)
        check(notes, vels, name)
        rows.append(f'    {{"{name}", {{')
        for tr in range(4):
            rows.append("        {" + ", ".join(str(x) for x in notes[tr]) + "},")
        rows.append("        },")
        rows.append("        {")                       # the vel group opens
        for tr in range(4):
            rows.append("        {" + ", ".join(str(x) for x in vels[tr]) + "},")
        rows.append("        },")
        rows.append("    },")
        bpm = e["bpm"]
        bpm_s = f"{bpm[0]}" if bpm[0] == bpm[1] else f"{bpm[0]}-{bpm[1]}"
        sk = f"db {skank_ex['r']}" if skank_ex else "offbeats"
        mel = f"db {mel_ex['r']}" if mel_ex else "--"
        report.append(f"  {name:14s} {e['st']:10s} {bpm_s:7s} skank={sk:9s} mel={mel:10s} "
                      f"bass {sum(1 for n in notes[BASS] if n not in (REST, CUT)):2d} hits, "
                      f"drums {sum(1 for n in notes[DRUM] if n != REST):2d} hits")
    rows.append("};")
    rows.append("")
    rows.append("#endif")
    return "\n".join(rows) + "\n", report


if __name__ == "__main__":
    DB = load_db()
    BY_ID = {e["id"]: e for e in DB["list"]}
    missing = [rid for rid, _ in BANK if rid not in BY_ID]
    assert not missing, f"riddims missing from the database: {missing}"
    out = os.path.join(HERE, "..", "firmware", "src", "dub_riddim.h")
    text, report = emit()
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"written {os.path.normpath(out)}: {len(BANK)} riddims")
    print("  (skank/db-mel sources; the melodic track holds over its rests, CUT ends it)")
    for line in report:
        print(line)
