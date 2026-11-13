# SLOOP Dub FM-1

Première base de firmware orientée reggae / dub pour le M-VAVE FM-1, dérivée de SLOOP et conservant sa licence GPL-3.0-only.

## État actuel

Le fork ajoute une extension DSP indépendante dans `firmware/src/dub.c` et `dub.h` :

- **Version 1.0 (2026)** : la première version de partage, après les retours de test. Trois corrections :
  - **L'ISO fonctionne** — les coefficients du crossover étaient ~100 fois trop faibles (`hz * 2100 / FS` donne 4 sur 32767 à 90 Hz) : SUB, BASS et MIDS sortaient quasi muets et TOPS, le reste non filtré, portait tout le signal (le « seul le Top réagit » du retour de test). Reconstruit : une échelle de stages un pôle par canal, trois croisements à 90 Hz / 420 Hz / 2,6 kHz, chaque croisement deux passe-bas et un passe-haut à zéro vrai de DC (aucune fuite de phase) ; stéréo ; les gains calculés une fois par bloc et glissés ~12 ms (un mute ne clique jamais). L'égaliseur jamais accessible quitte la structure.
  - **TIME plie la boucle comme un vrai tape delay** — tourner TIME avec une boucle dans le delay accélère ou ralentit la boucle en continu : la tête de lecture marche à au plus la moitié de la vitesse de la bande (`DUB_TAPE_SLEW`), régulièrement à travers chaque bloc (`dly_a` → `dly_b`, Q8 échantillon par échantillon) — la tonalité monte en raccourcissant, descend en allongeant, le pliage tient tant que la tête avance (parcours complet ≈ 2,7 s). Avant, le glissement `(cible − courant) >> 4` par bloc balayait la tête en ~12 ms — le saut entendu.
  - **Les lignes suivent les knobs** — DLY LEVEL et SIREN LEVEL ne se redessinaient pas : `song.g[G_DMIX]`, `dub_menu_siren` et `song.g[G_BPM]` manquaient à la signature de redraw du menu.
  - Le paquet à flasher est publié à `docs/firmware/sloop-dub-1.5.fwsc` (image 580 976 o de 581 564 [slot 0x8DFBC], marge 588 o) et l'installateur web le sert par défaut. Empreinte complète plus bas.

