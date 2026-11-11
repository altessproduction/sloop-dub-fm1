# CHANGELOG — SLOOP Dub FM-1

Le fil des versions du fork Dub. La base SLOOP et son histoire : [SLOOP.md](SLOOP.md)
et les [releases](https://github.com/isod89/sloop-fm1/releases) du dépôt d'origine.

## 1.3 — novembre 2026

**Les riddims suivent le sound system.** La banque passe de dix à **vingt-deux
riddims** de 64 pas × 4 pistes (`tools/gen_riddims.py` → `dub_riddim.h`, ~11 Ko en
ROM), organisée par genre — chaque riddim apporte ses **quatre patterns associés**
(ligne de basse, skanks, mélodie, drums), chargeables séparément sur la page RDM.

- **Ska** : `SKA` 88 bpm (la marche de basse en noires, le rim sec sur les
  contretemps), `TWO TONE` 92 (les pompes d'octaves), `ROCKSTDY` 76 (le rebond).
- **Dancehall** : `DANCEHALL` 95 (le clap 3+3+2, les stabs poussés, la fanfare),
  `DEMBOW` 100 (le boom-ch-boom-chick strict, la sub qui répond).
- **Bass music UK** : `UK STEPPA` 84 (le kick au temps, le drone, les rims),
  `DNB STEP` 174 (le two-step, les ghost snares, la sub qui roule), `JUNGLE` 172
  (le break haché et ses ghosts, la sub qui répond), `RAGGA JGL` 170 (break +
  clap ragga, stabs fanfare), `DUBSTEP` 140 (le half-time, la sub wobblée, une
  seule stab sombre), `UK 2STEP` 134 (la syncope garage), `BASSLINE` 132 (le
  kick au temps, la basse en contretemps, les claps décalés).
- **Les dix riddims reggae / dub d'origine jouent enfin leur groove entier** :
  la tenue à une note par pas du séquenceur faisait qu'un kick posé sur le pas
  d'une snare (ou d'un charley) était écrasé par elle — le one-drop n'avait
  **aucun kick** (la snare gagnait le pas 8), le steppers perdait la moitié de
  son four-on-the-floor, le meditate ne sonnait que ses charleys. Corrigé dans
  le générateur : le one-drop pose son kick une double-croche avant sa snare
  (le pickup des roots), le steppers emporte son kick aux quatre temps, le
  meditate redevient un vrai one-drop ; `check_bank()` refuse désormais tout
  hit écrasé (vérification AST des `D(...)` du générateur).
- Le drum track note ses hits en General MIDI : 36 kick, 37 rim, 38 caisse
  claire (les ghosts à faible vélocité), 39 clap, 42 charley fermé, 46 ouvert.
- Docs suivent (DUB-FR.md, README.md, la page de l'émulateur web) avec le
  tempo conseillé de chaque riddim.
- **Le site suit la banque jusqu'au dernier nom** : les deux pages de l'éditeur
  web (`index.html` servi en ligne et `sloop-editor.html` hors-ligne) servent
  les 154 presets des douze moteurs, les 32 kits synthétisés et l'enum KIT des
  37 kits — `update_editor_presets.py` et `update_editor_kits.py` synchronisent
  maintenant les deux pages ; les exemples (slots démo, mock, tuto, PRS) citent
  les sons nouveaux. Les deux wasm (émulateur `docs/dub/sloop.wasm` et aperçu
  `sloop-preview.wasm`) sont recompilés depuis ces sources — l'ancienne banque
  d'origine n'y vit plus ; `wasm_smoke_test.js` attend les 22 riddims et les
  listes PRS nouvelles (bass 10, skanks / mélodie / kits 8) et passe.
  `build.sh` accepte un autre driver wasm32 (`CC=`/`CFLAGS=`).

## 1.2 — novembre 2026

**Les kits de batterie suivent la banque sound-system.** 37 kits toujours, mais
orientés genre, tous recalibrés (`tests/drum_level.c` + `tools/level_drumkits.py`).

- **Les 5 kits échantillonnés** (la batterie acoustique CC0 et ses traitements)
  deviennent **ONE DROP, STEPPERS, SKA, ROCKERS et DUB** : le traitement par lane
  est maintenant une table (`DK_SHIFT`/`DK_DEC` dans drums.c) — chaque son pitché
  et fondé vers le jeu du style (le rimshot devant au one drop, le kick profond
  au steppers, le rim sec et présent au ska…), le TUNE / DECAY du drum track
  (2.7) s'ajoute par-dessus et reste prioritaire.
- **9 kits synthétisés sont reconstruits** (`tools/gen_drumkits.py`) aux places
  des moins utiles au fork : ONEDROP, ROCKERS, ROCKSTDY, SKA, DIGITAL (le reggae
  numérique), RUBADUB (la drumbox rub-a-dub, un léger crush), RAGGA (crush 0x22),
  GQOM et STEPPERS. JUNGLE, DUBSTEP, GARAGE, DEMBOW, TRAP, DRILL, AMAPIANO, AFRO
  et les machines 808 / 909 / 606 / VINTAGE restent.
- **Le menu PRS du module dub suit** (dub.c) : ONE DROP, STEPPERS, VINTAGE, 808,
  JUNGLE, DUBSTEP, RAGGA, DEMBOW.
- **L'éditeur web est synchronisé** (`scripts/update_editor_kits.py` régénère
  DSYN_MOCK_NAMES / DSYN_MOCK_KITS et la liste KIT de sloop-editor.html depuis
  le header généré).
- Le kit au démarrage d'un projet neuf : ONE DROP (la batterie échantillonnée).

## 1.1 — novembre 2026

**La banque de sons d'usine est refondue pour le sound system.** Les 158 presets
(13 moteurs, SLICE compris) remplacent la banque d'origine : reggae, roots, ska, dub,
drum & bass, jungle, ragga jungle, dubstep, UK steppers, bass music. Chaque moteur a
sa banque redessinée paramètre par paramètre, et tous les niveaux sont recalibrés
(`tools/level_presets.py`, cible −15 LUFS, trois passes).

- **Les basses de chaque genre** (ANALOG, DIGITAL, FM6, CZ, CHIP, SAMPLE, VOICE, TRIO,
  PHYS) : les subs reggae et steppers, les 808 qui glissent (ROOTS 808, RAGGA 808),
  le Reese et le roller DnB, les wobbles et growls dubstep, la basse UK garage.
- **Le comping** : SKANK ORGN et les orgues de la banque WHEEL, BUBBLE ORG (TRIO),
  les EP skank FM et CZ, SKANK PNO, les guitares du skank en modélisation physique
  (SKANK GTR, UPSTROKE, SKA GTR).
- **Les stabs d'un doigt** (TRIO) : STEPPA STB, ROOTS STB, SKA STAB, TWO TONE,
  RAGGA STB, DNB STAB, JUNGLE STB, DUBSTEP STB — DUB CHORD reste, comme REGGAE ORG.
- **Les sirens et FX du sound system** (NOISE) : DUB SIREN et SIREN 2 (le registre LFSR
  pitché, le LFO le fait pleurer), AIR HORN, la pluie de vinyle et de bande.
- **Les breaks** (SLICE) : AMEN CUT, JUNGLE 16, RAGGA CUT sur le break intégré.
- **Les 8 patchs FM6 d'usine sont réécrits** (`tools/gen_fm6_patches.py`) : SKANK,
  DUB KEYS, FM SUB, GROWL, STEPPA, BELL, HORNS, MELODI — la mélodica du dubpoète.
- **La banque PRS du module dub suit** (dub.c) : les trois listes basse / skank /
  mélodie pointent sur les nouveaux presets (nom + index vérifiés).
- **L'éditeur web est synchronisé** (scripts/update_editor_presets.py régénère les
  blocs `presets:` et `FACTORY_PK` de sloop-editor.html depuis les tables C).
