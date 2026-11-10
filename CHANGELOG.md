# CHANGELOG — SLOOP Dub FM-1

Le fil des versions du fork Dub. La base SLOOP et son histoire : [SLOOP.md](SLOOP.md)
et les [releases](https://github.com/isod89/sloop-fm1/releases) du dépôt d'origine.

## 1.0 — novembre 2026

La première version de partage : le firmware est prêt pour le test réel sur FM-1,
l'installateur web sert ce paquet, l'émulateur navigateur est reconstruit sur le même code.

**Les trois corrections des retours de test :**

- **L'ISO fonctionne.** Les coefficients du crossover étaient ~100 fois trop faibles
  (`hz * 2100 / FS` donne 4 sur 32767 à 90 Hz) : SUB, BASS et MIDS sortaient quasi muets
  et TOPS, le reste non filtré, portait tout le signal — un knob ou un mute ne faisait
  jamais que ce que fait TOPS. Reconstruit : une échelle de stages un pôle par canal,
  trois croisements à **90 Hz / 420 Hz / 2,6 kHz**, chaque croisement deux passe-bas et
  un passe-haut à **zéro vrai de DC** (aucune fuite de phase entre les bandes) ; **stéréo** ;
  les gains calculés une fois par bloc et glissés en ~12 ms (un mute ou un mouvement de
  knob ne clique jamais). Les champs d'égaliseur jamais accessibles quittent la structure.
- **TIME plie la boucle comme un vrai tape delay.** Tourner TIME avec une boucle qui
  tourne dans le delay **accélère ou ralentit la boucle en continu** (varispeed) : la tête
  de lecture marche à au plus la moitié de la vitesse de la bande, régulièrement à travers
  chaque bloc — le pliage tient tant que la tête avance (parcours complet ≈ 2,7 s, la
  tonalité monte en raccourcissant, descend en allongeant). Avant, le glissement
  `(cible − courant) >> 4` par bloc balayait la tête en ~12 ms — le saut entendu.
- **Les lignes suivent les knobs.** DLY LEVEL et SIREN LEVEL ne se redessinaient pas :
  leurs valeurs (`song.g[G_DMIX]`, `dub_menu_siren`, `song.g[G_BPM]`) manquaient à la
  signature de redraw du menu.

**Divers :**

- Version affichée sur la machine : **SLOOP DUB 1.0** (splash et ABOUT).
- Le dépôt devient la distribution : l'installateur web sert **sloop-dub-1.0.0.fwsc**, la
  page d'accueil GitHub explique le fork au-dessus des fonctions SLOOP, les outils de
  développement (tests hôtes, sources de l'éditeur web) sortent du checkout — ils restent
  dans l'historique git et chez le développeur.
- Empreinte mesurée (JieLi, ce dépôt) : **image flash 565 440 o / 581 052** (marge
  15 612 o), `.data`+`.bss` 57 608 o, `.lowram` 22 772 o, pool 328 396 o — le varispeed et
  l'isolateur coûtent ~400 o de flash et 8 o de RAM sur le 2.9.16.
- Tests : dub_test 200 contrôles (les bandes répondent vraiment, chaque mute coupe son
  sinus) ; ui_pages_test 513 ; stress_test 40 000 trames ; golden 182 rendus inchangés
  (DUB off passe bit à bit) ; smoke wasm AUDIO-PATH-OK avec la preuve des mutes sur le
  binaire réel.

## 2.9.16 — la sirène remappée, tenue à travers les pages

- **SIREN SEND** déménage sur **SIR** (K4), **SIREN LEVEL** sur **SR2** (K4) — le parcours
  de la sirène se lit d'un trait.
- **OCT+ tenu, la sirène suit la navigation** : SIR → SR2 → DLY la laissent hurler ;
  sur DLY, OCT+ n'a plus aucune autre fonction que la sirène.
- La console web disparaît sous l'émulateur : la faceplate et le menu du firmware sont les
  seuls contrôles, les fonctions du fork sont expliquées sous le visualiseur.
- Paquet : `sloop-dub-2.9.16.fwsc` (image 565 040 o, marge 16 012 o).

## 2.9.15 — le visualiseur réduit à WIRES

- L'appui bref sur HOME garde le seul style **WIRES** ; les onze autres, la FFT 512 points
  et leurs tampons sortent du firmware : 7 616 o de flash et ~7 Ko de RAM rendus
  (marge flash 8,3 → 15,9 Ko, pool 10,2 → 15,7 Ko).

## 2.9.1 → 2.9.14 — la naissance du module

- **2.9.1** la sirène NJD : cinq types de LFO, cinq waves, balayage exponentiel, envoi delay.
- **2.9.2** le séquenceur dub (quatre pistes, 16/32/64 pas) et les **dix riddims** de 64 pas.
- **2.9.3** les presets de sons dub par piste (basse, skank, mélodie, kits) — de vrais
  presets moteur SLOOP.
- **2.9.4 / 2.9.5** PLAY démarre et arrête le transport au menu ; le retour de chargement
  s'affiche dans le menu.
- **2.9.6** le chargement atterrit dans le séquenceur SLOOP lui-même — un seul séquenceur,
  éditable partout.
- **2.9.7** le filtre **bipolaire** de la page DUB, le **throw** vers le delay, et le
  **tape delay** (temps libre ou divisions, wow/flutter, saturation).
- **2.9.8** les knobs en **potentiomètres** (~300°) sur les pages Dub ; **OCT+ tenu sonne
  la sirène**, relâché elle s'arrête.
- **2.9.9** les pages **ACCENTS** et **SLIDES** — un second séquenceur sur les drapeaux.
- **2.9.10** **K1 seul** engage DUB : les knobs, chargements et la sirène restent hors du
  commutateur.
- **2.9.11** le **son intact au repos** (aucun filtre caché, bit à bit, stéréo comprise) ;
  SIREN LEVEL affiche toujours sa valeur et commande ; le DLY remappé (TIME / LEVEL /
  FEEDBK / MODE rond).
- **2.9.12** la page **SND** : un envoi delay par piste du séquenceur, sauvegardé au projet.
- **2.9.13** la **sirène indépendante** du module DUB : elle sonne DUB éteint et aucune
  bande de l'ISO ni le DUB FILTER ne la colore jamais.
- **2.9.14** `-Oz`, `--gc-sections`, `-fdata-sections` : la flash rentre à nouveau en
  gardant le logo graphique.

## 2.8.5 — la base

Le fork part de SLOOP 2.8.5 (les FM-1 à puce UC25HQ80 sauvegardent et se mettent à jour).
Tout SLOOP est dedans : trois synthés et une boîte à drums, douze moteurs, 153 sons,
37 kits, mode chanson, USB audio, MIDI — voir [SLOOP.md](SLOOP.md) et
[DEMARRAGE-RAPIDE-FR.md](DEMARRAGE-RAPIDE-FR.md).
