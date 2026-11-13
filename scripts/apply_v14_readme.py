#!/usr/bin/env python3
# Applies the v1.4 README updates: counts, status block, the MT40 bank table, the MT-40 section.
from pathlib import Path

R = Path(__file__).resolve().parent.parent / "README.md"
t = R.read_text()
miss = []


def sub(a, b, n=1):
    global t
    if a in t:
        t = t.replace(a, b, n)
    else:
        miss.append(a[:72])


MT40_SECTION = """## The Casio MT-40: the functions, the rhythms, the sounds

In 1981 Casio sold a cheap home keyboard, the **Casiotone MT-40**. Its engineer **Hiroko Okuda**
programmed six auto-rhythm presets — and her "Rock" pattern, with its bouncing bassline, left
Jamaica in 1984 as **the Sleng Teng riddim**: Wayne Smith's *Under Mi Sleng Teng* (King Jammy's,
1985) was built on it, and it spawned hundreds of tracks — the birth of digital dancehall. The
keyboard itself is a must of digital reggae, and 1.4 rebuilds it inside SLOOP Dub: its six
rhythms, its 22 tones and its drum voices, **reconstructed by hand** (no factory ROM data is
copied, in the spirit of this fork — the sleng is recognisable from the first measure).

### The MT-40's functions, as SLOOP Dub plays them

| The MT-40 (1981) | In SLOOP Dub 1.4 |
| --- | --- |
| **6 built-in auto-rhythms** — one measure of bass + drums per chord (major / minor / 7th) | The **six MT-40 riddims** (RDM page), four bars each, their bass follows the roots you set |
| **FILL-IN** switch — two interludes: a drum fill, a snare roll | The **fourth bar** of every MT-40 riddim carries its fill; live fills stay yours (the CHOP page, the pads) |
| **SYNCHRO START** — the rhythm starts with the first note | **PLAY from any page** (2.9.4), MIDI clock sync (INT / USB / TRS) |
| **Auto bass**, one finger — the chord's bass pattern plays itself | The riddim's **BASS track** (or load a bass pattern alone), the SKANK page's chord qualities MAJ / MIN / 7TH / MIN7 |
| **4-position tone memory** | The **favourites** (16 slots at the top of the PRESETS list) and the **MT40 kind** |
| **Vibrato / Sustain switches** | The engines' LFO vibrato and release — every MT-40 tone is a real patch you can edit |
| **Rhythm / Bass volume balance** | The dub mixer: track LEVELs, the isolator's four bands, the DUB filter and throws |
| **Tempo control + tempo lamp** | The transport BPM, the menu bar, the tap tempo |
| **Pitch control knob** (back panel, tuning) | The project's tune / transpose per track |

### The six rhythms (the RDM page, at the bank's end)

| MT-40 preset | riddim | BPM | What it plays |
| --- | --- | --- | --- |
| **Rock** | **SLENG TENG** | 82 | The famous one: the eighth-note pump, the octave pop, the flat-seventh turnaround — the C#m–B–A–B walk of *Under Mi Sleng Teng*. The machine gave bass and drums only: the skank stays the player's offbeat. |
| Pops | MT40 POPS | 96 | The eighth-note pop bounce, root–fifth, an open hat answering. |
| Slow Rock | MT40 SLOWRK | 66 | The lazy half-time, the long bass notes, the hats keeping the sixteenths warm. |
| Swing | MT40 SWING | 84 | The walking bass (root–fifth–sixth–octave), the rim on the upbeats. |
| Waltz | MT40 WALTZ | 90 | The oom-pah-pah laid on a 4/4 grid: bass on one, the stabs on two and three, the pickup. |
| Samba | MT40 SAMBA | 100 | The syncopated surdo, the agogo on the rim, the offbeat hats. |

Each one's fourth bar is the **fill-in** the machine's FILL-IN switch dropped at the bar ends —
a snare roll, or a tom fill. Load the whole riddim with OCT+ on RDM, or take its bass, skanks or
drums alone with KN2 / KN3 / KN4 + OCT+.

### The 22 tones (the PRESETS page, kind **MT40**)

The machine's own numbering, 1 to 22 — each one a real patch on the engine that suits it best
(FM = the DIGITAL 4-op engine, ANLG = ANALOG, WHEEL = the drawbar organ, PHYS = the string
model, CHIP = LOFI):

| | | | |
| --- | --- | --- | --- |
| 1 MT E.PIANO (FM) | 2 MT BANJO (PHYS) | 3 MT GUITAR (PHYS) | 4 MT HARPSI (FM) |
| 5 MT XYLO (FM) | 6 MT CELESTA (FM) | 7 MT GLOCK (FM) | 8 MT ORGAN (WHEEL) |
| 9 MT ACCORD (FM) | 10 MT PIPE (WHEEL) | 11 MT ORIENT (WHEEL) | 12 MT BRASS (ANLG) |
| 13 MT CELLO (PHYS) | 14 MT SFUZZ (FM) | 15 MT VIOLIN (PHYS) | 16 MT TRUMPET (FM) |
| 17 MT FUNNY (CHIP) | 18 MT ENSMBL (ANLG) | 19 MT CLARIN (FM) | 20 MT FLUTE (FM) |
| 21 MT RECORD (FM) | 22 MT FOLKFLT (FM) | | |

The fuzzy ones the dancehall producers abused — **Synth. Fuzz** and the joke **Funny Fuzz** —
live here too, with the nasal **Oriental Pipe**. Every tone is a full patch: the LEVEL knob and
the DUB sends come along, like any preset of the bank.

### The MT-40 kit

The drum track's kit list gains **MT-40** (the DUB page's PRS, 9 kits): the thin chip-noise
snare, the short boxy kick, the tiny hats and the short crash of the machine's rhythm unit, with
a touch of bit-crush for the 1981 DAC. Play it under `SLENG TENG` and the tune is already there.

"""

