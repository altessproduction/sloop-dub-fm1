# SLOOP Dub FM-1

Première base de firmware orientée reggae / dub pour le M-VAVE FM-1, dérivée de SLOOP et conservant sa licence GPL-3.0-only.

## État actuel

Le fork ajoute une extension DSP indépendante dans `firmware/src/dub.c` et `dub.h` :

- **Dub siren** (2.9.1) : une vraie siren dub style NJD — oscillateur au choix (`SQR`, `PLS`, `SAW`, `TRI`, `SIN`), **balayage de pitch exponentiel** piloté par un LFO au choix (`WAIL` triangle, `HILO` deux tons, `RAMP` la charge du yelp, `SWEEP` la chute, `SPACE` l'échantillonneur glissé), symétrie du LFO, vitesse 1 à 16 Hz, profondeur 0 à 2 octaves, et **envoi vers le delay** du projet SLOOP.
- **Séquenceur dub** : stockage et lecture de 16, 32 ou 64 pas, avec note et vélocité par pas.
- **Skank à une touche** : huit accords (`MAJ`, `MIN`, `DIM`, `AUG`, `7TH`, `MIN7`, `9TH`, `PWR`), fondamentale chromatique, octave 3 à 5, vélocité réglable ; jusqu'à cinq notes (la 9TH).
- **Presets** : cinq points de départ (`ROOTS BASS`, `SKANK CHORD`, `DUB SIREN`, `STEPPERS`, `TAPE ECHO`).
- **DUB ISOLATOR** : quatre bandes `SUB`, `BASS`, `MIDS`, `TOPS`, croisements de séparation, gain, mute, correction paramétrique légère par bande et mix dry/wet.

Le module est inclus selon la convention SLOOP d'unité de compilation unique. Il est initialisé dans le démarrage de l'application et placé dans `mix_block`, après les effets wet et avant le master. Il reste **désactivé par défaut** (`dub_enabled = 0`) jusqu'à activation par une page Dub ou par les contrôles firmware ; cette décision évite de modifier le son existant de SLOOP dès le premier démarrage.

## Les pages Dub du menu (appui long sur HOME)

Le menu ouvert en maintenant **HOME** compte onze pages, une par fonction Dub après les cinq pages SLOOP (`SCR`, `LGT`, `AUD`, `SEQ`, `SYS`) ; le bandeau d'onglets montre cinq pages autour de la courante (`< SYS DUB SIR SR2 SKK >`) et `SELECT` passe de l'une à l'autre. Chaque page a ses lignes réglées par `KNOB 1..4`, `OCT+` valide, joue ou bascule, `OCT-` ferme le menu :

- **DUB** : `DUB ENABLE`, `DUB PRESET` (OCT+ applique), `DUB MIX` (0 sec … 127 wet, OCT+ coupe).
- **SIR** : `SIREN TYPE` (WAIL HILO RAMP SWEEP SPACE ; OCT+ sonorise), `SIREN WAVE` (SQR PLS SAW TRI SIN ; OCT+ sonorise), `SIREN PITCH` (2 Hz par cran, OCT+ remet 740), `SIREN LEVEL` (OCT+ on/off).
- **SR2** : `SIREN RATE` (1 à 16 Hz, OCT+ remet 2 Hz), `SIREN DEPTH` (le balayage, 0 à 2 octaves, OCT+ remet 96), `SIREN SYM` (la symétrie du LFO, OCT+ remet 64), `SIREN SEND` (l'envoi delay, OCT+ bascule 0/48).
- **SKANK** : `SKANK CHORD` (les huit accords), `SKANK ROOT` (chromatique), `SKANK OCT` (3 à 5), `SKANK VEL` ; **OCT+ sur n'importe quelle ligne joue l'accord** sur la piste 1.
- **DSEQ** : `SEQ LENGTH`, `SEQ STEP`, `SEQ NOTE`, `SEQ VELOCITY`.
- **ISO** : `SUB`, `BASS`, `MIDS`, `TOPS` (gain ; **OCT+ mute la bande**, le gain est gardé).

Côté DSP, les réglages vivent dans `dub_siren_t` (`freq_hz`, `depth`, `rate`, `type`, `wave`, `sym`, `send`, avec `dub_siren_set_freq` / `set_rate` / `set_type` / `set_wave` / `set_sym` / `set_send` bornés) et la table `DUB_SKANK_NAMES` de `dub.h` ; l'émulateur et l'éditeur web passent par les mêmes points d'entrée. Le rendu de la sirène a déménagé dans `mix_block` : il arrive **avant** `fx_buses`, si bien que la part `SIREN SEND` entre dans le bus delay réel de SLOOP (`acc[0].sd`) et ressort dans l'écho du projet ; l'isolateur, lui, reste après les buses, avant le master. Le niveau est à pente douce (`level_cur`) : les déclenchements et les coupures ne cliquent pas.

## Tests et prévisualisation navigateur

Le test sans matériel `tests/dub_test.c` couvre :

- les fréquences de croisement et les paramètres de l'isolateur, le mix à sec ;
- les bornes de la sirène (220 / 1 200 Hz, rate 1 à 16 Hz, type/wave/sym/send bornés), son rendu stéréo borné, les cinq courbes de LFO et les cinq courbes d'oscillateur, et l'envoi delay (le bus se remplit, se vide à sec) ;
- les longueurs 16/32/64 et le rejet d'une longueur invalide ;
- les huit accords skank à une touche, leur troncature et leur rebouclage ;
- la présence de la banque de presets.

La suite UI complète `tests/ui_pages_test.c` parcourt les onze pages du menu sur le firmware réel hébergé : les six pages Dub (réglages, OCT+, navigation), la fenêtre d'onglets et la fin de course de `SELECT`, puis 20 000 trames d'usage aléatoire. Il est complété par `tests/dub_emulator_test.py`, qui vérifie la page navigateur sur écrans mobile et bureau : onglets de la console Dub (DUB/SIR/SR2/SKANK/DSEQ/ISO), grille 16/32/64, presets, sirène, skank, isolateur, transport, accessibilité des boutons et absence de défilement horizontal. `tests/menu_navigation_test.py` fait la même marche des pages dans l'émulateur, et `tests/public_menu_check.py` la refait sur le site publié après déploiement.

Pour lancer les contrôles locaux :

```sh
cc -std=c99 -Wall -Wextra -Werror -O2 tests/dub_test.c -o /tmp/dub_test
/tmp/dub_test
python3 tests/dub_emulator_test.py
python3 tests/menu_navigation_test.py
```

La compilation et l’installation sur le matériel FM-1 nécessitent toujours la toolchain JieLi et les fichiers SDK AC79 décrits dans `BUILDING.md`.

## Émulateur web

Une surface web jouable est publiée sous `docs/dub/` et déployée automatiquement sur GitHub Pages à chaque envoi vers `main`. Sa console Dub est le **miroir des pages du menu** : six onglets (`DUB`, `SIR`, `SR2`, `SKANK`, `DSEQ`, `ISO`), les mêmes réglages que l'écran LCD — type et courbe de la sirène, pitch, niveau, vitesse, profondeur, symétrie et envoi delay, les huit accords skank avec fondamentale, octave et vélocité, le mix de l'isolateur, la grille de séquence et les presets.

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
