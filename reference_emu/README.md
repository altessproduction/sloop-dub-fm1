# The SLOOP Dub web emulator

**Play it: https://altessproduction.github.io/sloop-dub-fm1/dub/**

A browser emulator of the M-VAVE FM-1 running the **SLOOP Dub firmware** — this
repository's own sources (GPL-3.0) compiled to WebAssembly, with a browser HAL in
place of the FM-1 hardware. No synth re-implementation: the sound, the sequencer,
the screens, the Dub menu, the siren, the tape delay and the isolator are the
firmware's own code. The FM-1's SPI flash is a local browser image (IndexedDB):
autosave, the project slots and the settings survive a reload.

The page is the FM-1's faceplate, and **the firmware's own menu is the only control
surface** — hold HOME, then SELECT, KNOB 1–4, OCT+ / OCT−, exactly as on the
machine. The fork's pages are explained under the device, in French (the section
« SLOOP DUB — LES FONCTIONS AJOUTÉES »).

## How it works

```
src/sloop_wasm.c        the web unity root: a browser HAL (time, input, ADC,
                        an ST7789 panel model, audio stubs) + the firmware
                        sources in the same order as on hardware
web/worklet.js          the wasm runs INSIDE an AudioWorklet: process() pulls
                        mix_block() for glitch-free audio; a UI frame runs
                        every ~17 ms and posts framebuffer + LED state out
web/emu.js              faceplate: screen canvas, knobs, buttons, keybed,
                        computer-keyboard + MIDI input, LED glow
web/index.html          the device skin + the fork's explanations
```

- The LCD is emulated at the panel-protocol level (CASET/RASET/RAMWR), so the
  firmware's own `lcd.c`/`gfx.c` draw every pixel.
- Input goes straight into the debounced `fm1_in` state the firmware reads;
  encoder detents arrive as steps.
- 44.1 kHz fixed-point DSP, as on the device. No floats anywhere.
- The Dub module's state is also readable through `emu_dbg` and the
  `emu_dub_*` exports (menu page, siren, sequencer steps) — the tests use it.

## Build

Needs `clang` + `lld` with the wasm32 target (no emscripten — any clang 18+,
e.g. [wasi-sdk](https://github.com/WebAssembly/wasi-sdk/releases)), `python3`
(+ numpy, Pillow) for the firmware's generated tables:

```sh
mkdir -p build/gen
python3 tools/gen_tables.py   build/gen/felucca_tables.h
python3 tools/gen_samples.py  build/gen/felucca_samples.h
python3 tools/gen_drumkits.py build/gen/felucca_drumkits.h
python3 tools/gen_fm6_patches.py build/gen/felucca_fm6.h
python3 tools/gen_font.py     build/gen/felucca_font.h
python3 tools/gen_icons.py    build/gen/felucca_icons.h
python3 tools/gen_logo.py     build/gen/sloop_logo.h

sh reference_emu/build.sh     # builds dist/sloop.wasm, refreshes docs/dub/
node reference_emu/wasm_smoke_test.js docs/dub/sloop.wasm
```

The smoke test is the shipped check: the exports, the dub audio path (dry note,
isolator, **the band mutes cutting their band**), the siren DUB-off, the riddim
bank and a real transport play — it ends with `AUDIO-PATH-OK`.

## Controls

- middle keyboard row = white keys from C4, top row = black keys
- `Z`/`X` OCT−/OCT+, `1`–`0` = FX SCL ENV LFO EDIT GLO HOME SAVE ARP SEQ,
  `Space` PLAY, `R` REC, `↑↓` SELECT, `←→` ALGORITHM, `[` `\` PRESETS
- knobs: mouse drag or scroll; buttons/keys: click or touch (multi-touch ok)
- a connected MIDI keyboard plays in (channels as on hardware: 1–3 synths,
  10 drums)

## Known gaps

- The HARDWARE CALIBRATION screen (hold OCT− + OCT+ at power-on) busy-waits
  on the key matrix and would stall the audio thread — don't enter it.
- Audio capture/USB-audio, the SysEx web editor and sample upload are stubbed.
- On phones the device rotates and scales to fill the screen (portrait).

## License

GPL-3.0-only, as the firmware it embeds.
