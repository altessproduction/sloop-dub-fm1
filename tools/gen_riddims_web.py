#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Generates firmware/src/dub_riddim.h from the Riddim-collection database
# (tools/riddims_db.js, window.RIDDB -- the data behind
# https://altessproduction.github.io/Riddim-collection/riddims.html).
# All the page's riddims -- the 38 of the Riddim Real Book, the 36 of the
# « RIDDIM MIDI » pack and Sleng Teng -- seventy-five 64-step riddims (four bars
# of sixteen sixteenths, played in a loop), four tracks each. The tracks land as
# the machine's DUB_TRK_* order: BASS (track 1), SKANK (track 2), MEL -- the
# riddim's remaining instrument (track 3), DRUM (track 4).
#
# The bank is written COMPRESSED, one stream a track, because the app slot has
# no room for seventy-five raw grids (75 x 512 bytes of notes and velocities).
# A track stream:
#   byte 0     the source bars held, S (0 the empty track, 1..4 the distinct bars)
#   byte 1     only when 2 <= S <= 3: the source each of the four bars plays,
#              two bits a bar, bar f's index in bits 2f..2f+1 (S == 1 plays its
#              one bar everywhere, S == 4 is the identity)
#   then, a source bar at a time: a count N (0..16), then N events of
#              { byte: the step in the bar (0..15), byte: the code -- the note
#                0..127 or DUB_SEQ_CUT (253), byte: the velocity 0..127 }.
# Every step an event does not write is DUB_SEQ_REST, the rest that holds.
# dub.c's dub_riddim_dec() expands the streams into the dub sequence at load;
# tests/riddim_check.c (tools/verify_riddims.sh) replays the expansion and
# compares it step by step with these very grids -- the round trip is the proof.
#
# The grids themselves: the database's own grid, 16 sixteenths a bar, events
# [step, midi note, length in steps]. Bass: the database's bars, cycled over the
# four bars, holds over the unwritten steps, CUT (253) where the note ends
# early. Skank: the database's own skank / guitar / chords stabs when the
# riddim has them (their chord root -- the SKANK page builds the chord around
# it), else the classic offbeats 2, 6, 10, 14 on the riddim's chord string.
# Melody: the remaining accompaniment (organ, brass, second chords, melody),
# its lead note. Drums: the riddim's own drm when it has one, else its style's
# pattern; the bank holds one drum a step, so a hit that lands with a stronger
# one shifts a sixteenth aside (the kick rides in before the snare, the sound
# system's pickup) or steps out for the hats. Run from the repo root:
#   python3 tools/gen_riddims_web.py            # writes firmware/src/dub_riddim.h
#   python3 tools/gen_riddims_web.py --golden build/riddim_golden.h
#                                               # the raw grids, for the C check
# The table is committed: the firmware builds need no Python.

import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = 64          # 4 bars x 16 sixteenths
BAR = 16
REST = 255          # DUB_SEQ_REST: a rest that holds (the TIE)
CUT = 253           # DUB_SEQ_CUT: the rest that cuts the held note

BASS, SKANK, MEL, DRUM = 0, 1, 2, 3          # = DUB_TRK_BASS..DRUM, tracks 1-4
TRACK_TAG = ("B", "S", "M", "D")             # the stream array names' suffixes

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