- Les sons de démarrage d'un projet neuf : SKANK SUB (piste 1), DX SKANK (piste 2),
  DUB FLUTE (piste 3).
- `tests/preset_level.c` du dépôt amont revient dans le fork avec les rôles de mesure
  de la banque sound-system (stabs d'un doigt, basses, beds tenus, comping, mélodie) ;
  les pages de test restent hors du firmware.

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
- Identité de paquet : **FM-1_234**, propre au fork et stable d'une version à l'autre —
  le schéma hérité `FM-1_9XY` donnait `FM-1_910` en 1.0, un numéro déjà pris sur
  thefirmwarehub.com par Felucca et trois autres forks. L'installateur web vérifie la
  nouvelle identité et le sha256 du paquet reconstruit ; le chargeur de mise à jour
  reste celui de Felucca (`ota-FM-1_900`, reconnu tel quel).
- Licences du Hip-Hop Pack : `LICENSING.md` porte le nom du fork et déclare le pack —
  CC0 partout, l'E.PIANO CC BY 3.0 (Greg Sullivan) — dans sa table tierce-partie et une
  section « sloop-DUB additions ».
- **L'identité.** La tour sound-system remplace la voile partout : la carte du hub, la bannière
  du dépôt (README, SLOOP, GUIDE, DÉMARRAGE RAPIDE), les icônes PWA — 192/512/maskable, plus
  celles (manquantes) de l'émulateur dub et les apple-touch-icon —, l'installateur et l'éditeur
  web, et le **splash d'allumage** : le même dessin quantifié en 16 couleurs RLE sur l'écran du
  FM-1 (9 056 o contre 4 635). Les SVG de la voile sortent du dépôt ; le service worker retrouve
  le bon nom de paquet (`sloop-dub-1.0.0.fwsc`) et un nouveau tampon de cache.
- Le dépôt devient la distribution : l'installateur web sert **sloop-dub-1.0.0.fwsc**, la
  page d'accueil GitHub explique le fork au-dessus des fonctions SLOOP, les outils de
  développement (tests hôtes, sources de l'éditeur web) sortent du checkout — ils restent
  dans l'historique git et chez le développeur.
- Empreinte mesurée (JieLi, ce dépôt) : **image flash 569 888 o / 581 052** (marge
  11 164 o, dont +4,4 Ko pour le splash de la tour), `.data`+`.bss` 57 608 o, `.lowram`
  22 772 o, pool 328 396 o — le varispeed et l'isolateur coûtent ~400 o de flash et 8 o de
  RAM sur le 2.9.16.
- Tests : dub_test 200 contrôles (les bandes répondent vraiment, chaque mute coupe son
  sinus) ; ui_pages_test 513 ; stress_test 40 000 trames ; golden 182 rendus inchangés
  (DUB off passe bit à bit) ; smoke wasm AUDIO-PATH-OK avec la preuve des mutes sur le
  binaire réel.
- La **2.9.17** (publiée entre-temps, une première passe des mêmes corrections) est ici
  reprise et approfondie : l'isolateur passe en échelle **stéréo** sans fuite de phase
  (un mute ne laisse plus filtrer la moitié du grave par les bandes du dessus), les gains
  glissent anti-clic et se calculent une fois par bloc, la tête du tape parcourt chaque
  bloc régulièrement ; les tests hôtes sont portés sur cette implémentation. Le correctif
  UBSan d'`eng_analog` (le décalage signé devenu multiplication) est gardé — le binaire
  reconstruit est identique à l'octet près.

## 2.9.17 — la première passe des corrections (supersédée par la 1.0)

- Le coefficient du crossover corrigé (2π au lieu de 2100), la signature de redraw
  complétée, la tête du delay mue par échantillon — la même intention, résolue alors en
  échelle mono à épaules 6 dB/oct. La 1.0 la remplace (voir plus haut).

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
