# SLOOP Dub FM-1 — la banque Riddim Collection (27 riddims)

Ce dépôt est le firmware **SLOOP Dub 1.7** (M-VAVE FM-1) dont **tous les riddims ont été
remplacés** par les vingt-sept riddims de la page
[Riddim Collection](https://altessproduction.github.io/Riddim-collection/riddims.html)
(Altess Production), dans l'ordre demandé, avec **la basse en piste 1, le skank en piste 2,
l'instrument restant en piste 3 et la batterie en piste 4**.

## Le paquet à installer

`sloop-dub-1.7-riddims.fwsc` — construit avec `./build.sh --release 1.7`
(identité **FM-1_234**, la même que le 1.7 officiel ; projets, presets, samples et réglages
conservés à la mise à jour). Image 580 656 o pour un slot de 581 564 o — **908 o de marge**.

## La banque (l'ordre de la page RDM)

| # | Nom LCD | Riddim de la page | Style | BPM (page) | Skank (piste 2) | Piste 3 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | AFRICAN BEAT | African Beat | reggae | 70–78 | contretemps sur la grille B · F♯ | — |
| 2 | ANSWER | Answer | reggae | 75–86 | contretemps sur B♭ · E♭ | — |
| 3 | ARTIBELLA | Artibella | reggae | 65–83 | skank du pack | orgue du pack |
| 4 | BAM BAM | Bam Bam | dancehall | 96 | accords du pack (Stalag) | — |
| 5 | BILLIE JEAN | Billie Jean | rockers | 72–86 | accords du pack | — |
| 6 | CREATED FATHER | Created By The Father | reggae | 80 | accords du pack | — |
| 7 | QUEEN MAJESTY | Queen Majesty | rocksteady | 94–100 | guitare du pack | orgue du pack |
| 8 | REAL ROCK | Real Rock | one drop | 70–90 | skank du pack | orgue du pack |
| 9 | SWING EASY | Swing Easy | one drop | 72–92 | guitare du pack | accords du pack |
| 10 | BABA BOOM | Baba Boom | steppers | 82 | accords du pack (1) | accords du pack (2) |
| 11 | CHASE VAMPIRE | Chase Vampire | steppers | 85 | skank du pack | — |
| 12 | DRUM SONG | Drum Song | digital | 89 | accords du pack | — |
| 13 | DUB ORGANIZER | Dub Organizer | steppers | 76 | skank du pack | — |
| 14 | DUBOLITIONS | Dubolitions | rocksteady | 119 | skank du pack | orgue du pack |
| 15 | EVERY TONGUE | Every Tongue Shall Tell | steppers | 81 | accords du pack | — |
| 16 | FISHERMAN | Fisherman | steppers | 75 | accords du pack | cuivres du pack |
| 17 | GHETTO PEOPLE | Ghetto People Song | steppers | 80 | accords du pack | — |
| 18 | GRAB YR LASS | Grab Your Lass and Come | steppers | 85 | guitare du pack | orgue du pack |
| 19 | HEATHEN | Heathen | steppers | 71 | accords du pack | — |
| 20 | JAVA | Java | steppers | 77 | skank du pack | — |
| 21 | LIBERATION | Liberation | rocksteady | 71 | guitare du pack | orgue du pack |
| 22 | MR BASSIE | Mr Bassie | rockers | 86 | accords du pack | — |
| 23 | REVOLUTION | Revolution | steppers | 89 | skank du pack | — |
| 24 | THE WHIP | The Whip | digital | 83 | skank du pack | cuivres du pack |
| 25 | WARRIORS CRY | Warriors Don't Cry | digital | 89 | accords du pack | — |
| 26 | WHEN I FALL | When I Fall in Love | digital | 80 | accords du pack | mélodie du pack |
| 27 | SLENG TENG | Sleng Teng | digital | 82 | contretemps (D) | — |

## Comment la transcription a été faite

Le générateur **`tools/gen_riddims_web.py`** lit la grille de la page
(`tools/riddims_db.js`, la base `window.RIDDB` du site) et écrit
`firmware/src/dub_riddim.h` :

- **Basse (piste 1)** : les mesures de la page, bouclées sur les quatre bars, notes telles
  quelles (grille en doubles-croches), vélocités de la page (112 au temps, 96 hors temps) ;
  les longueurs de notes reviennent en tenues (TIE) et en coupures `DUB_SEQ_CUT` (253) —
  chaque note écrite ré-attaque, même au même pitch.
- **Skank (piste 2)** : quand la page a un accompagnement *skank* ou *guitare* (ou des
  accords), ce sont ses stabs — leur racine nourrit l'accord que la page **SKK** de la
  machine construit (MAJ/MIN/7TH…, octave réglable) ; sinon, contretemps classiques
  2 · 6 · 10 · 14 sur les racines de la grille d'accords de la page (`AFRICAN BEAT`,
  `ANSWER`, `SLENG TENG` — deux accords sur une mesure = un changement à la mi-mesure).
