# SLOOP Dub FM-1

Première base de firmware orientée reggae / dub pour le M-VAVE FM-1, dérivée de SLOOP et conservant sa licence GPL-3.0-only.

## État actuel

Le fork ajoute une extension DSP indépendante dans `firmware/src/dub.c` et `dub.h` :

- **Dub siren** (2.9.1) : une vraie siren dub style NJD — oscillateur au choix (`SQR`, `PLS`, `SAW`, `TRI`, `SIN`), **balayage de pitch exponentiel** piloté par un LFO au choix (`WAIL` triangle, `HILO` deux tons, `RAMP` la charge du yelp, `SWEEP` la chute, `SPACE` l'échantillonneur glissé), symétrie du LFO, vitesse 1 à 16 Hz, profondeur 0 à 2 octaves, et **envoi vers le delay** du projet SLOOP.
- **Séquenceur dub** (2.9.2) : **quatre pistes** (basse, skanks, mélodie, drums) de 16, 32 ou 64 pas, note et vélocité par pas, jouées sur le transport (DUB ENABLE + PLAY) — basse et mélodie en legato, skanks en piqué d'accord, drums en notes General MIDI.
- **Riddims** (2.9.2) : dix séquences reggae dub de 64 pas × 4 pistes (`ONE DROP`, `STEPPERS`, `ROCKERS`, `DUBWALK`, `DIGITAL`, `LOVERS`, `MEDITATE`, `SKANKIN`, `DUB CUT`, `ZION`) sur la page RDM — KN1 sélectionne le riddim et OCT+ charge tout, KN2/KN3/KN4 + OCT+ chargent les motifs de basse, skank ou drum seuls dans les pistes du séquenceur. (2.9.6 : **le chargement atterrit dans le séquenceur SLOOP lui-même** — les pas des pistes 1–4, lisibles et éditables partout où SLOOP édite un pattern, voir « Le séquenceur dub ».)
- **PLAY au menu** (2.9.4) : **PLAY démarre et arrête le transport même menu ouvert** — avant, le menu avalait PLAY, si bien qu'un riddim chargé sur sa page ne pouvait pas se faire entendre ; le geste est maintenant CHARGER (OCT+ sur RDM) puis PLAY, sans quitter la page. **Le retour de chargement est visible au menu** (2.9.5) : `RIDDIM LOADED` / `BASS LOADED` / `SKANK LOADED` / `DRUM LOADED` clignote dans la barre du haut, sur l'écran d'accueil comme dans le menu.
- **Presets de sons dub** (2.9.3) : la page PRS charge un son par piste du riddim — **KN1 + OCT+** la basse (`SUB BASS`, `808 BOOM`, `FAT BASS`, `REESE`, `WOBBLE`, `ACID 303`, `CZ BASS`, `NES BASS`), **KN2 + OCT+** le skank (`DUB CHORD`, `MIN STAB`, `MIN7 STAB`, `REGGAE ORG`, `DIRTY B3`, `SOUL ORGAN`, `AFRO KEYS`, `CHIP CHORD`), **KN3 + OCT+** la mélodie (`PAN FLUTE`, `STEELPAN`, `STEEL DRUM`, `KALIMBA`, `SQR LEAD`, `SYNC LEAD`, `FAT LEAD`, `CZ LEAD`) et **KN4 + OCT+** le kit drum (`DEEP`, `DUST`, `VINTAGE`, `808`, `DUBSTEP`, `DEMBOW`, `AMAPIANO`, `AFRO`). Chaque son est un vrai preset moteur de SLOOP (changement de moteur puis preset, niveaux calibrés et patches FM6 compris) ; le kit s'écrit dans la piste de drums.
- **Filtre, envoi et tape delay** (2.9.7) : la page DUB remappe ses lignes — `DUB FILTER` le filtre **bipolaire** (à gauche le passe-bas, à droite le passe-haut, au centre le crantage : le signal intact), `DUB MIX` le mix, `DUB SEND` l'envoi vers le delay (le *throw*) ; la page DSEQ sort et **DLY** entre : le **tape delay** — temps libre en ms ou la synchro tempo, release des répétitions, division 1/4 … 1/16 pointées. Pendant DUB le bus delay tourne en bande magnétique : le temps glisse, la lecture ondule (wow 0,7 Hz, flutter 6,3 Hz), les répétitions passent une saturation douce ; DUB off, le delay tempo du SLOOP tel qu'il a toujours été.
- **Knobs potentiomètres et sirène momentanée** (2.9.8) : sur SIR, SR2, DUB, DLY et les bandes ISO, les knobs K1–K4 se comportent en **potentiomètres** — tout le parcours en moins d'un tour, ~300° (un cran = une part du parcours, sans accélération). Sur les pages SIR/SR2, **OCT+ tenu sonne la sirène** au niveau de la ligne SIREN LEVEL (2.9.11 : **ce que la ligne affiche commande** — 0 reste silencieux), **relâché elle s'arrête** — un tap ne déclenche plus les lignes (ce sont les knobs qui règlent) ; quitter la page tenue l'arrête aussi, et ailleurs OCT+ garde ses autres vies.
- **ACCENTS et SLIDES** (2.9.9) : deux pages de plus au bouton SEQ du séquenceur SLOOP — une **grille de pas sur les quatre pistes** (une rangée par piste B/S/M/D, seize pas par écran), un second séquenceur parallèle posé sur les drapeaux que les notes déclenchent déjà : **KN1** marche le pas, **KN2** saute la banque de 16, **ALGORITHM** (l'encodeur) change de piste, **OCT+ bascule le drapeau** au curseur. Un accent fait jouer le pas à 127 ; un slide fait **glisser la note vers la suivante** au lieu de la re-attaquer (un repos rompt la chaîne). La piste de drums montre ses hits en pointillés — ses niveaux restent sur sa grille DRUMS.
- **Le son intact au repos, le niveau qui commande, le delay remappé** (2.9.11) : **DUB n'ajoute plus aucun filtre invisible** — DUB FILTER sur FLAT et l'ISO au neutre, le son est **bit à bit celui de l'original**, stéréo comprise (le lisseur interne de l'isolateur, qui assombrissait le mix et le repliait en mono dès DUB allumé, ne touche plus jamais le signal : il ne sert qu'à façonner la courbe d'égaliseur quand on s'en sert). Les seuls colorants du son en DUB restent **l'ISO et le DUB FILTER**. Sur SIR/SR2, **SIREN LEVEL affiche toujours sa valeur** et **commande le volume** : 0 reste silencieux même OCT+ tenu, et le knob retient la sirène pendant qu'elle sonne. La page **DLY** se remappe : K2 `DLY LEVEL` (le niveau de l'écho dans le mix), K3 `DLY FEEDBK` (les répétitions), K4 `DLY MODE` (FREE et toutes les divisions sur un seul parcours).
- **L'envoi de chaque piste dans le delay** (2.9.12) : une page **SND** de plus après DLY — **un potentiomètre par piste du séquenceur** : K1 `BASS SEND` (piste 1), K2 `SKANK SEND` (piste 2), K3 `MELODY SEND` (piste 3), K4 `DRUM SEND` (la piste de drums, le réglage DLY de GLO > DRUMS). Tout le parcours en ~300°, la ligne affiche un pourcentage (0–100 %) et **DRY** à zéro ; **OCT+ bascule sec ↔ demi-envoi**. Le niveau d'envoi nourrit le même bus delay que le tape delay (et l'écho tempo quand DUB est off), il se sauvegarde avec le projet et joue aussitôt — le delay dubbed piste par piste, sans quitter le menu.
- **La sirène indépendante du module DUB** (2.9.13) : la sirène est **une voix à part entière** — elle sonne **même quand DUB est éteint** (OCT+ tenu sur SIR/SR2, la ligne SIREN LEVEL commande comme toujours), et **aucune bande de l'ISO ni le DUB FILTER ne la colore jamais**, DUB allumé ou non : dans la chaîne du master elle rend dans sa propre rangée et rejoint le mix **juste après le module DUB**, avant le filtre DJ du master (FILT) qui, lui, continue de la balayer. Son seul chemin vers le delay reste son propre **SIREN SEND** ; le throw de la page DUB (K4) n'envoie plus la sirène. Désactiver DUB (K1 sur la page DUB) ne coupe plus la sirène.
- **Skank à une touche** : huit accords (`MAJ`, `MIN`, `DIM`, `AUG`, `7TH`, `MIN7`, `9TH`, `PWR`), fondamentale chromatique, octave 3 à 5, vélocité réglable ; jusqu'à cinq notes (la 9TH).
- **Presets** : cinq points de départ (`ROOTS BASS`, `SKANK CHORD`, `DUB SIREN`, `STEPPERS`, `TAPE ECHO`).
- **DUB ISOLATOR** : quatre bandes `SUB`, `BASS`, `MIDS`, `TOPS`, croisements de séparation, gain, mute, correction paramétrique légère par bande et mix dry/wet. (2.9.11 : **au repos le module se retire** — tous les knobs au neutre, le signal d'origine passe bit à bit, stéréo comprise ; et l'égaliseur d'une bande ne filtre plus le son par-dessous, il pose sa courbe une seule fois.)

Le module est inclus selon la convention SLOOP d'unité de compilation unique. Il est initialisé dans le démarrage de l'application et placé dans `mix_block`, après les effets wet et avant le master. Il reste **désactivé par défaut** (`dub_enabled = 0`) jusqu'à activation par une page Dub ou par les contrôles firmware ; cette décision évite de modifier le son existant de SLOOP dès le premier démarrage. (2.9.13 : la sirène ne suit plus cette place — elle rend dans ses propres buffers et rejoint le mix après le module, si bien que ni l'ISO ni le DUB FILTER ne la traversent et qu'elle sonne DUB éteint comme allumé ; avec DUB off le chemin du mix reste **bit à bit celui d'origine**, les tests golden le confirment.)

## Les pages Dub du menu (appui long sur HOME)

Le menu ouvert en maintenant **HOME** compte quatorze pages, une par fonction Dub après les cinq pages SLOOP (`SCR`, `LGT`, `AUD`, `SEQ`, `SYS`) ; le bandeau d'onglets montre cinq pages autour de la courante (`< SYS DUB SIR SR2 SKK >`) et `SELECT` passe de l'une à l'autre. Chaque page a ses lignes réglées par `KNOB 1..4`, `OCT+` valide, joue ou bascule, `OCT-` ferme le menu :

- **DUB** : `DUB ENABLE`, `DUB FILTER` (2.9.7 : le filtre **bipolaire** — à gauche le passe-bas, à droite le passe-haut, au centre le crantage : le signal intact), `DUB MIX` (0 sec … 127 wet, OCT+ coupe), `DUB SEND` (2.9.7 : l'envoi vers le delay, le *throw*), `DUB PRESET` (OCT+ applique). (2.9.8 : chaque parcours de knob tient en ~300°.)
- **SIR** : `SIREN TYPE` (WAIL HILO RAMP SWEEP SPACE), `SIREN WAVE` (SQR PLS SAW TRI SIN), `SIREN PITCH` (220–1200 Hz, OCT+ remet 740), `SIREN LEVEL` (0–127, **la valeur affichée est le niveau** — 0 silencieux ; OCT+ bascule 0/88). (2.9.8 : parcours de knob ~300° ; **OCT+ tenu sonne la sirène** au niveau réglé, **relâché elle s'arrête** ; 2.9.11 : le knob retient la sirène pendant qu'elle sonne ; 2.9.13 : **elle sonne même DUB éteint** et ne passe par aucun filtre du module.)
- **SR2** : `SIREN RATE` (1 à 16 Hz, OCT+ remet 2 Hz), `SIREN DEPTH` (le balayage, 0 à 2 octaves, OCT+ remet 96), `SIREN SYM` (la symétrie du LFO, OCT+ remet 64), `SIREN SEND` (l'envoi delay, OCT+ bascule 0/48). (2.9.8 : parcours ~300° ; OCT+ tenu sonne aussi ici.)
- **SKANK** : `SKANK CHORD` (les huit accords), `SKANK ROOT` (chromatique), `SKANK OCT` (3 à 5), `SKANK VEL` ; **OCT+ sur n'importe quelle ligne joue l'accord** sur la piste 1. Ce sont ces réglages que la piste skank d'un riddim utilise pour sonner.
- **DLY** (2.9.7, à la place de DSEQ — l'édition des pas vit dans les pages PATTERN / NOTES du SLOOP et à la console web) : le **tape delay** du module. (2.9.11 : les lignes remappées) — `DLY TIME` (le temps libre 40–1400 ms quand le mode est FREE, sinon le temps de la division s'affiche en grisé), `DLY LEVEL` (le niveau de l'écho dans le mix, le MIX du projet, 0–127 — OCT+ remet 90), `DLY FEEDBK` (le retour des répétitions, 0–120 — OCT+ remet 60), `DLY MODE` (la gamme ronde : **FREE**, puis 1/4, 1/8, 1/16, 1/32, 8T, 16T, 1/8D, 1/16D, 1/4D — OCT+ bascule FREE ↔ la dernière division). (2.9.8 : parcours ~300°.)
- **SND** (2.9.12) : l'envoi de chaque piste du séquenceur dans le delay — `BASS SEND` (K1, piste 1), `SKANK SEND` (K2, piste 2), `MELODY SEND` (K3, piste 3), `DRUM SEND` (K4, la piste de drums : le DLY de GLO > DRUMS). Un **potentiomètre** par piste (~300°, 0–100 %), la ligne affiche le pourcentage et **DRY** à zéro, OCT+ bascule sec ↔ demi-envoi. L'envoi se sauvegarde dans le projet et nourrit le bus delay aussitôt — tape delay quand DUB joue, écho tempo sinon.
- **RDM** : la banque de riddims (2.9.2). `RIDDIM` (`KN1` sélectionne parmi les dix, **OCT+ charge les quatre pistes entières**), `BASS PATTERN` (`KN2` + **OCT+ charge la ligne de basse seule**, piste 1), `SKANK PATTERN` (`KN3` + **OCT+ les skanks seuls**, piste 2), `DRUM PATTERN` (`KN4` + **OCT+ les drums seuls**, piste 4). Mélanger basse d'un riddim et drums d'un autre est le geste classique du sound system. (2.9.4 : **PLAY démarre le transport depuis n'importe quelle page du menu**.) (2.9.5 : **chaque chargement s'affiche dans le menu** — la barre du haut remplace `MENU` par `RIDDIM LOADED`, `BASS LOADED`, `SKANK LOADED` ou `DRUM LOADED` pendant une seconde ; avant, le message ne vivait que sur l'écran d'accueil, masqué par le menu, et un OCT+ réussi semblait ne rien faire.)
- **PRS** : les presets de sons dub par piste (2.9.3) : `BASS PRESET` (`KN1` + OCT+ charge dans la piste 1), `SKANK PRESET` (`KN2` + OCT+, piste 2), `MELODY PRESET` (`KN3` + OCT+, piste 3), `DRUM KIT` (`KN4` + OCT+, le kit de la piste de drums).
- **ISO** : `SUB`, `BASS`, `MIDS`, `TOPS` (gain ; **OCT+ mute la bande**, le gain est gardé).

### Le séquenceur dub et les dix riddims

Le chargement d'un riddim (2.9.6, `dub_tracks_load`) écrit **dans le séquenceur SLOOP lui-même** : les pistes 1–4 (basse, skanks, mélodie, drums) reçoivent les 64 pas du riddim dans leurs vrais pas (`step[]` / `dstep[]`), leur LEN passe à 64, et le séquenceur parallèle du dub disparaît — **un seul séquenceur** : ce qui charge est ce qui joue et ce qui s'édite ensuite. La ligne de basse et la mélodie tiennent leur note sur les pas suivants : le maintien devient des pas TIE (pointillés sur la console web, éditables comme les autres). Un skank pique son accord d'une double-croche, construit avec la qualité et l'octave de la page SKANK ; les notes General MIDI des drums (36 kick, 38 caisse claire, 39 clap, 42 charley fermé, 46 ouvert) vont chacune dans sa lane de la piste de drums, la vélocité dans le niveau du hit. Après OCT+, tout se joue et s'édite comme un pattern SLOOP normal : touches SEQ, pages PATTERN et NOTES, couche SEQ, sons des pistes au choix habituel. Le transport fait tourner le tout, calé sur le tempo du projet. Les pages **ACCENTS** et **SLIDES** (2.9.9) s'ajoutent à la marche SEQ (NOTES → PATTERN → ACCENTS → SLIDES) : la grille des quatre pistes y pose les accents (le pas joue à 127) et les slides (la note glisse vers la suivante au lieu de re-attaquer ; un repos rompt la chaîne) — sur un riddim chargé comme sur n'importe quel pattern, et les drapeaux suivent le pattern dans le projet sauvegardé.

Les dix riddims (`tools/gen_riddims.py` → `firmware/src/dub_riddim.h`, ~5 Ko en ROM) : `ONE DROP` 72 bpm, `STEPPERS` 76, `ROCKERS` 80, `DUBWALK` 70, `DIGITAL` 92, `LOVERS` 84, `MEDITATE` 66, `SKANKIN` 88, `DUB CUT` 74, `ZION` 68 — chacun sa progression (Am, Dm, F, G…), son groove de basse (syncopé une-drop, croches steppers, marche dub…), ses skanks (contretemps, temps 2-4, poussés) et son pattern de drums (one-drop, steppers, rockers, digital). Réglez le BPM du projet sur le tempo du riddim pour le feel juste.

Côté console web (2.9.6) : l'onglet **DSQ** montre **les pistes du séquenceur SLOOP** (quatre pistes × 64 pas, relecture `emu_dub_seq_len` / `emu_dub_seq_note` / `emu_dub_seq_pos` / `emu_dub_seq_playing`) — ce qu'un OCT+ (page RDM du firmware ou boutons CHARGER de l'onglet RDM) a chargé **dans les pistes** s'affiche tel quel, chaque piste suit son propre LEN, la colonne claire est la tête de lecture pendant PLAY, la piste choisie (BASS SKNK MEL DRUM) s'édite au clic (les pas tenus TIE se dessinent en pointillé) ; l'onglet RDM affiche `CHARGÉ · <nom>` après chaque chargement.

Côté DSP, les réglages vivent dans `dub_siren_t` (`freq_hz`, `depth`, `rate`, `type`, `wave`, `sym`, `send`, avec `dub_siren_set_freq` / `set_rate` / `set_type` / `set_wave` / `set_sym` / `set_send` bornés) et la table `DUB_SKANK_NAMES` de `dub.h` ; l'émulateur et l'éditeur web passent par les mêmes points d'entrée. Le rendu de la sirène a déménagé dans `mix_block` : il arrive **avant** `fx_buses`, si bien que la part `SIREN SEND` entre dans le bus delay réel de SLOOP (`acc[0].sd`) et ressort dans l'écho du projet ; l'isolateur, lui, reste après les buses, avant le master. Le niveau est à pente douce (`level_cur`) : les déclenchements et les coupures ne cliquent pas.

## Tests et prévisualisation navigateur

Le test sans matériel `tests/dub_test.c` couvre :

- les fréquences de croisement et les paramètres de l'isolateur, le mix à sec ;
- les bornes de la sirène (220 / 1 200 Hz, rate 1 à 16 Hz, type/wave/sym/send bornés), son rendu stéréo borné, les cinq courbes de LFO et les cinq courbes d'oscillateur, et l'envoi delay (le bus se remplit, se vide à sec) ;
- les longueurs 16/32/64 et le rejet d'une longueur invalide ;
- la banque de riddims (2.9.2) : dix séquences nommées, chaque note/velocité dans les bornes, chaque piste a de la musique, `dub_riddim_load` copie les quatre pistes entières (64 pas, tête à 0), `dub_riddim_load_track` ne touche que sa piste, `dub_seq_set_step` ignore une piste invalide et fait d'une note > 127 un repos ;
- les banques de sons dub (2.9.3) : huit par rôle, nommés et distincts, les kits dans la liste des kits.
- les huit accords skank à une touche, leur troncature et leur rebouclage ;
- la présence de la banque de presets.

La suite UI complète `tests/ui_pages_test.c` parcourt les treize pages du menu sur le firmware réel hébergé : les huit pages Dub (réglages, OCT+ et chargements RDM/PRS — chaque son dub y est vérifié comme un vrai preset moteur, et OCT+ bascule le moteur et le preset de la piste), la fenêtre d'onglets et la fin de course de `SELECT`, puis 20 000 trames d'usage aléatoire. Il est complété par `tests/dub_emulator_test.py`, qui vérifie la page navigateur sur écrans mobile et bureau : onglets de la console Dub (DUB/SIR/SR2/SKANK/DSEQ/RDM/ISO) avec les sélecteurs et chargements de riddims, la vue séquenceur quatre pistes (2.9.4), presets, sirène, skank, isolateur, transport, accessibilité des boutons et absence de défilement horizontal. `tests/menu_navigation_test.py` fait la même marche des pages dans l'émulateur, `tests/riddim_test.py` rejoue le scénario complet du 2.9.4 (chargement RDM → relecture DSQ → **PLAY au menu qui sonne le riddim** → motifs recombinés → OCT+ firmware → LEN 64) et `tests/public_menu_check.py` refait la marche sur le site publié après déploiement. `reference_emu/wasm_smoke_test.js` vérifie enfin le binaire seul : exports, banque de riddims (les dix noms lus dans la mémoire WASM), chargements, et **la lecture réelle sur transport** — RMS au repos, en lecture, à l'arrêt.

Pour lancer les contrôles locaux :

```sh
cc -std=c99 -Wall -Wextra -Werror -O2 tests/dub_test.c -o /tmp/dub_test
/tmp/dub_test
python3 tests/dub_emulator_test.py
python3 tests/menu_navigation_test.py
```

La compilation et l’installation sur le matériel FM-1 nécessitent toujours la toolchain JieLi et les fichiers SDK AC79 décrits dans `BUILDING.md`.

## Émulateur web

Une surface web jouable est publiée sous `docs/dub/` et déployée automatiquement sur GitHub Pages à chaque envoi vers `main`. Sa console Dub est le **miroir des pages du menu** : dix onglets (`DUB`, `SIR`, `SR2`, `SKANK`, `DLY`, `SND`, `SEQ`, `RDM`, `PRS`, `ISO`), les mêmes réglages que l'écran LCD — type et courbe de la sirène, pitch, niveau, vitesse, profondeur, symétrie et envoi delay, les huit accords skank avec fondamentale, octave et vélocité, le mix de l'isolateur, la grille de séquence, les presets, **l'onglet RDM** (les dix riddims, chargements tout/basse/skank/drum), **l'onglet PRS** (les sons de basse, skank, mélodie et les kits, chargés par piste) et **l'onglet SND** (l'envoi delay des quatre pistes du séquenceur, 2.9.12) — le tout par les mêmes exports WASM que le matériel. Chargez un riddim, un son par piste, puis appuyez sur **PLAY** de l'émulateur : le riddim joue avec les sons choisis.

Le moteur SLOOP/WASM est distribué avec la page et exécute le mixage firmware dans un `AudioWorklet` séparé. La page envoie l'état SLOOP, le transport, les notes, la sirène (niveau, pitch, profondeur, vitesse, type, courbe, symétrie, envoi), le mix, les bandes de l'isolateur et le skank à l'adaptateur firmware. `docs/dub/sloop.wasm` est compilé depuis ce dépôt et expose déjà les exports dédiés (`emu_dub_siren_type`, `_wave`, `_sym`, `_send`, `_level`, `_freq`, `_depth`, `emu_dub_siren_rate`, `emu_dub_mix`) : le `worklet.js` les détecte au chargement, donc un ancien binaire reste aussi supporté (les réglages correspondants y sont alors sans effet).

Un test de fumée du binaire vérifie le chemin audio complet (note sèche, note sous isolateur plein mix, sirène seule) sans navigateur :

```sh
node reference_emu/wasm_smoke_test.js            # test reference_emu/dist/sloop.wasm
node reference_emu/wasm_smoke_test.js docs/dub/sloop.wasm
```

**Reconstruire le WASM** (clang + lld wasm32, pas besoin d'emscripten — déjà fait pour `docs/dub/sloop.wasm`, à refaire après toute modification du C) :

```sh
python3 tools/gen_tables.py build/gen/felucca_tables.h
python3 tools/gen_samples.py build/gen/felucca_samples.h
python3 tools/gen_drumkits.py build/gen/felucca_drumkits.h
python3 tools/gen_fm6_patches.py build/gen/felucca_fm6.h
python3 tools/gen_font.py build/gen/felucca_font.h
python3 tools/gen_icons.py build/gen/felucca_icons.h
python3 tools/gen_logo.py build/gen/sloop_logo.h
sh reference_emu/build.sh      # compile sloop.wasm et rafraîchit docs/dub/
```

Cette prévisualisation reste un adaptateur navigateur : elle ne remplace pas encore le flashage du FM-1, n'émule pas les entrées/sorties matérielles et ne persiste pas encore les nouveaux paramètres Dub dans le format de projet SLOOP.

## Installation de développement

1. Partir d'un checkout SLOOP compatible avec la cible FM-1.
2. Copier l'extension dans `firmware/src/` et ajouter les inclusions de `dub.h` / `dub.c` dans `felucca.c`.
3. Vérifier l'initialisation de `dub_isolator`, `dub_siren` et `dub_sequence` dans `felucca_init`.
4. Brancher les contrôles UI avec des valeurs bornées et conserver le bypass au démarrage.
5. Compiler le firmware JieLi, produire le paquet `.fwsc`, puis tester l'installation sur un FM-1 de développement avec une sauvegarde SLOOP disponible.

## Prochaine tranche recommandée

1. ~~Reconstruire `docs/dub/sloop.wasm`~~ **fait** : le binaire est compilé depuis ce dépôt (clang 18 wasm32) et validé par `wasm_smoke_test.js` plus les tests navigateur.
2. Relier les événements de note et le tempo SLOOP à `dub_seq_advance`, au lieu de faire avancer le module indépendamment.
3. Remplacer progressivement le correcteur paramétrique simplifié par de vrais biquads Q15 par bande, après mesure du budget CPU sur les deux cœurs.
4. Ajouter la persistance projet seulement après stabilisation du format ; la tranche actuelle ne modifie volontairement pas le format SLOOP.
5. Vérifier le coût DSP, les crêtes, le courant audio et l'absence de clics sur sirène, mute et changements de preset.

## Points techniques à surveiller

- Le FM-1 est une cible fixe-point 44,1 kHz avec un budget CPU et mémoire limité.
- L'isolateur actuel travaille en mono puis recopie le résultat gauche/droite ; il s'agit d'une première tranche robuste, pas encore d'un égaliseur paramétrique complet de qualité studio.
- Les filtres de séparation et les paramètres de gain doivent être testés avec le limiteur et les effets master de SLOOP avant activation permanente.
- Toute redistribution doit conserver les notices GPL et les crédits de SLOOP/Felucca.