# ---- header, links, intro
sub('alt="SLOOP DUB 1.3 · FM-1"', 'alt="SLOOP DUB 1.4 · FM-1"')
sub('<a href="docs/firmware/sloop-dub-1.3.fwsc">the 1.3 package (.fwsc)</a>',
    '<a href="docs/firmware/sloop-dub-1.4.fwsc">the 1.4 package (.fwsc)</a>')
sub("""**twenty-two 64-step riddims** that load into the sequencer with their patterns, a four-band
**isolator** whose mutes really cut, a **tape delay** whose TIME knob bends the loop like a real
tape echo, per-track **throws** into the delay, and the **WIRES** visualizer — over the whole
SLOOP base: twelve synthesis engines, 158 sound-system presets, 37 drum kits, your own samples,
song mode, USB audio, MIDI in on the jack, MIDI clock and MIDI out. Reggae, roots, ska, dub,
dancehall, drum & bass, jungle, ragga jungle, dubstep, UK steppers, bass music: no factory
patterns to load, everything you hear, you play — or you load a riddim and dub over it.""",
    """**twenty-eight 64-step riddims** that load into the sequencer with their patterns, a four-band
**isolator** whose mutes really cut, a **tape delay** whose TIME knob bends the loop like a real
tape echo, per-track **throws** into the delay, and the **WIRES** visualizer — over the whole
SLOOP base: twelve synthesis engines, **180 sound-system presets** (the genre bank plus the
**Casio MT-40's 22 tones**), **38 drum kits** including the MT-40's rhythm unit, your own samples,
song mode, USB audio, MIDI in on the jack, MIDI clock and MIDI out. Reggae, roots, ska, dub,
dancehall, drum & bass, jungle, ragga jungle, dubstep, UK steppers, bass music — and the MT-40,
the keyboard the Sleng Teng came from: no factory patterns to load, everything you hear, you
play — or you load a riddim and dub over it.""")