# the bank: ALL the riddims of the Riddim-collection page, in the page's own
# order (the Real Book's 38 first, the pack's 36, Sleng Teng closes).
# (db id, the name the LCD shows -- 14 characters fit the row)
BANK = [
    ("african-beat",            "AFRICAN BEAT"),
    ("all-we-need",             "ALL WE NEED"),
    ("answer",                  "ANSWER"),
    ("artibella",               "ARTIBELLA"),
    ("baby-i-love-you",         "BABY I LOVE"),
    ("ballistic",               "BALLISTIC"),
    ("bam-bam",                 "BAM BAM"),
    ("beat-down-babylon",       "BEAT DOWN"),
    ("better-must-come",        "BETTER MUST"),
    ("billie-jean",             "BILLIE JEAN"),
    ("created-by-father",       "CREATED FATHER"),
    ("cuss-cuss",               "CUSS CUSS"),
    ("death-in-arena",          "DEATH IN ARENA"),
    ("dirty-harry",             "DIRTY HARRY"),
    ("drifter",                 "DRIFTER"),
    ("duck",                    "DUCK"),
    ("expo-train",              "EXPO TRAIN"),
    ("far-east",                "FAR EAST"),
    ("fattie-fattie",           "FATTIE FATTIE"),
    ("get-in-groove",           "GET IN GROOVE"),
    ("head-to-toe",             "HEAD TO TOE"),
    ("movie-star",              "MOVIE STAR"),
    ("my-conversation",         "CONVERSATION"),
    ("my-jamaican-girl",        "MY JAMAICAN"),
    ("pick-up-pieces",          "PICK UP PIECES"),
    ("pressure-slide",          "PRESSURE SLIDE"),
    ("pretty-looks",            "PRETTY LOOKS"),
    ("punaany",                 "PUNAANY"),
    ("queen-majesty",           "QUEEN MAJESTY"),
    ("real-rock",               "REAL ROCK"),
    ("stalag",                  "STALAG"),
    ("stars",                   "STARS"),
    ("swing-easy",              "SWING EASY"),
    ("take-a-ride",             "TAKE A RIDE"),
    ("tempo",                   "TEMPO"),
    ("world-a-music",           "WORLD A MUSIC"),
    ("you-dont-care",           "YOU DONT CARE"),
    ("youth-man",               "YOUTH MAN"),
    ("baba-boom",               "BABA BOOM"),
    ("chase-vampire",           "CHASE VAMPIRE"),
    ("cherry-oh-baby",          "CHERRY OH BABY"),
    ("darker-shade-of-black",   "DARKER SHADE"),
    ("drum-song",               "DRUM SONG"),
    ("dub-organizer",           "DUB ORGANIZER"),
    ("dubolitions",             "DUBOLITIONS"),
    ("ethiopian-kings",         "ETHIOPIAN KINGS"),
    ("every-tongue-shall-tell", "EVERY TONGUE"),
    ("fade-away",               "FADE AWAY"),
    ("fisherman",               "FISHERMAN"),
    ("freedom-blues",           "FREEDOM BLUES"),
    ("ghetto-people-song",      "GHETTO PEOPLE"),
    ("grab-your-lass-and-come", "GRAB YR LASS"),
    ("gunman",                  "GUNMAN"),
    ("heathen",                 "HEATHEN"),
    ("heavenless",              "HEAVENLESS"),
    ("jah-shakey",              "JAH SHAKEY"),
    ("java",                    "JAVA"),
    ("johnny-dollar",           "JOHNNY DOLLAR"),
    ("jump-up",                 "JUMP UP"),
    ("liberation",              "LIBERATION"),
    ("mr-bassie",               "MR BASSIE"),
    ("nanny-goat",              "NANNY GOAT"),
    ("peanie-peanie",           "PEANIE PEANIE"),
    ("revolution",              "REVOLUTION"),
    ("rockfort-rock",           "ROCKFORT ROCK"),
    ("rougher-yet",             "ROUGHER YET"),
    ("run-down-the-world",      "RUN DOWN WORLD"),
    ("satta",                   "SATTA MASSAGA"),
    ("shank-i-sheck",           "SHANK I SHECK"),
    ("skylarking",              "SKYLARKING"),
    ("the-whip",                "THE WHIP"),
    ("warning",                 "WARNING"),
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


def first_sounding(bars):
    """the arrangement's first bar that plays anything: the long ones (the
    pack's Fade Away, Freedom Blues) open on silent intro bars, and the 64-step
    loop must start where the groove sounds -- the bass's first bar sets the
    window every track follows"""
    for i, b in enumerate(bars):
        if b:
            return i
    return 0


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


def melodic_track(notes, vels, track, site_bars, off=0, lead=False):
    """the database's bars onto the four (the note the lead carries when a step
    stacks several, else the chord's lowest root); holds over the unwritten
    steps, CUT where the note ends early. The window starts at off -- the
    bass's first sounding bar (first_sounding) -- so a long arrangement's
    silent intros stay out of the loop. The bass leans on the page's own
    dynamics (112 the beat, 96 off it), the accompaniment plays 100."""
    for f in range(4):
        groups = events_of(site_bars[(off + f) % len(site_bars)])
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


def generated_skank(notes, vels, db_entry, off):
    """no accompaniment in the database: the classic offbeats 2, 6, 10, 14 on
    the chord string's roots (two chords over the one bar: half a bar each)"""
    pcs = chord_pcs(db_entry.get("ch", ""))
    nbars = len(db_entry["bars"])
    for f in range(4):
        if len(pcs) == 2 * nbars:                    # the chords walk inside the bar
            root = pcs[(2 * ((off + f) % nbars)) % len(pcs)]
            root2 = pcs[(2 * ((off + f) % nbars) + 1) % len(pcs)]
            half = {2: root, 6: root, 10: root2, 14: root2}
        elif pcs:
            root = pcs[(off + f) % len(pcs)]
            half = {2: root, 6: root, 10: root, 14: root}
        else:                                        # no chord string: the fifth above the bar's first bass note
            first = events_of(db_entry["bars"][(off + f) % nbars])
            s0 = min(first) if first else 0
            n0 = min(m for m, _ in first[s0]) if first else 36
            root = (n0 + 7) % 12
            half = {2: root, 6: root, 10: root, 14: root}
        for st, pc in half.items():
            put(notes, vels, SKANK, f * BAR + st, (pc % 12) + 60,
                108 if st % 8 == 2 else 104)


def skank_of_ex(notes, vels, ex_bars, off):
    """the database's stabs: their chord root (the SKANK page's quality builds
    the chord around it), one stab a step, the bass's window"""
    for f in range(4):
        groups = events_of(ex_bars[(off + f) % len(ex_bars)])
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
    off = first_sounding(db_entry["bars"])   # the loop window: the bass's first bar
    melodic_track(notes, vels, BASS, db_entry["bars"], off=off, lead=False)
    if skank_ex:
        skank_of_ex(notes, vels, skank_ex["bars"], off)
    else:
        generated_skank(notes, vels, db_entry, off)
    if mel_ex:
        melodic_track(notes, vels, MEL, mel_ex["bars"], off=off, lead=True)
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


# --- the compressed bank ---------------------------------------------------

def track_events(notes, vels, tr):
    """the 64-step grid back into per-bar event lists (a bar: [(step, code, vel)],
    the code a note or CUT -- REST steps are the holds, never written)"""
    bars = []
    for f in range(4):
        ev = []
        for s in range(BAR):
            st = f * BAR + s
            n = notes[tr][st]
            if n != REST:
                ev.append((s, n, vels[tr][st]))
        bars.append(tuple(ev))
    return bars


def compress_track(notes, vels, tr):
    """the track's stream: the source bars held, the map when 2..3, then a count
    and {step, code, vel} events a source bar"""
    bars = track_events(notes, vels, tr)
    if not any(bars):
        return [0]                              # the empty track
    srcs = []                                   # the distinct source bars, in order
    map4 = []
    for b in bars:
        if b in srcs:
            map4.append(srcs.index(b))
        else:
            srcs.append(b)
            map4.append(len(srcs) - 1)
    s = len(srcs)
    assert 1 <= s <= 4
    out = [s]
    if 2 <= s <= 3:
        out.append(sum(m << (2 * f) for f, m in enumerate(map4)))
    for bar in srcs:
        out.append(len(bar))
        for step, code, vel in bar:
            assert 0 <= step < BAR and 0 <= vel <= 127
            assert code == CUT or 0 <= code <= 127
            out += [step, code, vel]
    return out


def decompress_track(stream):
    """the loader's mirror in Python (dub.c dub_riddim_dec): the round trip's
    second half, so the generator proves its own encoding before writing it"""
    notes = [REST] * STEPS
    vels = [0] * STEPS
    p = 0
    s = stream[p]; p += 1
    if not s:
        return notes, vels
    m = None
    if 2 <= s <= 3:
        m = stream[p]; p += 1
    bars = []
    for _ in range(s):
        n = stream[p]
        bars.append(stream[p + 1:p + 1 + 3 * n])
        p += 1 + 3 * n
    assert p == len(stream), "trailing bytes in the stream"
    for f in range(4):
        src = f if s == 4 else (0 if s == 1 else (m >> (2 * f)) & 3)
        ev = bars[src]
        for i in range(0, len(ev), 3):
            step, code, vel = ev[i], ev[i + 1], ev[i + 2]
            notes[f * BAR + step] = code
            vels[f * BAR + step] = vel
    return notes, vels


def emit_stream(name, stream):
    """one C array, wrapped at twenty numbers a line"""
    rows = [f"static const uint8_t {name}[] = {{"]
    for i in range(0, len(stream), 20):
        rows.append("    " + ", ".join(str(x) for x in stream[i:i + 20]) + ",")
    rows.append("};")
    return rows


def emit():
    rows = []
    rows.append("/* SPDX-License-Identifier: GPL-3.0-only")
    rows.append(" * Generated by tools/gen_riddims_web.py from the Riddim-collection database")
    rows.append(" * (tools/riddims_db.js, the data of altessproduction.github.io/Riddim-collection)")
    rows.append(" * -- do not edit by hand: change the generator and run it again. All the")
    rows.append(" * page's riddims -- seventy-five 64-step loops, four tracks each")
    rows.append(" * (DUB_TRK_BASS, DUB_TRK_SKANK, DUB_TRK_MEL, DUB_TRK_DRUM -- the bass on")
    rows.append(" * track 1, the skank on track 2, the riddim's remaining instrument on track")
    rows.append(" * 3, the drums on track 4), one step a sixteenth, four bars played in a")
    rows.append(" * loop. The bank is compressed, one stream a track (the format is written")
    rows.append(" * out in the generator's head); dub.c's dub_riddim_dec() expands it into")
    rows.append(" * the dub sequence at load. DUB_SEQ_REST (255) is a rest that holds,")
    rows.append(" * DUB_SEQ_CUT (253) the rest that cuts. The dub_riddim_t struct is in")
    rows.append(" * dub.h; tests/riddim_check.c proves the expansion against these grids. */")
    rows.append("#ifndef SLOOP_DUB_RIDDIM_H")
    rows.append("#define SLOOP_DUB_RIDDIM_H")
    rows.append('#include "dub.h"')
    rows.append("")
    report = []
    structs = []
    total = 0
    for rid, name in BANK:
        e = BY_ID[rid]
        skank_ex, mel_ex = assign_ex(e.get("ex"))
        notes, vels = build_riddim(e, skank_ex, mel_ex)
        check(notes, vels, name)
        sym = "RD_" + rid.upper().replace("-", "_")
        streams = [compress_track(notes, vels, tr) for tr in range(4)]
        for tr in range(4):                     # the round trip: the encoding holds
            dn, dv = decompress_track(streams[tr])
            assert dn == notes[tr], f"{name}: track {tr}: notes round trip off"
            assert dv == vels[tr], f"{name}: track {tr}: vels round trip off"
        sz = sum(len(s) for s in streams)
        total += sz
        for tr in range(4):
            rows += emit_stream(f"{sym}_{TRACK_TAG[tr]}", streams[tr])
        structs.append(f'    {{"{name}", {{{sym}_B, {sym}_S, {sym}_M, {sym}_D}}}},')
        bpm = e["bpm"]
        bpm_s = f"{bpm[0]}" if bpm[0] == bpm[1] else f"{bpm[0]}-{bpm[1]}"
        sk = f"db {skank_ex['r']}" if skank_ex else "offbeats"
        mel = f"db {mel_ex['r']}" if mel_ex else "--"
        report.append(f"  {name:14s} {e['st']:10s} {bpm_s:7s} skank={sk:9s} mel={mel:10s} "
                      f"bass {sum(1 for n in notes[BASS] if n not in (REST, CUT)):2d} hits, "
                      f"drums {sum(1 for n in notes[DRUM] if n != REST):2d} hits, "
                      f"{sz:4d} B")
    rows.append("")
    rows.append("const dub_riddim_t DUB_RIDDIMS[] = {")
    rows += structs
    rows.append("};")
    rows.append("")
    rows.append("#endif")
    return "\n".join(rows) + "\n", report, total


def emit_golden():
    """the raw grids, tests/riddim_check.c's side of the proof: the streams the
    loader expands must come back exactly these"""
    rows = []
    rows.append("/* SPDX-License-Identifier: GPL-3.0-only")
    rows.append(" * Generated by tools/gen_riddims_web.py --golden (do not edit): the raw")
    rows.append(" * 64-step grids the compressed bank must expand to. tests/riddim_check.c")
    rows.append(" * loads every riddim through dub.c and memcmp()s the four tracks against")
    rows.append(" * these arrays. */")
    rows.append('#include "dub.h"')
    rows.append("")
    rows.append(f"#define GOLDEN_N {len(BANK)}u")
    for which, arr in (("NOTES", "notes"), ("VELS", "vels")):
        rows.append(f"const uint8_t GOLDEN_{which}[GOLDEN_N][DUB_TRK_N][DUB_RIDDIM_STEPS] = {{")
        for rid, name in BANK:
            e = BY_ID[rid]
            skank_ex, mel_ex = assign_ex(e.get("ex"))
            notes, vels = build_riddim(e, skank_ex, mel_ex)
            grid = {"notes": notes, "vels": vels}[arr]
            rows.append(f"    {{ /* {name} */")
            for tr in range(4):
                rows.append("    {" + ", ".join(str(x) for x in grid[tr]) + "},")
            rows.append("    },")
        rows.append("};")
        rows.append("")
    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    DB = load_db()
    BY_ID = {e["id"]: e for e in DB["list"]}
    missing = [rid for rid, _ in BANK if rid not in BY_ID]
    assert not missing, f"riddims missing from the database: {missing}"
    golden = None
    args = sys.argv[1:]
    if "--golden" in args:
        golden = args[args.index("--golden") + 1]
    out = os.path.join(HERE, "..", "firmware", "src", "dub_riddim.h")
    text, report, total = emit()
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"written {os.path.normpath(out)}: {len(BANK)} riddims, {total} bytes of streams")
    print("  (skank/db-mel sources; the melodic track holds over its rests, CUT ends it)")
    for line in report:
        print(line)
    if golden:
        with open(golden, "w", encoding="utf-8") as f:
            f.write(emit_golden())
        print(f"written {golden}: the raw grids for tests/riddim_check.c")
