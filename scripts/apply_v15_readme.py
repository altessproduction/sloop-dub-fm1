#!/usr/bin/env python3
# Applies the v1.5 README updates: status block, links, version strings, the riddim
# tables (the classics in, the dropped ones out), a "The classic riddims" section with
# each riddim's origin, and the TOC.
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "README.md"
t = P.read_text(encoding="utf-8")

def sub(old, new):
    global t
    assert old in t, f"README: not found: {old[:70]!r}"
    assert t.count(old) == 1, f"README: not unique: {old[:70]!r}"
    t = t.replace(old, new)

# ---- version strings
sub('alt="SLOOP DUB 1.4 · FM-1"', 'alt="SLOOP DUB 1.5 · FM-1"')
sub('<a href="docs/firmware/sloop-dub-1.4.fwsc">the 1.4 package (.fwsc)</a>',
    '<a href="docs/firmware/sloop-dub-1.5.fwsc">the 1.5 package (.fwsc)</a>')
sub("The installer serves **SLOOP Dub 1.4** (`sloop-dub-1.4.fwsc`)",
    "The installer serves **SLOOP Dub 1.5** (`sloop-dub-1.5.fwsc`)")
sub("- **Direct download:** [sloop-dub-1.4.fwsc](docs/firmware/sloop-dub-1.4.fwsc), installed with the\n  installer's file picker, or with `python tools/fm1_install.py sloop-dub-1.4.fwsc` (needs",
    "- **Direct download:** [sloop-dub-1.5.fwsc](docs/firmware/sloop-dub-1.5.fwsc), installed with the\n  installer's file picker, or with `python tools/fm1_install.py sloop-dub-1.5.fwsc` (needs")
sub("the version (*SLOOP DUB 1.4*) and its build date", "the version (*SLOOP DUB 1.5*) and its build date")
sub("`sloop-editor-1.4.html`", "`sloop-editor-1.5.html`")
sub("by **Altess Production**, from 2.9.1 to 1.4.", "by **Altess Production**, from 2.9.1 to 1.5.")

# ---- the status block
sub("""> **Status: SLOOP Dub 1.4 — the MT-40 release.** The **Casio MT-40** joins the firmware: its six
> auto-rhythms are six new riddims (`SLENG TENG` at their head — the machine's "Rock" preset,
> rebuilt), its **22 tones** fill a new **MT40** kind of the bank (1 Electric Piano … 22 Folk
> Flute, each a real patch), and its drum voices are the new **MT-40** kit. The riddim bank now
> holds **twenty-eight** 64-step riddims, each with its four patterns (bass, skanks, melody,
> drums) loadable one track at a time; the bank counts **180 presets** and **38 kits**, all
> level-matched. Everything is reconstructed by hand — no factory ROM data. Still custom
> firmware: install at your own risk, and please [report](../../issues) what you find. Your
> projects, presets, samples and settings are kept when you update, and you can go back at any
> time (see [Going back](#going-back)).""",
"""> **Status: SLOOP Dub 1.5 — the classic riddims.** The **eleven riddims every sound system
> grew up on** join the bank: **Heavenless, Tonight, Get in the Groove, Hot Milk, Answer,
> Promised Land, Gunman, Here I Come, Sleng Teng, Tempo, Peany Peany** — from the Studio One
> rocksteady of 1967–68 to the first digital dancehall of 1985–87, each one a full 64-step
> riddim with its four patterns, **rebuilt by hand from the records** (no factory ROM data, no
> sample copied — the groove is recognisable from the first bar; their origins are in
> [The classic riddims](#the-classic-riddims)). Ten generic riddims step aside so the bank
> stays at **twenty-eight** and the build fits its slot (588 bytes to spare); the MT-40's six
> rhythms, its 22 tones and its kit stay (see [The Casio MT-40](#the-casio-mt-40-the-functions-the-rhythms-the-sounds)).
> The bank counts **180 presets** and **38 kits**, all level-matched. Still custom firmware:
> install at your own risk, and please [report](../../issues) what you find. Your projects,
> presets, samples and settings are kept when you update, and you can go back at any time
> (see [Going back](#going-back)).""")

# ---- the riddim tables
sub("""| Reggae · dub · roots | BPM | | BPM |
| --- | --- | --- | --- |
| ONE DROP | 72 | DUBWALK | 70 |
| STEPPERS | 76 | DIGITAL | 92 |
| ROCKERS | 80 | LOVERS | 84 |
| MEDITATE | 66 | SKANKIN | 88 |
| DUB CUT | 74 | ZION | 68 |

| Ska | BPM | Dancehall / ragga | BPM |
| --- | --- | --- | --- |
| SKA | 88 | DANCEHALL | 95 |
| TWO TONE | 92 | DEMBOW | 100 |
| ROCKSTDY | 76 | | |

| UK bass music | BPM | | BPM |
| --- | --- | --- | --- |
| UK STEPPA | 84 | RAGGA JGL | 170 |
| DNB STEP | 174 | DUBSTEP | 140 |
| JUNGLE | 172 | UK 2STEP | 134 |
| BASSLINE | 132 | | | |

| Casio MT-40 | BPM | | BPM |
| --- | --- | --- | --- |
| SLENG TENG | 82 | MT40 SWING | 84 |
| MT40 POPS | 96 | MT40 WALTZ | 90 |
| MT40 SLOWRK | 66 | MT40 SAMBA | 100 |""",
"""| Reggae · dub · roots | BPM | | BPM |
| --- | --- | --- | --- |
| ONE DROP | 72 | DUBWALK | 70 |
| STEPPERS | 76 | MEDITATE | 66 |
| ROCKERS | 80 | DUB CUT | 74 |
| SKA | 88 | ZION | 68 |

| The classics | BPM | | BPM |
| --- | --- | --- | --- |
| HEAVENLESS | 80 | GUNMAN | 78 |
| TONIGHT | 84 | HERE I COME | 95 |
| GET IN GROOVE | 88 | SLENG TENG | 82 |
| HOT MILK | 92 | TEMPO | 88 |
| ANSWER | 82 | PEANY PEANY | 92 |
| PROMISED LAND | 78 | | |

| Dancehall / ragga | BPM | UK bass music | BPM |
| --- | --- | --- | --- |
| DANCEHALL | 95 | JUNGLE | 172 |
| DEMBOW | 100 | DUBSTEP | 140 |

| Casio MT-40 | BPM | | BPM |
| --- | --- | --- | --- |
| MT40 POPS | 96 | MT40 SWING | 84 |
| MT40 SLOWRK | 66 | MT40 WALTZ | 90 |
| | | MT40 SAMBA | 100 |""")