# ---- status block
sub("""> **Status: SLOOP Dub 1.3.** The riddim bank grows to **twenty-two riddims**, each with its four
> patterns (bass, skanks, melody, drums) loadable one track at a time (mixing one riddim's bass
> with another's drums is the sound system's classic move), and the ten reggae / dub originals'
> drums play their full grooves again (the one drop's kick was silently swallowed by a same-step
> overwrite). The sound-system bank (1.1: 158 presets) is backed by the **drum kits** (1.2: 37,
> all level-matched). The isolator was rebuilt — its crossover sat a hundred times too low: SUB,
> BASS and MIDS came out near silence and TOPS carried the whole sound — and DLY TIME now bends
> the loop like a tape. Still custom firmware: install at your own risk, and please
> [report](../../issues) what you find. Your projects, presets, samples and settings are kept
> when you update, and you can go back at any time (see [Going back](#going-back)).""",
    """> **Status: SLOOP Dub 1.4 — the MT-40 release.** The **Casio MT-40** joins the firmware: its six
> auto-rhythms are six new riddims (`SLENG TENG` at their head — the machine's "Rock" preset,
> rebuilt), its **22 tones** fill a new **MT40** kind of the bank (1 Electric Piano … 22 Folk
> Flute, each a real patch), and its drum voices are the new **MT-40** kit. The riddim bank now
> holds **twenty-eight** 64-step riddims, each with its four patterns (bass, skanks, melody,
> drums) loadable one track at a time; the bank counts **180 presets** and **38 kits**, all
> level-matched. Everything is reconstructed by hand — no factory ROM data. Still custom
> firmware: install at your own risk, and please [report](../../issues) what you find. Your
> projects, presets, samples and settings are kept when you update, and you can go back at any
> time (see [Going back](#going-back)).""")

# ---- contents
sub("2. [The sound-system bank: 158 presets](#the-sound-system-bank-158-presets)\n3. [The drum kits: 37](#the-drum-kits-37)\n4. [The riddims: 22](#the-riddims-22)\n5. [Your first dub in 60 seconds](#your-first-dub-in-60-seconds)",
    "2. [The sound-system bank: 180 presets](#the-sound-system-bank-180-presets)\n3. [The drum kits: 38](#the-drum-kits-38)\n4. [The riddims: 28](#the-riddims-28)\n5. [The Casio MT-40: the functions, the rhythms, the sounds](#the-casio-mt-40-the-functions-the-rhythms-the-sounds)\n6. [Your first dub in 60 seconds](#your-first-dub-in-60-seconds)")
sub("6. [Screenshots](#screenshots)\n7. [The base SLOOP](#the-base-sloop)\n8. [Install](#install)\n9. [The controls](#the-controls)\n10. [The menu: settings of the FM-1](#the-menu-settings-of-the-fm-1)\n11. [MIDI and USB audio](#midi-and-usb-audio)\n12. [The web editor](#the-web-editor)\n13. [Compatibility](#compatibility)\n14. [Troubleshooting](#troubleshooting)\n15. [Specifications](#specifications)\n16. [Documentation](#documentation)\n17. [Building](#building)\n18. [Contributing](#contributing)\n19. [Credits and thanks](#credits-and-thanks)\n20. [Licence](#licence)",
    "7. [Screenshots](#screenshots)\n8. [The base SLOOP](#the-base-sloop)\n9. [Install](#install)\n10. [The controls](#the-controls)\n11. [The menu: settings of the FM-1](#the-menu-settings-of-the-fm-1)\n12. [MIDI and USB audio](#midi-and-usb-audio)\n13. [The web editor](#the-web-editor)\n14. [Compatibility](#compatibility)\n15. [Troubleshooting](#troubleshooting)\n16. [Specifications](#specifications)\n17. [Documentation](#documentation)\n18. [Building](#building)\n19. [Contributing](#contributing)\n20. [Credits and thanks](#credits-and-thanks)\n21. [Licence](#licence)")

# ---- dub wing references
sub("**OCT+ on RDM loads one of the twenty-two 64-step", "**OCT+ on RDM loads one of the twenty-eight 64-step")
sub("the bank is [below](#the-sound-system-bank-158-presets)", "the bank is [below](#the-sound-system-bank-180-presets)")

