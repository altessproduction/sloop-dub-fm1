#!/usr/bin/env python3
# Applies the v1.4 doc updates: CHANGELOG entry, DUB-FR.md counts/footprint, GUIDE.md bank count.
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- CHANGELOG.md : the 1.4 section, before 1.3
cl = ROOT / "CHANGELOG.md"
t = cl.read_text()
V14 = """## 1.4 — novembre 2026

**Le Casio MT-40 entre dans la boîte.** Le clavier de 1981 dont un preset — le « Rock »
de Hiroko Okuda — a fait basculer le reggae dans l'ère digitale fournit maintenant ses
**six auto-rythmes**, ses **22 sons** et son **unité de rythme** au SLOOP Dub. Tout est
reconstruit à la main (aucune donnée ROM d'usine copiée), dans l'esprit du dépôt : le
sleng est reconnaissable à la première mesure.

- **Six riddims MT-40** (`tools/gen_riddims.py`, la banque passe de 22 à **28**) :
  `SLENG TENG` 82 bpm (la pompe en croches, le pop d'octave, la retombée sur la b7 —
  la progression de « Under Mi Sleng Teng », C#m–B–A–B), `MT40 POPS` 96, `MT40 SLOWRK` 66,
  `MT40 SWING` 84 (la basse qui marche), `MT40 WALTZ` 90 (le oom-pah-pah posé sur la
  grille 4/4), `MT40 SAMBA` 100 (l'agogo au rim, la surdo syncopée). La machine ne jouait
  que basses et drums : le skank reste la contremise du musicien, la mélodie celle du
  toaster ; la 4e mesure de chaque riddim porte le **fill-in** que l'interrupteur
  FILL-IN de la machine lâchait (un rouleau de caisse claire, ou un fill de toms).
- **Les 22 sons dans une catégorie `MT40`** (page PRESETS), dans l'ordre de la liste de
  la machine : 1 Electric Piano, 2 Banjo, 3 Guitar, 4 Harpsichord, 5 Xylophone, 6 Celesta,
  7 Glockenspiel, 8 Organ, 9 Accordion, 10 Pipe Organ, 11 Oriental Pipe, 12 Brass,
  13 Cello, 14 Synth. Fuzz, 15 Violin, 16 Trumpet, 17 Funny Fuzz, 18 St. Ensemble,
  19 Clarinet, 20 Flute, 21 Recorder, 22 Folk Flute. Répartis là où ils sonnent juste :
  12 en DIGITAL (les claviers, mallettes et anches FM), 2 en ANALOG (brass, strings),
  3 en WHEEL (les orgues), 4 en PHYS (banjo, guitare, violon, violoncelle) et le Funny
  Fuzz en LOFI. `scripts/update_editor_presets.py` suit.
- **Le kit `MT-40`** (33e kit synthétisé, `tools/gen_drumkits.py`) : la caisse claire fine
  au bruit « chip », le kick court et carré, les charleys minuscules, la cymbale courte —
  et un soupçon de crush (1 bit, sample-and-hold 2) pour le DAC de 1981. Il rejoint la
  banque drums du module DUB (`DUB_DK_KITS`, 9 kits).
- **L'émulateur web suit** (`reference_emu/build.sh`, wasm32) : le smoke test attend
  28 riddims dont `SLENG TENG` et 9 kits — AUDIO-PATH-OK, DUB-SEQ-PLAYS-OK.
- **La place comptait** : l'image passe de 576 208 à **580 944 o** sur le slot de
  0x8DFBC (581 564 o) — **620 o de marge**. Les six riddims (+3 Ko de pas), les 22
  presets (~1 Ko), le kit (~360 o) et leurs noms ont repris presque tout le reste.

"""
t = t.replace("## 1.3 — novembre 2026", V14 + "## 1.3 — novembre 2026", 1)
cl.write_text(t)
print("CHANGELOG: 1.4 inséré")

