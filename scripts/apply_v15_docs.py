#!/usr/bin/env python3
# Applies the v1.5 doc updates: the CHANGELOG entry, DUB-FR.md counts/riddim families/
# footprint, the RDM page examples.
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---- CHANGELOG.md : the 1.5 section, before 1.4
cl = ROOT / "CHANGELOG.md"
t = cl.read_text(encoding="utf-8")
V15 = """## 1.5 — novembre 2026

**Les classiques du sound system entrent dans la boîte.** Les onze riddims que tout sound
system a broyés — de la salle Studio One aux premières heures du digital — sont maintenant
dans la banque : **Heavenless, Tonight, Get in the Groove, Hot Milk, Answer, Promised Land,
Gunman, Here I Come, Sleng Teng, Tempo, Peany Peany**. Comme toujours dans ce dépôt, tout
est reconstruit à la main d'après le disque (aucun échantillon ni ROM copié) : le tempo, la
marche de basse, le drop — la première mesure dit de quel disque il vient.

- **Dix riddims nouveaux** (`tools/gen_riddims.py`), par famille :
  - **Studio One / rocksteady** — `HEAVENLESS` 80 bpm (Vin Gordon, 1968, Coxsone Dodd ;
    la marche root–quinte), `TONIGHT` 84 (Keith & Tex, 1967, Derrick Harriott ; la basse
    qui roule), `GET IN GROOVE` 88 (le riddim de 1968 alias *Up Park Camp* — John Holt
    l'a rendu célèbre en 1976), `HOT MILK` 92 (Jackie Mittoo & The Soul Vendors, 1968 ;
    le backbeat feutré, la ligne qui flotte), `ANSWER` 82 (le galop d'un seul accord —
    né de « I'll Never Let You Go » de Slim Smith & The Uniques, 1967), `PROMISED LAND`
    78 (Dennis Brown avec Aswad, 1981 ; le one-drop, la cadence F–B♭–C–G).
  - **Dancehall band et digital des années 80** — `GUNMAN` 78 (Michael Prophet, 1980,
    Henry « Junjo » Lawes à Channel One ; la marche mineure lourde des Roots Radics,
    le kick qui respire et le fill qui arrive), `HERE I COME` 95 (Barrington Levy, 1985 ;
    la pompe d'octaves), `TEMPO` 88 (Anthony Red Rose, 1985, Firehouse de King Tubby),
    `PEANY PEANY` 92 (le riddim de Bobby Digital, 1987, alias *Fade Away* — Little John
    l'a chanté d'abord) ; le `SLENG TENG` (déjà là depuis le 1.4) les précède.
- **Dix riddims cèdent leur place** pour tenir dans le slot — la banque reste à **28** et
  l'échange ne coûte que +32 o : `DIGITAL`, `LOVERS`, `SKANKIN`, `ROCKSTDY`, `TWO TONE`,
  `UK STEPPA`, `DNB STEP`, `RAGGA JGL`, `UK 2STEP`, `BASSLINE`. Les racines restent
  (`ONE DROP`, `STEPPERS`, `ROCKERS`, `DUBWALK`, `MEDITATE`, `DUB CUT`, `ZION`, `SKA`,
  `DANCEHALL`, `DEMBOW`, `JUNGLE`, `DUBSTEP`) et les cinq autres auto-rythmes du MT-40
  aussi (`MT40 POPS`, `MT40 SLOWRK`, `MT40 SWING`, `MT40 WALTZ`, `MT40 SAMBA`).
- **La chaîne web suit** : l'émulateur recompilé (zig, wasm32) passe le smoke test — 28
  riddims dont les onze, AUDIO-PATH-OK / DUB-SEQ-PLAYS-OK ; le wasm de l'éditeur suit ;
  l'installateur web sert le paquet 1.5 (sha256 vérifié), le STAMP du service worker est
  recalculé.
- **La place** : l'image passe de 580 944 à **580 976 o** (+32 o) sur le slot de 0x8DFBC
  (581 564 o) — **588 o de marge**.

## 1.4 — novembre 2026"""
assert t.count("## 1.4 — novembre 2026") == 1
t = t.replace("## 1.4 — novembre 2026", V15)
cl.write_text(t, encoding="utf-8")
print("CHANGELOG: 1.5 inséré")

# ---- DUB-FR.md
fr = ROOT / "DUB-FR.md"
t = fr.read_text(encoding="utf-8")

def sub(old, new):
    global t
    assert old in t, f"DUB-FR: not found: {old[:70]!r}"
    assert t.count(old) == 1, f"DUB-FR: not unique: {old[:70]!r}"
    t = t.replace(old, new)