- **Dub siren** (2.9.1) : une vraie siren dub style NJD — oscillateur au choix (`SQR`, `PLS`, `SAW`, `TRI`, `SIN`), **balayage de pitch exponentiel** piloté par un LFO au choix (`WAIL` triangle, `HILO` deux tons, `RAMP` la charge du yelp, `SWEEP` la chute, `SPACE` l'échantillonneur glissé), symétrie du LFO, vitesse 1 à 16 Hz, profondeur 0 à 2 octaves, et **envoi vers le delay** du projet SLOOP.
- **Séquenceur dub** (2.9.2) : **quatre pistes** (basse, skanks, mélodie, drums) de 16, 32 ou 64 pas, note et vélocité par pas, jouées sur le transport (DUB ENABLE + PLAY) — basse et mélodie en legato, skanks en piqué d'accord, drums en notes General MIDI.
- **Riddims** (2.9.2) : vingt-huit séquences sound-system de 64 pas × 4 pistes (`tools/gen_riddims.py` → `dub_riddim.h`), organisées par genre : **reggae / dub / roots** (`ONE DROP`, `STEPPERS`, `ROCKERS`, `DUBWALK`, `MEDITATE`, `DUB CUT`, `ZION`), **ska** (`SKA`), **les classiques du sound system** (`HEAVENLESS`, `TONIGHT`, `GET IN GROOVE`, `HOT MILK`, `ANSWER`, `PROMISED LAND`, `GUNMAN`, `HERE I COME`, `SLENG TENG`, `TEMPO`, `PEANY PEANY`), **dancehall** (`DANCEHALL`, `DEMBOW`), **bass music UK** (`JUNGLE`, `DUBSTEP`) et les **cinq autres auto-rythmes du Casio MT-40** (`MT40 POPS`, `MT40 SLOWRK`, `MT40 SWING`, `MT40 WALTZ`, `MT40 SAMBA`) sur la page RDM — KN1 sélectionne le riddim et OCT+ charge tout, KN2/KN3/KN4 + OCT+ chargent les motifs de basse, skank ou drum seuls dans les pistes du séquenceur (chaque riddim apporte ses **quatre patterns associés** : sa ligne de basse, ses skanks, sa mélodie, son pattern de drums — mélanger les motifs entre riddims est le geste classique du sound system). (2.9.6 : **le chargement atterrit dans le séquenceur SLOOP lui-même** — les pas des pistes 1–4, lisibles et éditables partout où SLOOP édite un pattern, voir « Le séquenceur dub ».)
- **PLAY au menu** (2.9.4) : **PLAY démarre et arrête le transport même menu ouvert** — avant, le menu avalait PLAY, si bien qu'un riddim chargé sur sa page ne pouvait pas se faire entendre ; le geste est maintenant CHARGER (OCT+ sur RDM) puis PLAY, sans quitter la page. **Le retour de chargement est visible au menu** (2.9.5) : `RIDDIM LOADED` / `BASS LOADED` / `SKANK LOADED` / `DRUM LOADED` clignote dans la barre du haut, sur l'écran d'accueil comme dans le menu.
- **Presets de sons dub** (2.9.3) : la page PRS charge un son par piste du riddim — **KN1 + OCT+** la basse (`SKANK SUB`, `ROOTS 808`, `STEPPA SUB`, `DNB REESE`, `WOBBLE`, `GROWL`, `CZ SUB`, `CHIP BASS`, `RAGGA BASS`, `TRIO BASS`), **KN2 + OCT+** le skank (`STEPPA STB`, `ROOTS STB`, `DUB CHORD`, `SKA STAB`, `SKANK ORGN`, `REGGAE ORG`, `DX SKANK`, `SKANK PNO`), **KN3 + OCT+** la mélodie (`MELODICA`, `DUB LEAD`, `DUB SIREN`, `STEEL PAN`, `AIR HORN`, `DUB FLUTE`, `FM HORNS`, `TOAST VOX`) et **KN4 + OCT+** le kit drum (`ONE DROP`, `STEPPERS`, `VINTAGE`, `808`, `JUNGLE`, `DUBSTEP`, `RAGGA`, `DEMBOW`). Chaque son est un vrai preset moteur de SLOOP (changement de moteur puis preset, niveaux calibrés et patches FM6 compris) ; le kit s'écrit dans la piste de drums.
- **Filtre, envoi et tape delay** (2.9.7) : la page DUB remappe ses lignes — `DUB FILTER` le filtre **bipolaire** (à gauche le passe-bas, à droite le passe-haut, au centre le crantage : le signal intact), `DUB MIX` le mix, `DUB SEND` l'envoi vers le delay (le *throw*) ; la page DSEQ sort et **DLY** entre : le **tape delay** — temps libre en ms ou la synchro tempo, release des répétitions, division 1/4 … 1/16 pointées. Pendant DUB le bus delay tourne en bande magnétique : le temps glisse, la lecture ondule (wow 0,7 Hz, flutter 6,3 Hz), les répétitions passent une saturation douce ; DUB off, le delay tempo du SLOOP tel qu'il a toujours été.
- **Knobs potentiomètres et sirène momentanée** (2.9.8) : sur SIR, SR2, DUB, DLY et les bandes ISO, les knobs K1–K4 se comportent en **potentiomètres** — tout le parcours en moins d'un tour, ~300° (un cran = une part du parcours, sans accélération). Sur les pages SIR/SR2, **OCT+ tenu sonne la sirène** au niveau de la ligne SIREN LEVEL (2.9.11 : **ce que la ligne affiche commande** — 0 reste silencieux), **relâché elle s'arrête** — un tap ne déclenche plus les lignes (ce sont les knobs qui règlent) ; quitter la page tenue l'arrête aussi, et ailleurs OCT+ garde ses autres vies.
- **ACCENTS et SLIDES** (2.9.9) : deux pages de plus au bouton SEQ du séquenceur SLOOP — une **grille de pas sur les quatre pistes** (une rangée par piste B/S/M/D, seize pas par écran), un second séquenceur parallèle posé sur les drapeaux que les notes déclenchent déjà : **KN1** marche le pas, **KN2** saute la banque de 16, **ALGORITHM** (l'encodeur) change de piste, **OCT+ bascule le drapeau** au curseur. Un accent fait jouer le pas à 127 ; un slide fait **glisser la note vers la suivante** au lieu de la re-attaquer (un repos rompt la chaîne). La piste de drums montre ses hits en pointillés — ses niveaux restent sur sa grille DRUMS.
- **Le son intact au repos, le niveau qui commande, le delay remappé** (2.9.11) : **DUB n'ajoute plus aucun filtre invisible** — DUB FILTER sur FLAT et l'ISO au neutre, le son est **bit à bit celui de l'original**, stéréo comprise (le lisseur interne de l'isolateur, qui assombrissait le mix et le repliait en mono dès DUB allumé, ne touche plus jamais le signal : il ne sert qu'à façonner la courbe d'égaliseur quand on s'en sert). Les seuls colorants du son en DUB restent **l'ISO et le DUB FILTER**. Sur SIR/SR2, **SIREN LEVEL affiche toujours sa valeur** et **commande le volume** : 0 reste silencieux même OCT+ tenu, et le knob retient la sirène pendant qu'elle sonne. La page **DLY** se remappe : K2 `DLY LEVEL` (le niveau de l'écho dans le mix), K3 `DLY FEEDBK` (les répétitions), K4 `DLY MODE` (FREE et toutes les divisions sur un seul parcours).
- **L'envoi de chaque piste dans le delay** (2.9.12) : une page **SND** de plus après DLY — **un potentiomètre par piste du séquenceur** : K1 `BASS SEND` (piste 1), K2 `SKANK SEND` (piste 2), K3 `MELODY SEND` (piste 3), K4 `DRUM SEND` (la piste de drums, le réglage DLY de GLO > DRUMS). Tout le parcours en ~300°, la ligne affiche un pourcentage (0–100 %) et **DRY** à zéro ; **OCT+ bascule sec ↔ demi-envoi**. Le niveau d'envoi nourrit le même bus delay que le tape delay (et l'écho tempo quand DUB est off), il se sauvegarde avec le projet et joue aussitôt — le delay dubbed piste par piste, sans quitter le menu.
- **La sirène indépendante du module DUB** (2.9.13) : la sirène est **une voix à part entière** — elle sonne **même quand DUB est éteint** (OCT+ tenu sur SIR/SR2, la ligne SIREN LEVEL commande comme toujours), et **aucune bande de l'ISO ni le DUB FILTER ne la colore jamais**, DUB allumé ou non : dans la chaîne du master elle rend dans sa propre rangée et rejoint le mix **juste après le module DUB**, avant le filtre DJ du master (FILT) qui, lui, continue de la balayer. Son seul chemin vers le delay reste son propre **SIREN SEND** ; le throw de la page DUB (K4) n'envoie plus la sirène. Désactiver DUB (K1 sur la page DUB) ne coupe plus la sirène.
- **Le visualiseur réduit à WIRES** (2.9.15) : l'appui bref sur HOME ouvre toujours l'écran plein du visualiseur, mais il ne garde plus que **WIRES** — les quatre cordes qui vibrent avec les pistes. Les onze autres styles (OSCILLOSCOPE, SPECTRUM, SPECTROGRAMME, LISSAJOUS, VU, CIRCLE, TAPE, LCD, BOUNCE, ORBIT, SLOOP), la FFT 512 points et leurs tampons sont retirés du firmware : **7,6 Ko de flash et ~7 Ko de RAM rendus** (marge flash de 8,3 à 15,9 Ko, pool de 10,2 à 15,7 Ko — voir l'empreinte plus bas). SELECT sur l'écran ne fait plus tourner de style : l'événement est avalé et le tempo ne bouge pas ; le créneau du style dans le mot de settings reste réservé, un projet plus ancien se charge à l'identique.
- **La sirène remappée, tenue à travers les pages** (2.9.16) : **SIREN SEND déménage sur SIR** (K4) et **SIREN LEVEL sur SR2** (K4) — le parcours de la sirène se lit d'un trait : ce qui la façonne d'abord, puis ce qu'elle envoie et ce qu'elle vaut. **OCT+ tenu, la sirène suit la navigation** : SELECT de SIR vers SR2 et jusqu'à la page DLY la laisse hurler, relâcher coupe, re-presser redémarre ; sur DLY, OCT+ n'a plus **aucune** autre fonction que la sirène (les knobs règlent tout, le mode du delay ne bascule plus). Sur les autres pages du menu, OCT+ garde ses autres vies. Sous l'émulateur web, la console d'onglets est retirée : **la faceplate et le menu du firmware sont les seuls contrôles**, et les fonctions du fork sont **expliquées sous l'émulateur** à sa place. Le paquet à flasher est publié à `docs/firmware/sloop-dub-2.9.16.fwsc`.
- **Skank à une touche** : huit accords (`MAJ`, `MIN`, `DIM`, `AUG`, `7TH`, `MIN7`, `9TH`, `PWR`), fondamentale chromatique, octave 3 à 5, vélocité réglable ; jusqu'à cinq notes (la 9TH).
- **Presets** : cinq points de départ (`ROOTS BASS`, `SKANK CHORD`, `DUB SIREN`, `STEPPERS`, `TAPE ECHO`).
- **DUB ISOLATOR** : quatre bandes `SUB`, `BASS`, `MIDS`, `TOPS`, croisements de séparation, gain, mute, correction paramétrique légère par bande et mix dry/wet. (2.9.11 : **au repos le module se retire** — tous les knobs au neutre, le signal d'origine passe bit à bit, stéréo comprise ; et l'égaliseur d'une bande ne filtre plus le son par-dessous, il pose sa courbe une seule fois.)

Le module est inclus selon la convention SLOOP d'unité de compilation unique. Il est initialisé dans le démarrage de l'application et placé dans `mix_block`, après les effets wet et avant le master. Il reste **désactivé par défaut** (`dub_enabled = 0`) jusqu'à activation par une page Dub ou par les contrôles firmware ; cette décision évite de modifier le son existant de SLOOP dès le premier démarrage. (2.9.13 : la sirène ne suit plus cette place — elle rend dans ses propres buffers et rejoint le mix après le module, si bien que ni l'ISO ni le DUB FILTER ne la traversent et qu'elle sonne DUB éteint comme allumé ; avec DUB off le chemin du mix reste **bit à bit celui d'origine**, les tests golden le confirment.)

## Les pages Dub du menu (appui long sur HOME)

Le menu ouvert en maintenant **HOME** compte quatorze pages, une par fonction Dub après les cinq pages SLOOP (`SCR`, `LGT`, `AUD`, `SEQ`, `SYS`) ; le bandeau d'onglets montre cinq pages autour de la courante (`< SYS DUB SIR SR2 SKK >`) et `SELECT` passe de l'une à l'autre. Chaque page a ses lignes réglées par `KNOB 1..4`, `OCT+` valide, joue ou bascule, `OCT-` ferme le menu :

- **DUB** : `DUB ENABLE`, `DUB FILTER` (2.9.7 : le filtre **bipolaire** — à gauche le passe-bas, à droite le passe-haut, au centre le crantage : le signal intact), `DUB MIX` (0 sec … 127 wet, OCT+ coupe), `DUB SEND` (2.9.7 : l'envoi vers le delay, le *throw*), `DUB PRESET` (OCT+ applique). (2.9.8 : chaque parcours de knob tient en ~300°.)
- **SIR** : `SIREN TYPE` (WAIL HILO RAMP SWEEP SPACE), `SIREN WAVE` (SQR PLS SAW TRI SIN), `SIREN PITCH` (220–1200 Hz, OCT+ remet 740), `SIREN SEND` (l'envoi delay, 0 = DRY — 2.9.16 : **venu de SR2**). (2.9.8 : parcours de knob ~300° ; **OCT+ tenu sonne la sirène** au niveau réglé sur SR2, **relâché elle s'arrête** ; 2.9.11 : le knob retient la sirène pendant qu'elle sonne ; 2.9.13 : **elle sonne même DUB éteint** et ne passe par aucun filtre du module.)
- **SR2** : `SIREN RATE` (1 à 16 Hz, OCT+ remet 2 Hz), `SIREN DEPTH` (le balayage, 0 à 2 octaves, OCT+ remet 96), `SIREN SYM` (la symétrie du LFO, OCT+ remet 64), `SIREN LEVEL` (0–127, **la valeur affichée est le niveau**, 0 silencieux — 2.9.16 : **venu de SIR**). (2.9.8 : parcours ~300° ; OCT+ tenu sonne aussi ici ; le knob de niveau suit la sirène pendant qu'elle sonne.)
- **SKANK** : `SKANK CHORD` (les huit accords), `SKANK ROOT` (chromatique), `SKANK OCT` (3 à 5), `SKANK VEL` ; **OCT+ sur n'importe quelle ligne joue l'accord** sur la piste 1. Ce sont ces réglages que la piste skank d'un riddim utilise pour sonner.
- **DLY** (2.9.7, à la place de DSEQ — l'édition des pas vit dans les pages PATTERN / NOTES du SLOOP) : le **tape delay** du module. (2.9.11 : les lignes remappées) — `DLY TIME` (le temps libre 40–1400 ms quand le mode est FREE, sinon le temps de la division s'affiche en grisé), `DLY LEVEL` (le niveau de l'écho dans le mix, le MIX du projet, 0–127), `DLY FEEDBK` (le retour des répétitions, 0–120), `DLY MODE` (la gamme ronde : **FREE**, puis 1/4, 1/8, 1/16, 1/32, 8T, 16T, 1/8D, 1/16D, 1/4D — les knobs cyclent tout ; 2.9.16 : **OCT+ ne bascule plus rien ici, il ne fait que la sirène**). (2.9.8 : parcours ~300°.)
- **SND** (2.9.12) : l'envoi de chaque piste du séquenceur dans le delay — `BASS SEND` (K1, piste 1), `SKANK SEND` (K2, piste 2), `MELODY SEND` (K3, piste 3), `DRUM SEND` (K4, la piste de drums : le DLY de GLO > DRUMS). Un **potentiomètre** par piste (~300°, 0–100 %), la ligne affiche le pourcentage et **DRY** à zéro, OCT+ bascule sec ↔ demi-envoi. L'envoi se sauvegarde dans le projet et nourrit le bus delay aussitôt — tape delay quand DUB joue, écho tempo sinon.
- **RDM** : la banque de riddims (2.9.2). `RIDDIM` (`KN1` sélectionne parmi les vingt-huit, **OCT+ charge les quatre pistes entières**), `BASS PATTERN` (`KN2` + **OCT+ charge la ligne de basse seule**, piste 1), `SKANK PATTERN` (`KN3` + **OCT+ les skanks seuls**, piste 2), `DRUM PATTERN` (`KN4` + **OCT+ les drums seuls**, piste 4). Mélanger basse d'un riddim et drums d'un autre est le geste classique du sound system — une basse de `GUNMAN` sous les drums de `ONE DROP`, un skank de `TONIGHT` sur le dembow. (2.9.4 : **PLAY démarre le transport depuis n'importe quelle page du menu**.) (2.9.5 : **chaque chargement s'affiche dans le menu** — la barre du haut remplace `MENU` par `RIDDIM LOADED`, `BASS LOADED`, `SKANK LOADED` ou `DRUM LOADED` pendant une seconde ; avant, le message ne vivait que sur l'écran d'accueil, masqué par le menu, et un OCT+ réussi semblait ne rien faire.)
- **PRS** : les presets de sons dub par piste (2.9.3) : `BASS PRESET` (`KN1` + OCT+ charge dans la piste 1), `SKANK PRESET` (`KN2` + OCT+, piste 2), `MELODY PRESET` (`KN3` + OCT+, piste 3), `DRUM KIT` (`KN4` + OCT+, le kit de la piste de drums).
- **ISO** : `SUB`, `BASS`, `MIDS`, `TOPS` (gain ; **OCT+ mute la bande**, le gain est gardé).

### Le séquenceur dub et les vingt-huit riddims

Le chargement d'un riddim (2.9.6, `dub_tracks_load`) écrit **dans le séquenceur SLOOP lui-même** : les pistes 1–4 (basse, skanks, mélodie, drums) reçoivent les 64 pas du riddim dans leurs vrais pas (`step[]` / `dstep[]`), leur LEN passe à 64, et le séquenceur parallèle du dub disparaît — **un seul séquenceur** : ce qui charge est ce qui joue et ce qui s'édite ensuite. La ligne de basse et la mélodie tiennent leur note sur les pas suivants : le maintien devient des pas TIE (pointillés sur la console web, éditables comme les autres). Un skank pique son accord d'une double-croche, construit avec la qualité et l'octave de la page SKANK ; les notes General MIDI des drums (36 kick, 38 caisse claire, 39 clap, 42 charley fermé, 46 ouvert) vont chacune dans sa lane de la piste de drums, la vélocité dans le niveau du hit. Après OCT+, tout se joue et s'édite comme un pattern SLOOP normal : touches SEQ, pages PATTERN et NOTES, couche SEQ, sons des pistes au choix habituel. Le transport fait tourner le tout, calé sur le tempo du projet. Les pages **ACCENTS** et **SLIDES** (2.9.9) s'ajoutent à la marche SEQ (NOTES → PATTERN → ACCENTS → SLIDES) : la grille des quatre pistes y pose les accents (le pas joue à 127) et les slides (la note glisse vers la suivante au lieu de re-attaquer ; un repos rompt la chaîne) — sur un riddim chargé comme sur n'importe quel pattern, et les drapeaux suivent le pattern dans le projet sauvegardé.

Les vingt-huit riddims (`tools/gen_riddims.py` → `firmware/src/dub_riddim.h`, ~14 Ko en ROM), le tempo conseillé du projet avec chacun : la famille **reggae / dub / roots** — `ONE DROP` 72 bpm, `STEPPERS` 76, `ROCKERS` 80, `DUBWALK` 70, `MEDITATE` 66, `DUB CUT` 74, `ZION` 68 ; la famille **ska** — `SKA` 88 (la marche de basse en noires, le rim sec sur les contretemps) ; les **classiques du sound system**, reconstruits à la main d'après le disque — `HEAVENLESS` 80 (Vin Gordon, 1968, Studio One ; la marche root–quinte), `TONIGHT` 84 (Keith & Tex, 1967, Derrick Harriott ; la basse rocksteady qui roule), `GET IN GROOVE` 88 (le riddim Studio One de 1968 alias *Up Park Camp* — John Holt 1976), `HOT MILK` 92 (Jackie Mittoo, 1968 ; le backbeat feutré), `ANSWER` 82 (le galop d'un seul accord, de « I'll Never Let You Go » de Slim Smith & The Uniques, 1967), `PROMISED LAND` 78 (Dennis Brown avec Aswad, 1981), `GUNMAN` 78 (Michael Prophet, 1980, Junjo Lawes à Channel One ; la marche mineure lourde des Roots Radics), `HERE I COME` 95 (Barrington Levy, 1985 ; la pompe d'octaves), `SLENG TENG` 82 (le « Rock » de la Casio MT-40 : la pompe en croches, le pop d'octave, la retombée b7 — la 4e mesure porte le fill-in du FILL-IN), `TEMPO` 88 (Anthony Red Rose, 1985, Firehouse de King Tubby), `PEANY PEANY` 92 (Bobby Digital, 1987, alias *Fade Away*) ; la famille **dancehall** — `DANCEHALL` 95 (le clap 3+3+2, les stabs poussés, la fanfare), `DEMBOW` 100 (le boom-ch-boom-chick strict) ; la famille **bass music UK** — `JUNGLE` 172 (le break haché, la sub qui répond), `DUBSTEP` 140 (le half-time, la sub wobblée, une seule stab sombre) ; la famille **MT-40** — `MT40 POPS` 96, `MT40 SLOWRK` 66 (le half-time paresseux), `MT40 SWING` 84 (la basse qui marche), `MT40 WALTZ` 90 (le oom-pah-pah sur une grille 4/4), `MT40 SAMBA` 100 (l'agogo au rim, la surdo syncopée) — chacun sa progression (Am, Dm, F, G…), son groove de basse, ses skanks et son pattern de drums. Réglez le BPM du projet sur le tempo du riddim pour le feel juste.

Le drum track des riddims note ses hits en General MIDI : 36 kick, 37 rim, 38 caisse claire (les ghosts à faible vélocité), 39 clap, 42 charley fermé, 46 ouvert — chaque note dans sa lane du kit chargé sur la piste (2.9.3), les traitements de kit (ONE DROP, STEPPERS, SKA, ROCKERS, DUB) s'ajoutent dessus. La tenue à une note par pas fait le style : le one-drop pose son kick une double-croche avant sa caisse claire (le pickup des roots), le steppers n'a pas de snare superposée à son kick, les breaks jungle gardent leurs ghosts.

Côté console web (2.9.6) : l'onglet **DSQ** montre **les pistes du séquenceur SLOOP** (quatre pistes × 64 pas, relecture `emu_dub_seq_len` / `emu_dub_seq_note` / `emu_dub_seq_pos` / `emu_dub_seq_playing`) — ce qu'un OCT+ (page RDM du firmware ou boutons CHARGER de l'onglet RDM) a chargé **dans les pistes** s'affiche tel quel, chaque piste suit son propre LEN, la colonne claire est la tête de lecture pendant PLAY, la piste choisie (BASS SKNK MEL DRUM) s'édite au clic (les pas tenus TIE se dessinent en pointillé) ; l'onglet RDM affiche `CHARGÉ · <nom>` après chaque chargement.

Côté DSP, les réglages vivent dans `dub_siren_t` (`freq_hz`, `depth`, `rate`, `type`, `wave`, `sym`, `send`, avec `dub_siren_set_freq` / `set_rate` / `set_type` / `set_wave` / `set_sym` / `set_send` bornés) et la table `DUB_SKANK_NAMES` de `dub.h` ; l'émulateur et l'éditeur web passent par les mêmes points d'entrée. Le rendu de la sirène a déménagé dans `mix_block` : il arrive **avant** `fx_buses`, si bien que la part `SIREN SEND` entre dans le bus delay réel de SLOOP (`acc[0].sd`) et ressort dans l'écho du projet ; l'isolateur, lui, reste après les buses, avant le master. Le niveau est à pente douce (`level_cur`) : les déclenchements et les coupures ne cliquent pas.

## Tests et prévisualisation navigateur

Les tests hôtes (`tests/`) et les tests navigateur vivent avec le développeur — ils ne sont plus publiés dans ce dépôt (1.0 : le dépôt ne garde que l'essentiel install/test). Voici ce qu'ils couvrent (l'historique git les garde) :

- les fréquences de croisement et les paramètres de l'isolateur, le mix à sec ;
- les bornes de la sirène (220 / 1 200 Hz, rate 1 à 16 Hz, type/wave/sym/send bornés), son rendu stéréo borné, les cinq courbes de LFO et les cinq courbes d'oscillateur, et l'envoi delay (le bus se remplit, se vide à sec) ;
- les longueurs 16/32/64 et le rejet d'une longueur invalide ;
- la banque de riddims (2.9.2) : vingt-huit séquences nommées, chaque note/velocité dans les bornes, chaque piste a de la musique, `dub_riddim_load` copie les quatre pistes entières (64 pas, tête à 0), `dub_riddim_load_track` ne touche que sa piste, `dub_seq_set_step` ignore une piste invalide et fait d'une note > 127 un repos ;
- les banques de sons dub (2.9.3) : huit par rôle, nommés et distincts, les kits dans la liste des kits.
- les huit accords skank à une touche, leur troncature et leur rebouclage ;
- la présence de la banque de presets.

La suite UI complète `tests/ui_pages_test.c` parcourt les treize pages du menu sur le firmware réel hébergé : les huit pages Dub (réglages, OCT+ et chargements RDM/PRS — chaque son dub y est vérifié comme un vrai preset moteur, et OCT+ bascule le moteur et le preset de la piste), la fenêtre d'onglets et la fin de course de `SELECT`, puis 20 000 trames d'usage aléatoire. Il est complété par `tests/dub_emulator_test.py`, qui vérifie la page navigateur sur écrans mobile et bureau : onglets de la console Dub (DUB/SIR/SR2/SKANK/DSEQ/RDM/ISO) avec les sélecteurs et chargements de riddims, la vue séquenceur quatre pistes (2.9.4), presets, sirène, skank, isolateur, transport, accessibilité des boutons et absence de défilement horizontal. `tests/menu_navigation_test.py` fait la même marche des pages dans l'émulateur, `tests/riddim_test.py` rejoue le scénario complet du 2.9.4 (chargement RDM → relecture DSQ → **PLAY au menu qui sonne le riddim** → motifs recombinés → OCT+ firmware → LEN 64) et `tests/public_menu_check.py` refait la marche sur le site publié après déploiement. `reference_emu/wasm_smoke_test.js` vérifie enfin le binaire seul : exports, banque de riddims (les dix noms lus dans la mémoire WASM), chargements, et **la lecture réelle sur transport** — RMS au repos, en lecture, à l'arrêt.

Pour lancer les contrôles locaux :

Le contrôle publié avec le dépôt est le **smoke test du binaire** (sans navigateur) :

```sh
node reference_emu/wasm_smoke_test.js            # test reference_emu/dist/sloop.wasm
node reference_emu/wasm_smoke_test.js docs/dub/sloop.wasm
```

Il vérifie les exports, le chemin audio dub (note sèche, note sous isolateur, sirène, **les mutes qui coupent leur bande**), la banque de riddims et une vraie lecture sur transport — `AUDIO-PATH-OK` à la fin.

La compilation et l’installation sur le matériel FM-1 nécessitent toujours la toolchain JieLi et les fichiers SDK AC79 décrits dans `BUILDING.md`.

## Émulateur web

Une surface web jouable est publiée sous `docs/dub/` et déployée automatiquement sur GitHub Pages à chaque envoi vers `main`. **La page est la faceplate du FM-1 et le firmware réel** — l'ancienne console d'onglets (`DUB`, `SIR`, `SR2`, …) est retirée (2.9.16) : le menu Dub du firmware (HOME long, SELECT, KNOB 1–4, OCT+, OCT−) est le seul réglage, exactement comme sur la machine. Sous l'émulateur, la section **« SLOOP DUB — LES FONCTIONS AJOUTÉES »** explique chaque page du fork (DUB, SIR, SR2, SKANK, DLY, SND, RDM, PRS, ISO, ACC/SLD), la sirène momentanée tenue à travers les pages et le chemin audio intact. Les tests lisent l'état du firmware lui-même par la sonde `emu_dbg` du wasm (menu ouvert, la page du curseur, la sirène active, le hash des pas du séquenceur) — la page ne reflète plus l'état, elle l'affiche.

Le moteur SLOOP/WASM est distribué avec la page et exécute le mixage firmware dans un `AudioWorklet` séparé. Les exports dédiés restent (`emu_dub_siren_type`, `_wave`, `_sym`, `_send`, `_level`, `_freq`, `_depth`, `emu_dub_siren_rate`, `emu_dub_mix`, …) : les réglages programmatiques marchent toujours, le `worklet.js` les détecte au chargement. Le paquet à flasher accompagne le dépôt : **`docs/firmware/sloop-dub-1.5.fwsc`** — l'installateur web le sert par défaut (sha256 vérifié avant écriture) ; il accepte aussi n'importe quel `.fwsc` à son sélecteur de fichier.

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

## Empreinte FM-1 (mesurée, build 1.5)

Mesures réelles obtenues avec la chaîne JieLi (clang 4.0.1 pi32v2) sur ce dépôt ; la base SLOOP 2.9.6
(`bddd08a`) servait de référence. Le 1.0 ajoute ~400 o de flash et 8 o de RAM sur le 2.9.16
(les trois correctifs : l'échelle du crossover, le varispeed tape, la signature de redraw) ; la banque
sound-system (1.1 : 158 presets, 1.2 : 37 kits, 1.3 : 22 riddims et leurs patterns) reprend ensuite
la marge jusqu'à 576 208 o ; le 1.4 y ajoute les six riddims et les 22 sons du Casio MT-40, le kit
MT40 et leurs noms (580 944 o) ; le 1.5 échange dix riddims génériques contre les onze classiques
du sound system (+32 o), et l'image s'établit à 580 976 o — **588 o de marge** sur le slot de 0x8DFBC. La flash du FM-1 offre 0x93000 o (588 Ko) au paquet ; le slot
application fait 0x8DFBC o (581 Ko) — en 2.9.6 il était déjà rempli à 99,9 % (360 o de marge).

| Ressource | 2.9.6 (base) | 2.9.13 | 2.9.16 | **1.5 (ce build)** | Capacité | Marge 1.5 |
|---|---|---|---|---|---|---|
| Image flash (code + rodata) | 580 692 o | 572 784 o | 565 040 o | **580 976 o** | 581 564 o | **588 o** |
| RAM `.data`+`.bss` | 60 108 o | 60 448 o | 57 600 o | **57 624 o** | 98 304 o | 40 680 o |
| `.lowram` (reverb, piles cœur 1) | 22 772 o | 22 772 o | 22 772 o | 22 772 o | 29 392 o | 6 620 o |
| Pool (canevas, lignes d'effets) | 333 900 o | 333 900 o | 328 396 o | **328 396 o** | 344 064 o | **15 668 o** |
| Pile principale au repos | — | 22 956 o libres (mesure appareil) | 24 320 o | — |

Les ajouts 2.9.7→2.9.13 (filtre bipolaire, remap delay, page SEND, indépendance de la sirène)
comptaient environ +9,5 Ko de symboles ; le build ne rentrait donc plus. Trois réglages de
compilation, sans toucher une ligne de code fonctionnelle, ramènent l'image sous le slot **en
conservant le logo graphique** :

- `-Oz` au lieu de `-Os` (clang pi32v2, densité de code) : environ −14 Ko ;
- `--gc-sections` sur l'édition de liens de l'application (le loader le faisait déjà) : les
  sections jamais référencées ne coûtent plus rien ;
- `-fdata-sections` : la rodata morte est élaguée aussi.

Le 2.9.15 rend en plus **7 616 o de flash** (les onze styles du visualiseur, la FFT 512 points et
leurs routines de dessin) et **≈7 Ko de RAM** (les tampons FFT et spectrogramme du pool −5,5 Ko, la
trajectoire Lissajous du `.bss` −1,5 Ko, l'état de dessin réduit) : la marge flash double, le pool
aussi.

### Le delay en particulier (queues longues)

La ligne de retard `dly_buf` est un tampon circulaire **statique** de 65 536 échantillons ×
16 bits = **128 Ko** dans le pool — alloué une fois pour toutes à la compilation pour le maximum
(1,49 s à 44,1 kHz : croche pointée à 31 BPM, noire à 41 BPM). Conséquences :

- **La longueur de la queue ne coûte rien** : temps réglé de 50 ms à 1,4 s, la RAM consommée par
  le delay est identique (128 Ko), et le coût CPU par échantillon aussi (une écriture, deux
  lectures interpolées, un passe-bas de coloration, un feedback — une dizaine d'opérations
  entières Q15, soit ~0,4 Mop/s à 44,1 kHz). Les répétitions longues ne parcourent jamais le
  tampon entier : seules les têtes de lecture/écriture travaillent.
- La queue longue tient par le **feedback** (DLY FEEDBK), pas par la mémoire ; les échantillons
  restent dans les 128 Ko déjà réservés, sans croissance possible.
- Le delay est le premier consommateur du pool (38 %) ; un délai plus long (2 s et plus) ne
  rentrerait qu'en empruntant la marge du pool et de `.lowram` (~17 Ko au total, soit +0,7 s)
  ou en dégradant la résolution de la ligne — non fait, décision produit SLOOP.

### CPU

Mesures appareil (DUALCORE.md, moteur SLOOP sans le module Dub) : 9 % au repos, 23 % avec le
second cœur et 31 % sans, sur le pire pattern du propriétaire ; interruption audio max mesurée
1,273 ms pour un bloc de 32 échantillons (0,725 ms). Le module Dub ajoute quelques opérations
fixe-point par échantillon (sirène, isolateur au repos entièrement court-circuité, têtes tape du
delay) — de l'ordre de +1 à 2 % de charge, très loin du garde-fou des 8 ms du second cœur.

### Ce qui reste serré

- **La flash** : 15,6 Ko de marge en 1.0 après `-Oz`, le visualiseur réduit et les trois correctifs ; toute grosse
  fonctionnalité future devra se justifier. Le plan B intégré du build (`FELUCCA_LOGO_TEXT=1`,
  logo en texte, −4,6 Ko) reste disponible si un jour ça déborde.
- **Le pool** : 15,7 Ko de marge (2.9.15) ; ne pas y ajouter de tampon sans vérification (`ok pool …` du build).