# ---- DUB-FR.md
d = ROOT / "DUB-FR.md"
t = d.read_text()
subs = [
    ("`docs/firmware/sloop-dub-1.3.fwsc` (image 576 208 o de 581 052, marge 4 844 o)",
     "`docs/firmware/sloop-dub-1.4.fwsc` (image 580 944 o de 581 564 [slot 0x8DFBC], marge 620 o)"),
    ("vingt-deux séquences sound-system de 64 pas × 4 pistes",
     "vingt-huit séquences sound-system de 64 pas × 4 pistes"),
    ("`UK 2STEP`, `BASSLINE`) sur la page RDM",
     "`UK 2STEP`, `BASSLINE`) et les **six auto-rythmes du Casio MT-40** (`SLENG TENG` — le preset "
     "« Rock » de la machine dont est né le Sleng Teng —, `MT40 POPS`, `MT40 SLOWRK`, `MT40 SWING`, "
     "`MT40 WALTZ`, `MT40 SAMBA`) sur la page RDM"),
    ("`KN1` sélectionne parmi les vingt-deux", "`KN1` sélectionne parmi les vingt-huit"),
    ("### Le séquenceur dub et les vingt-deux riddims", "### Le séquenceur dub et les vingt-huit riddims"),
    ("Les vingt-deux riddims (`tools/gen_riddims.py`", "Les vingt-huit riddims (`tools/gen_riddims.py`"),
    ("`BASSLINE` 132 (le kick au temps, la basse en contretemps, les claps décalés) — chacun sa progression",
     "`BASSLINE` 132 (le kick au temps, la basse en contretemps, les claps décalés) ; la famille "
     "**MT-40** — `SLENG TENG` 82 (le « Rock » de la Casio MT-40 reconstruit à la main : la pompe en croches, "
     "le pop d'octave, la retombée b7 ; la machine ne jouait que basses et drums, le skank est la contremise "
     "du musicien ; sa 4e mesure porte le fill-in du FILL-IN), `MT40 POPS` 96, `MT40 SLOWRK` 66 (le half-time "
     "paresseux), `MT40 SWING` 84 (la basse qui marche), `MT40 WALTZ` 90 (le oom-pah-pah sur une grille 4/4), "
     "`MT40 SAMBA` 100 (l'agogo au rim, la surdo syncopée) — chacun sa progression"),
    ("la banque de riddims (2.9.2) : vingt-deux séquences nommées",
     "la banque de riddims (2.9.2) : vingt-huit séquences nommées"),
    ("**`docs/firmware/sloop-dub-1.3.fwsc`**", "**`docs/firmware/sloop-dub-1.4.fwsc`**"),
    ("## Empreinte FM-1 (mesurée, build 1.3)", "## Empreinte FM-1 (mesurée, build 1.4)"),
    ("sound-system (1.1 : 158 presets, 1.2 : 37 kits, 1.3 : 22 riddims et leurs patterns) reprend ensuite\nla marge jusqu'à 576 208 o.",
     "sound-system (1.1 : 158 presets, 1.2 : 37 kits, 1.3 : 22 riddims et leurs patterns) reprend ensuite\nla marge jusqu'à 576 208 o ; le 1.4 y ajoute les six riddims et les 22 sons du Casio MT-40, le kit\nMT40 et leurs noms, et l'image s'établit à 580 944 o — **620 o de marge** sur le slot de 0x8DFBC."),
    ("| **1.3 (ce build)** | Capacité | Marge 1.3 |", "| **1.4 (ce build)** | Capacité | Marge 1.4 |"),
    ("| Image flash (code + rodata) | 580 692 o | 572 784 o | 565 040 o | **576 208 o** | 581 052 o | **4 844 o** |",
     "| Image flash (code + rodata) | 580 692 o | 572 784 o | 565 040 o | **580 944 o** | 581 564 o | **620 o** |"),
    ("| RAM `.data`+`.bss` | 60 108 o | 60 448 o | 57 600 o | **57 608 o** | 98 304 o | 40 696 o |",
     "| RAM `.data`+`.bss` | 60 108 o | 60 448 o | 57 600 o | **57 624 o** | 98 304 o | 40 680 o |"),
]
miss = 0
for a, b in subs:
    if a in t:
        t = t.replace(a, b, 1)
    else:
        miss += 1
        print("DUB-FR: NON TROUVÉ:", a[:70])
d.write_text(t)
print(f"DUB-FR: {len(subs) - miss}/{len(subs)} remplacements")

# ---- GUIDE.md
g = ROOT / "GUIDE.md"
t = g.read_text()
a = "**158 sound-system presets** (SLOOP Dub 1.1: reggae, roots, ska, dub, drum & bass, jungle, ragga, dubstep, UK steppers, bass music), every one a full patch on one of the engines, all level-matched (the same LEVEL gives the same loudness). **PRESETS** browses them **by kind** — basses, keys, organs, pads, leads, plucks and bells, stabs, FX —"
b = "**180 sound-system presets** — the 158 genre presets of SLOOP Dub 1.1 (reggae, roots, ska, dub, drum & bass, jungle, ragga, dubstep, UK steppers, bass music) plus the **Casio MT-40's 22 tones** (1.4), every one a full patch on one of the engines, all level-matched (the same LEVEL gives the same loudness). **PRESETS** browses them **by kind** — basses, keys, organs, pads, leads, plucks and bells, stabs, FX, MT40 —"
if a in t:
    t = t.replace(a, b, 1)
    print("GUIDE: banque 180 OK")
else:
    print("GUIDE: NON TROUVÉ")
g.write_text(t)