- **Piste 3 (l'instrument restant)** : l'autre accompagnement de la page — orgue, cuivres,
  deuxième accords ou mélodie —, la note du haut par temps, tenues et coupures respectées.
  Les riddims que la page joue basse-et-drums seulement laissent la piste 3 **vide** (à vous
  de la jouer) : AFRICAN BEAT, ANSWER, BAM BAM, BILLIE JEAN, CREATED FATHER, CHASE VAMPIRE,
  DRUM SONG, DUB ORGANIZER, EVERY TONGUE, GHETTO PEOPLE, HEATHEN, JAVA, MR BASSIE,
  REVOLUTION, WARRIORS CRY, SLENG TENG.
- **Batterie (piste 4)** : le pattern propre du riddim quand la page en a un (le pack, le
  Sleng Teng), sinon celui de son style. La banque tient **une note de drum par pas** : là
  où la page empile kick et caisse claire (Sleng Teng) ou kick et rim (le one-drop), le
  **kick entre une double-croche avant** (le pickup du sound system) et les charleys
  déplacés sortent ; les ghosts restent doux (niveau GHOST).

Les six noms courts (l'écran tient quatorze caractères) : CREATED FATHER, EVERY TONGUE,
GHETTO PEOPLE, GRAB YR LASS, WARRIORS CRY, WHEN I FALL — le nom complet de la page est dans
le tableau ci-dessus et dans le README.

## Vérifications faites

- **Recroisage indépendant** : le `dub_riddim.h` généré a été relu (parsing C) et comparé
  pas à pas à la grille de la page — les 27 riddims, les 4 pistes, notes **et** vélocités :
  tout concorde ; chaque événement de basse de la page est présent à son pas.
- **Compile C** : `gcc -fsyntax-only -Wall -Wextra` propre ; `sizeof DUB_RIDDIMS/…[0]` = 27.
- **Build complet** avec la toolchain JieLi (clang 4.0.1 pi32v2) : toutes les vérifications
  du build passent (`image 580 656 B`, accès registres, RAM) ; les noms de la nouvelle
  banque sont dans l'image, les anciens ont disparu.
- Le smoke test de l'émulateur (`reference_emu/wasm_smoke_test.js`) est mis à jour pour la
  banque de 27 (compte, noms, readback du chargeur) — il demande clang wasm32 pour tourner,
  absent de l'environnement de génération ; le paquet .fwsc ci-joint est le test réel.

## Reconstruire la banque / le firmware

```
python3 tools/gen_riddims_web.py        # réécrit firmware/src/dub_riddim.h depuis la grille
./build.sh                              # build dev (identité FM-1_900)
./build.sh --release 1.7                # build installable (identité FM-1_234)
```

La toolchain et l'SDK : voir BUILDING.md (`tools/get_toolchain.sh`, clone AC79
AC79NN_SDK_V1.2.1_2023-12-13).

## Ce qui a changé dans le dépôt

- `firmware/src/dub_riddim.h` — la banque (27 riddims, générée).
- `tools/gen_riddims_web.py` + `tools/riddims_db.js` — le nouveau générateur et la grille
  de la page (régénérable).
- `tools/gen_riddims.py` supprimé (l'ancienne banque n'existe plus ; l'historique git le
  garde) — `scripts/verify_sleng_bounce.js` aussi (il vérifiait la transcription 1.6 du
  Sleng Teng, retirée de la banque).
- `README.md`, `DUB-FR.md`, `firmware/src/dub.h` — les sections riddims réécrites
  (27, la Riddim Collection, la MT-40 garde ses 22 sons et son kit, son Rock est le
  SLENG TENG de la collection).
- `reference_emu/wasm_smoke_test.js` — les attentes du test mises à la banque de 27.
- `CHANGELOG.md` intact (l'historique des versions).
- `docs/firmware/sloop-dub-1.7.fwsc` **remplacé par le nouveau paquet** (même nom, même
  identité FM-1_234) : le lien de téléchargement du dépôt et l'installateur web servent la
  banque Riddim Collection — l'empreinte sha256 de l'installateur (`docs/webapp/installer/index.html`)
  et de DUB-FR.md est mise à jour, comme le descriptif `fmhub.json`.

Licence du firmware et de la banque : GPL-3.0 (la grille de la page Riddim Collection est
elle-même publiée GPL-3.0 par Altess Production — son en-tête d'export MIDI le porte).