# ---- bank section
sub("## The sound-system bank: 158 presets", "## The sound-system bank: 180 presets")
sub("- **158 sound-system presets** (the list is [above](#the-sound-system-bank-158-presets)),",
    "- **180 sound-system presets** (the list is [above](#the-sound-system-bank-180-presets)),")

sub("""| SNARE FX | AMEN CUT | JUNGLE 16 | RAGGA CUT |
| USR SLICE | | | |

## The drum kits: 37""",
    """| SNARE FX | AMEN CUT | JUNGLE 16 | RAGGA CUT |
| USR SLICE | | | |

**MT40** — 22 (the Casio MT-40's 22 tones, the machine's own numbering 1–22; the story and the
engine behind each is [below](#the-casio-mt-40-the-functions-the-rhythms-the-sounds))

| | | | |
| --- | --- | --- | --- |
| MT E.PIANO | MT BANJO | MT GUITAR | MT HARPSI |
| MT XYLO | MT CELESTA | MT GLOCK | MT ORGAN |
| MT ACCORD | MT PIPE | MT ORIENT | MT BRASS |
| MT CELLO | MT SFUZZ | MT VIOLIN | MT TRUMPET |
| MT FUNNY | MT ENSMBL | MT CLARIN | MT FLUTE |
| MT RECORD | MT FOLKFLT | | |

## The drum kits: 38""")
sub("the\n**thirty-two synthesised kits** are built like on the classic machines",
    "the\n**thirty-three synthesised kits** are built like on the classic machines")
sub("""| RUBADUB | ARCADE | RAGGA | INDUSTR | GQOM |
| STEPPERS | JAZZ | | | |""",
    """| RUBADUB | ARCADE | RAGGA | INDUSTR | GQOM |
| STEPPERS | JAZZ | MT40 | | |""")

# ---- riddims section + the new MT-40 section
sub("## The riddims: 22\n\nTwenty-two 64-step riddims, four bars each,",
    "## The riddims: 28\n\nTwenty-eight 64-step riddims, four bars each,")
sub("""| UK bass music | BPM | | BPM |
| --- | --- | --- | --- |
| UK STEPPA | 84 | RAGGA JGL | 170 |
| DNB STEP | 174 | DUBSTEP | 140 |
| JUNGLE | 172 | UK 2STEP | 134 |
| BASSLINE | 132 | | |""",
    """| UK bass music | BPM | | BPM |
| --- | --- | --- | --- |
| UK STEPPA | 84 | RAGGA JGL | 170 |
| DNB STEP | 174 | DUBSTEP | 140 |
| JUNGLE | 172 | UK 2STEP | 134 |
| BASSLINE | 132 | | | |

| Casio MT-40 | BPM | | BPM |
| --- | --- | --- | --- |
| SLENG TENG | 82 | MT40 SWING | 84 |
| MT40 POPS | 96 | MT40 WALTZ | 90 |
| MT40 SLOWRK | 66 | MT40 SAMBA | 100 |

""" + MT40_SECTION)

# ---- install + about
sub("The installer serves **SLOOP Dub 1.3** (`sloop-dub-1.3.fwsc`)",
    "The installer serves **SLOOP Dub 1.4** (`sloop-dub-1.4.fwsc`)")
sub("- **Direct download:** [sloop-dub-1.3.fwsc](docs/firmware/sloop-dub-1.3.fwsc), installed with the\n  installer's file picker, or with `python tools/fm1_install.py sloop-dub-1.3.fwsc` (needs",
    "- **Direct download:** [sloop-dub-1.4.fwsc](docs/firmware/sloop-dub-1.4.fwsc), installed with the\n  installer's file picker, or with `python tools/fm1_install.py sloop-dub-1.4.fwsc` (needs")
sub("the version (*SLOOP DUB 1.3*) and its build date", "the version (*SLOOP DUB 1.4*) and its build date")

R.write_text(t)
print(f"README: {len(miss)} remplacement(s) NON TROUVÉ(S)")
for m in miss:
    print("  MISS:", m)