sub("`docs/firmware/sloop-dub-1.4.fwsc` (image 580 944 o de 581 564 [slot 0x8DFBC], marge 620 o)",
    "`docs/firmware/sloop-dub-1.5.fwsc` (image 580 976 o de 581 564 [slot 0x8DFBC], marge 588 o)")
sub("**`docs/firmware/sloop-dub-1.4.fwsc`**", "**`docs/firmware/sloop-dub-1.5.fwsc`**")

sub("""organisées par genre : **reggae / dub / roots** (`ONE DROP`, `STEPPERS`, `ROCKERS`, `DUBWALK`, `DIGITAL`, `LOVERS`, `MEDITATE`, `SKANKIN`, `DUB CUT`, `ZION`), **ska** (`SKA`, `TWO TONE`, `ROCKSTDY`), **dancehall** (`DANCEHALL`, `DEMBOW`) et **bass music UK** (`UK STEPPA`, `DNB STEP`, `JUNGLE`, `RAGGA JGL`, `DUBSTEP`, `UK 2STEP`, `BASSLINE`) et les **six auto-rythmes du Casio MT-40** (`SLENG TENG` — le preset « Rock » de la machine dont est né le Sleng Teng —, `MT40 POPS`, `MT40 SLOWRK`, `MT40 SWING`, `MT40 WALTZ`, `MT40 SAMBA`)""",
"""organisées par genre : **reggae / dub / roots** (`ONE DROP`, `STEPPERS`, `ROCKERS`, `DUBWALK`, `MEDITATE`, `DUB CUT`, `ZION`), **ska** (`SKA`), **les classiques du sound system** (`HEAVENLESS`, `TONIGHT`, `GET IN GROOVE`, `HOT MILK`, `ANSWER`, `PROMISED LAND`, `GUNMAN`, `HERE I COME`, `SLENG TENG`, `TEMPO`, `PEANY PEANY`), **dancehall** (`DANCEHALL`, `DEMBOW`), **bass music UK** (`JUNGLE`, `DUBSTEP`) et les **cinq autres auto-rythmes du Casio MT-40** (`MT40 POPS`, `MT40 SLOWRK`, `MT40 SWING`, `MT40 WALTZ`, `MT40 SAMBA`)""")

sub("une basse de `DNB STEP` sous les drums de `ONE DROP`, un skank de `UK 2STEP` sur le dembow",
    "une basse de `GUNMAN` sous les drums de `ONE DROP`, un skank de `TONIGHT` sur le dembow")

