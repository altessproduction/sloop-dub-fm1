**The classics every sound system grew up on join the firmware.** The eleven riddims that
built the dance — from the Studio One sessions of 1967–68 to the first digital dancehall of
1985–87 — now live in the bank: **Heavenless, Tonight, Get in the Groove, Hot Milk, Answer,
Promised Land, Gunman, Here I Come, Sleng Teng, Tempo, Peany Peany**. As ever in this fork,
everything is **rebuilt by hand from the records** — no sample, no factory ROM data — so the
first bar tells you which record it came from.

- **Ten new riddims** (`tools/gen_riddims.py`), by family:
  - **Studio One / rocksteady** — `HEAVENLESS` 80 bpm (Vin Gordon, 1968, Coxsone Dodd; the
    root–fifth walk), `TONIGHT` 84 (Keith & Tex, 1967, Derrick Harriott; the rolling bass),
    `GET IN GROOVE` 88 (the 1968 Studio One riddim, aka *Up Park Camp* — John Holt's 1976
    cut), `HOT MILK` 92 (Jackie Mittoo & The Soul Vendors, 1968; the mellow backbeat, the
    floating line), `ANSWER` 82 (the one-chord gallop — from Slim Smith & The Uniques,
    *I'll Never Let You Go*, 1967), `PROMISED LAND` 78 (Dennis Brown with Aswad, 1981; the
    one drop, the F–B♭–C–G cadence).
  - **Eighties band and digital dancehall** — `GUNMAN` 78 (Michael Prophet, 1980, Henry
    "Junjo" Lawes at Channel One; the Roots Radics' heavy minor march), `HERE I COME` 95
    (Barrington Levy, 1985; the bouncing octave pump), `TEMPO` 88 (Anthony Red Rose, 1985,
    King Tubby's Firehouse), `PEANY PEANY` 92 (Bobby Digital's riddim, 1987, aka *Fade
    Away* — Little John voiced it first); the `SLENG TENG` (already in since 1.4) leads them.
- **Ten generic riddims step aside** to keep the bank at **28** and the build inside its
  slot — the swap costs +32 bytes: `DIGITAL`, `LOVERS`, `SKANKIN`, `ROCKSTDY`, `TWO TONE`,
  `UK STEPPA`, `DNB STEP`, `RAGGA JGL`, `UK 2STEP`, `BASSLINE`. The bases stay (`ONE DROP`,
  `STEPPERS`, `ROCKERS`, `DUBWALK`, `MEDITATE`, `DUB CUT`, `ZION`, `SKA`, `DANCEHALL`,
  `DEMBOW`, `JUNGLE`, `DUBSTEP`) and so do the MT-40's five other rhythms.
- **The bass repeats strike again** (`seq.c` dub_tracks_load): the riddim load glued every
  same-pitch note into the held one (a TIE), so the Sleng Teng's bounce — the note pairs at
  steps 3–4 and 11–12 — melted into one long held note. Every written note now attacks, even
  at the unison: **32 bass attacks across the four bars, six same-pitch re-strikes** (the
  MT-40's pluck), the held note ending at its gate into the next attack; the dub glue stays
  over the rests (the hold is a TIE step, visible and editable on the PATTERN page). The
  emulator proves it end to end (`scripts/verify_sleng_bounce.js`): SLENG-BOUNCE-OK. No
  tempo change — the repeats were always in the grid, the loader glued them.
- **The web chain follows**: the emulator rebuilt (zig, wasm32) passes the smoke test — 28
  riddims including the eleven, AUDIO-PATH-OK / DUB-SEQ-PLAYS-OK — and the SLENG-BOUNCE-OK;
  the editor's preview wasm too; the installer serves the 1.5 package (sha256 checked before
  writing); the service worker's STAMP recomputed.
- **The footprint**: the image goes from 580 944 to **580 976 B** (+32) on the 0x8DFBC slot
  (581 564 B) — **588 B of headroom**.

**Install**: the web installer below serves 1.5 directly; or download `sloop-dub-1.5.fwsc`
and flash it with the installer's file picker. Your projects, presets, samples and settings
survive the update. Still custom firmware — install at your own risk.
