# CHANGELOG — SLOOP Dub FM-1

Le fil des versions du fork Dub. La base SLOOP et son histoire : [SLOOP.md](SLOOP.md)
et les [releases](https://github.com/isod89/sloop-fm1/releases) du dépôt d'origine.

## 1.5 — novembre 2026

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
- **Les répétitions de basse frappent de nouveau** (2.9.6) : au chargement d'un riddim, le
  chargeur collait en TIE toute note de même hauteur que la tenue — le bounce du Sleng Teng
  (les paires 3–4 et 11–12) fondait dans une seule note filée. Chaque pas écrit re-frappe
  maintenant, même à l'unisson : **32 attaques de basse sur les quatre mesures, dont six
  re-frappes consécutives de même hauteur** (le pluck du MT-40), la note tenue s'achevant à
  son gate dans l'attaque suivante ; le glue dub reste sur les silences (la tenue devient un
  TIE, lisible et éditable au PATTERN). Vérifié dans l'émulateur (`scripts/verify_sleng_bounce.js`)
  : SLENG-BOUNCE-OK.
- **La chaîne web suit** : l'émulateur recompilé (zig, wasm32) passe le smoke test — 28
  riddims dont les onze, AUDIO-PATH-OK / DUB-SEQ-PLAYS-OK — et le SLENG-BOUNCE-OK ; le wasm
  de l'éditeur suit ; l'installateur web sert le paquet 1.5 (sha256 vérifié), le STAMP du
  service worker est recalculé.
- **La place** : l'image passe de 580 944 à **580 976 o** (+32 o) sur le slot de 0x8DFBC
  (581 564 o) — **588 o de marge**.

## 1.4 — novembre 2026

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