# ---- the new section, before the MT-40 one
sub("""## The Casio MT-40: the functions, the rhythms, the sounds""",
"""## The classic riddims

The eleven riddims every sound system grew up on, from the 1.5: each one is a full 64-step
riddim with its four patterns (bass, skanks, melody, drums), and each one is **rebuilt by hand
from the records** — no sample, no factory ROM data, only the tempo, the bass line and the drop
reconstructed so the first bar says which record it came from. Their origins:

| Riddim | First came from | Year, studio |
| --- | --- | --- |
| **HEAVENLESS** | Vin Gordon's *Heavenless* (cut as Don Drummond Jr) & Sound Dimension | 1968, Studio One (Coxsone Dodd) |
| **TONIGHT** | Keith & Tex, *Tonight* — the rolling rocksteady bass | 1967, prod. Derrick Harriott |
| **GET IN GROOVE** | the Get in the Groove riddim, aka *Up Park Camp* — Roy Shirley's *Get in the Groove*, John Holt's *Up Park Camp* | 1968 Studio One; Holt 1976 |
| **HOT MILK** | Jackie Mittoo & The Soul Vendors, *Hot Milk* — the floating lead | 1968, Studio One (Coxsone Dodd) |
| **ANSWER** | Slim Smith & The Uniques, *I'll Never Let You Go* — the one-chord gallop | 1967, Studio One; 80s recuts |
| **PROMISED LAND** | Dennis Brown, *The Promised Land*, with Aswad (cut on the UK side as *Love Fire*) | 1981 |
| **GUNMAN** | Michael Prophet, *Gunman* — the Roots Radics' heavy march, Scientist at the mix | 1980, Junjo Lawes, Channel One |
| **HERE I COME** | Barrington Levy, *Here I Come (Broader Than Broadway)* | 1985 |
| **SLENG TENG** | Wayne Smith, *Under Mi Sleng Teng* — the MT-40's "Rock" preset | 1984/85, King Jammy's |
| **TEMPO** | Anthony Red Rose, *Tempo* | 1985, Firehouse (King Tubby) |
| **PEANY PEANY** | the Peanie Peanie riddim, aka *Fade Away* — Little John voiced it first, Shabba Ranks made it famous | 1987, Bobby Digital |

Ten generic riddims of the 1.1–1.4 bank step aside to keep the bank at twenty-eight and the
image inside its slot: `DIGITAL`, `LOVERS`, `SKANKIN`, `TWO TONE`, `ROCKSTDY`, `UK STEPPA`,
`DNB STEP`, `RAGGA JGL`, `UK 2STEP`, `BASSLINE`. The bases stay: the reggae / dub / roots
family, `SKA`, `DANCEHALL`, `DEMBOW`, `JUNGLE`, `DUBSTEP` and the MT-40's five other rhythms.

## The Casio MT-40: the functions, the rhythms, the sounds""")

# ---- TOC
sub("""4. [The riddims: 28](#the-riddims-28)
5. [The Casio MT-40: the functions, the rhythms, the sounds](#the-casio-mt-40-the-functions-the-rhythms-the-sounds)
6. [Your first dub in 60 seconds](#your-first-dub-in-60-seconds)
7. [Screenshots](#screenshots)
8. [The base SLOOP](#the-base-sloop)
9. [Install](#install)
10. [The controls](#the-controls)
11. [The menu: settings of the FM-1](#the-menu-settings-of-the-fm-1)
12. [MIDI and USB audio](#midi-and-usb-audio)
13. [The web editor](#the-web-editor)
14. [Compatibility](#compatibility)
15. [Troubleshooting](#troubleshooting)
16. [Specifications](#specifications)""",
"""4. [The riddims: 28](#the-riddims-28)
5. [The classic riddims](#the-classic-riddims)
6. [The Casio MT-40: the functions, the rhythms, the sounds](#the-casio-mt-40-the-functions-the-rhythms-the-sounds)
7. [Your first dub in 60 seconds](#your-first-dub-in-60-seconds)
8. [Screenshots](#screenshots)
9. [The base SLOOP](#the-base-sloop)
10. [Install](#install)
11. [The controls](#the-controls)
12. [The menu: settings of the FM-1](#the-menu-settings-of-the-fm-1)
13. [MIDI and USB audio](#midi-and-usb-audio)
14. [The web editor](#the-web-editor)
15. [Compatibility](#compatibility)
16. [Troubleshooting](#troubleshooting)
17. [Specifications](#specifications)""")

P.write_text(t, encoding="utf-8")
print("README: 1.5 appliqué")
