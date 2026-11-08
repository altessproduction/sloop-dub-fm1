# SLOOP Dub FM-1

Première base de firmware orientée reggae / dub pour le M-VAVE FM-1, dérivée de SLOOP et conservant sa licence GPL-3.0-only.

## État actuel

Le fork ajoute une extension DSP indépendante dans `firmware/src/dub.c` et `dub.h` :

- **Dub siren** : oscillateur audio avec LFO, profondeur et déclenchement de niveau.
- **Séquenceur dub** : stockage et lecture de 16, 32 ou 64 pas, avec note et vélocité par pas.
- **Skank à une touche** : triades majeures, mineures, diminuées et augmentées à partir d'une fondamentale.
- **Presets** : cinq points de départ (`ROOTS BASS`, `SKANK CHORD`, `DUB SIREN`, `STEPPERS`, `TAPE ECHO`).
- **DUB ISOLATOR** : quatre bandes `SUB`, `BASS`, `MIDS`, `TOPS`, croisements de séparation, gain, mute et correction paramétrique légère par bande.

Le module est inclus selon la convention SLOOP d'unité de compilation unique. Il est initialisé dans le démarrage de l'application et placé dans `mix_block`, après les effets wet et avant le master. Il reste **désactivé par défaut** (`dub_enabled = 0`) tant que les pages et raccourcis UI ne sont pas câblés ; cette décision évite de modifier le son existant de SLOOP dès le premier démarrage.

## Tests et prévisualisation navigateur

Le test sans matériel `tests/dub_test.c` couvre :

- les fréquences de croisement et les paramètres de l'isolateur ;
- le rendu stéréo de la sirène ;
- les longueurs 16/32/64 et le rejet d'une longueur invalide ;
- la construction d'un accord skank à une touche ;
- la présence de la banque de presets.

Il est complété par `tests/dub_emulator_test.py`, qui vérifie la page navigateur sur écrans mobile et bureau : grille 16/32/64, presets, sirène, skank, isolateur, transport, accessibilité des boutons et absence de défilement horizontal.

La prévisualisation SLOOP est construite en WebAssembly avec `python3 tools/build_preview.py`. Les douze moteurs de SLOOP sont comparés au rendu C natif par `tests/run_preview_tests.sh` ; la version initiale Dub a été vérifiée avec un écart nul entre les deux moteurs pour ces douze moteurs.

Pour lancer les contrôles locaux :

```sh
cc -std=c99 -Wall -Wextra -Werror -O2 tests/dub_test.c -o /tmp/dub_test
/tmp/dub_test
python3 tests/dub_emulator_test.py
python3 tools/build_preview.py
sh tests/run_preview_tests.sh
```

La compilation et l’installation sur le matériel FM-1 nécessitent toujours la toolchain JieLi et les fichiers SDK AC79 décrits dans `BUILDING.md`.

## Émulateur web

Une surface web jouable est publiée sous `docs/dub/` et déployée automatiquement sur GitHub Pages à chaque envoi vers `main`. Elle propose le séquenceur, les presets, le skank, la sirène et l’isolateur pour préparer le jeu et écouter une maquette navigateur.

Le moteur SLOOP/WASM est distribué avec la page pour les sons de base. Les commandes spécifiques Dub de cette première version sont actuellement prévisualisées par une couche audio navigateur : elles décrivent et testent l’interaction, mais ne constituent pas encore l’intégration complète des nouveaux paramètres dans le protocole, les pages de l’écran FM-1 et le format de projet.

## Installation de développement

1. Partir d'un checkout SLOOP compatible avec la cible FM-1.
2. Copier l'extension dans `firmware/src/` et ajouter les inclusions de `dub.h` / `dub.c` dans `felucca.c`.
3. Vérifier l'initialisation de `dub_isolator`, `dub_siren` et `dub_sequence` dans `felucca_init`.
4. Brancher les contrôles UI avec des valeurs bornées et conserver le bypass au démarrage.
5. Compiler le firmware JieLi, produire le paquet `.fwsc`, puis tester l'installation sur un FM-1 de développement avec une sauvegarde SLOOP disponible.

## Prochaine tranche recommandée

1. Ajouter une page UI `DUB` en réutilisant les couches SLOOP existantes : sirène, isolateur, longueur de séquence et preset.
2. Relier les événements de note et le tempo SLOOP à `dub_seq_advance`, au lieu de faire avancer le module indépendamment.
3. Remplacer progressivement le correcteur paramétrique simplifié par de vrais biquads Q15 par bande, après mesure du budget CPU sur les deux cœurs.
4. Ajouter la persistance projet seulement après stabilisation du format ; la première tranche ne modifie volontairement pas le format SLOOP.
5. Vérifier le coût DSP, les crêtes, le courant audio et l'absence de clics sur sirène, mute et changements de preset.

## Points techniques à surveiller

- Le FM-1 est une cible fixe-point 44,1 kHz avec un budget CPU et mémoire limité.
- L'isolateur actuel travaille en mono puis recopie le résultat gauche/droite ; il s'agit d'une première tranche robuste, pas encore d'un égaliseur paramétrique complet de qualité studio.
- Les filtres de séparation et les paramètres de gain doivent être testés avec le limiteur et les effets master de SLOOP avant activation permanente.
- Toute redistribution doit conserver les notices GPL et les crédits de SLOOP/Felucca.