sub("""Les vingt-huit riddims (`tools/gen_riddims.py` → `firmware/src/dub_riddim.h`, ~11 Ko en ROM), le tempo conseillé du projet avec chacun : la famille **reggae / dub / roots** — `ONE DROP` 72 bpm, `STEPPERS` 76, `ROCKERS` 80, `DUBWALK` 70, `DIGITAL` 92, `LOVERS` 84, `MEDITATE` 66, `SKANKIN` 88, `DUB CUT` 74, `ZION` 68 ; la famille **ska** — `SKA` 88 (marche de basse en noires, rim sec sur les contretemps), `TWO TONE` 92 (pompes d'octaves à la 2 Tone), `ROCKSTDY` 76 (le rebond rocksteady) ; la famille **dancehall** — `DANCEHALL` 95 (le clap 3+3+2, les stabs poussés, la fanfare), `DEMBOW` 100 (le boom-ch-boom-chick strict) ; la famille **bass music UK** — `UK STEPPA` 84 (le kick au temps, le drone profond, les rims), `DNB STEP` 174 (le two-step, les ghost snares, la sub qui roule), `JUNGLE` 172 (le break haché, la sub qui répond), `RAGGA JGL` 170 (le break + le clap ragga, les stabs fanfare), `DUBSTEP` 140 (le half-time, la sub wobblée, une seule stab sombre), `UK 2STEP` 134 (la syncope garage, les accords poussés), `BASSLINE` 132 (le kick au temps, la basse en contretemps, les claps décalés) ; la famille **MT-40** — `SLENG TENG` 82 (le « Rock » de la Casio MT-40 reconstruit à la main : la pompe en croches, le pop d'octave, la retombée b7 ; la machine ne jouait que basses et drums, le skank est la contremise du musicien ; sa 4e mesure porte le fill-in du FILL-IN), `MT40 POPS` 96, `MT40 SLOWRK` 66 (le half-time paresseux), `MT40 SWING` 84 (la basse qui marche), `MT40 WALTZ` 90 (le oom-pah-pah sur une grille 4/4), `MT40 SAMBA` 100 (l'agogo au rim, la surdo syncopée) — chacun sa progression (Am, Dm, F, G…), son groove de basse, ses skanks et son pattern de drums. Réglez le BPM du projet sur le tempo du riddim pour le feel juste.""",
"""Les vingt-huit riddims (`tools/gen_riddims.py` → `firmware/src/dub_riddim.h`, ~14 Ko en ROM), le tempo conseillé du projet avec chacun : la famille **reggae / dub / roots** — `ONE DROP` 72 bpm, `STEPPERS` 76, `ROCKERS` 80, `DUBWALK` 70, `MEDITATE` 66, `DUB CUT` 74, `ZION` 68 ; la famille **ska** — `SKA` 88 (la marche de basse en noires, le rim sec sur les contretemps) ; les **classiques du sound system**, reconstruits à la main d'après le disque — `HEAVENLESS` 80 (Vin Gordon, 1968, Studio One ; la marche root–quinte), `TONIGHT` 84 (Keith & Tex, 1967, Derrick Harriott ; la basse rocksteady qui roule), `GET IN GROOVE` 88 (le riddim Studio One de 1968 alias *Up Park Camp* — John Holt 1976), `HOT MILK` 92 (Jackie Mittoo, 1968 ; le backbeat feutré), `ANSWER` 82 (le galop d'un seul accord, de « I'll Never Let You Go » de Slim Smith & The Uniques, 1967), `PROMISED LAND` 78 (Dennis Brown avec Aswad, 1981), `GUNMAN` 78 (Michael Prophet, 1980, Junjo Lawes à Channel One ; la marche mineure lourde des Roots Radics), `HERE I COME` 95 (Barrington Levy, 1985 ; la pompe d'octaves), `SLENG TENG` 82 (le « Rock » de la Casio MT-40 : la pompe en croches, le pop d'octave, la retombée b7 — la 4e mesure porte le fill-in du FILL-IN), `TEMPO` 88 (Anthony Red Rose, 1985, Firehouse de King Tubby), `PEANY PEANY` 92 (Bobby Digital, 1987, alias *Fade Away*) ; la famille **dancehall** — `DANCEHALL` 95 (le clap 3+3+2, les stabs poussés, la fanfare), `DEMBOW` 100 (le boom-ch-boom-chick strict) ; la famille **bass music UK** — `JUNGLE` 172 (le break haché, la sub qui répond), `DUBSTEP` 140 (le half-time, la sub wobblée, une seule stab sombre) ; la famille **MT-40** — `MT40 POPS` 96, `MT40 SLOWRK` 66 (le half-time paresseux), `MT40 SWING` 84 (la basse qui marche), `MT40 WALTZ` 90 (le oom-pah-pah sur une grille 4/4), `MT40 SAMBA` 100 (l'agogo au rim, la surdo syncopée) — chacun sa progression (Am, Dm, F, G…), son groove de basse, ses skanks et son pattern de drums. Réglez le BPM du projet sur le tempo du riddim pour le feel juste.""")

sub("""## Empreinte FM-1 (mesurée, build 1.4)""", """## Empreinte FM-1 (mesurée, build 1.5)""")
sub("""la marge jusqu'à 576 208 o ; le 1.4 y ajoute les six riddims et les 22 sons du Casio MT-40, le kit
MT40 et leurs noms, et l'image s'établit à 580 944 o — **620 o de marge** sur le slot de 0x8DFBC.""",
"""la marge jusqu'à 576 208 o ; le 1.4 y ajoute les six riddims et les 22 sons du Casio MT-40, le kit
MT40 et leurs noms (580 944 o) ; le 1.5 échange dix riddims génériques contre les onze classiques
du sound system (+32 o), et l'image s'établit à 580 976 o — **588 o de marge** sur le slot de 0x8DFBC.""")
sub("| Ressource | 2.9.6 (base) | 2.9.13 | 2.9.16 | **1.4 (ce build)** | Capacité | Marge 1.4 |\n|---|---|---|---|---|---|---|\n| Image flash (code + rodata) | 580 692 o | 572 784 o | 565 040 o | **580 944 o** | 581 564 o | **620 o** |",
    "| Ressource | 2.9.6 (base) | 2.9.13 | 2.9.16 | **1.5 (ce build)** | Capacité | Marge 1.5 |\n|---|---|---|---|---|---|---|\n| Image flash (code + rodata) | 580 692 o | 572 784 o | 565 040 o | **580 976 o** | 581 564 o | **588 o** |")

fr.write_text(t, encoding="utf-8")
print("DUB-FR: 1.5 appliqué")
