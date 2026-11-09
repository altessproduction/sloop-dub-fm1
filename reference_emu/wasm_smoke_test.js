#!/usr/bin/env node
/*
 * Smoke test for the freshly built reference_emu/dist/sloop.wasm (or docs/dub copy).
 *   node reference_emu/wasm_smoke_test.js [path/to/sloop.wasm]
 * Checks: exports, boot, the Dub audio path (dry note / isolator / siren),
 * the new exports (emu_dub_siren_rate, emu_dub_mix) and the 5-voice skank chords.
 * Exit code 0 = all good.
 */
'use strict';
const fs = require('fs');
const path = require('path');

const WASM = process.argv[2] ||
    path.join(__dirname, 'dist', 'sloop.wasm');

const u32 = (b0, b1, b2, b3) => (b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)) >>> 0;
const NON = (n, v) => u32(9, 0x90, n, v);          /* USB-MIDI note-on,  CIN=9 */
const NOFF = (n) => u32(8, 0x80, n, 64);           /* USB-MIDI note-off, CIN=8 */

(async () => {
    const { instance } = await WebAssembly.instantiate(fs.readFileSync(WASM), { env: {} });
    const e = instance.exports;
    const names = WebAssembly.Module.exports(
        await WebAssembly.compile(fs.readFileSync(WASM))).map(x => x.name);

    const need = ['emu_dub_siren_rate', 'emu_dub_mix', 'emu_dub_skank',
        'emu_dub_siren', 'emu_dub_band', 'emu_dub_seq_length', 'emu_dub_seq_step'];
    for (const n of need)
        if (!names.includes(n)) throw new Error('missing export ' + n);
    console.log('exports .......... OK (' + names.length + ' total, all dub exports present)');

    e.emu_init();
    e.emu_start();
    const ap = e.emu_audio_ptr();
    const f32 = () => new Float32Array(e.memory.buffer);
    const render = (n) => { e.emu_render(n); return f32().slice(ap / 4, ap / 4 + n); };
    const rms = (x) => { let s = 0; for (const v of x) s += v * v; return Math.sqrt(s / x.length); };

    /* dry note, dub off */
    e.emu_midi(NON(60, 100));
    e.emu_dub_enable(0);
    for (let i = 0; i < 8; i++) render(256);
    const rDry = rms(render(256));

    /* note through the isolator, full wet, bass+treble muted */
    e.emu_dub_enable(1);
    e.emu_dub_mix(255);
    e.emu_dub_band(0, -12, 1);
    e.emu_dub_band(1, 0, 0);
    e.emu_dub_band(2, -12, 1);
    e.emu_dub_siren(100, 740, 96);
    e.emu_dub_siren_rate(64);          /* ~8.5 Hz from the new mapping */
    for (let i = 0; i < 8; i++) render(256);
    const rWet = rms(render(256));

    /* siren only */
    e.emu_midi(NOFF(60));
    const rSiren = rms(render(512));

    /* 5-voice skank chords must not crash */
    e.emu_dub_skank(0, 4, 3, 100);     /* C 7TH oct 3 */
    e.emu_dub_skank(7, 7, 5, 127);     /* B PWR oct 5 */
    e.emu_dub_seq_length(16);
    e.emu_dub_seq_step(0, 60, 100);
    e.emu_frame();
    console.log('skank/seq/frame .. OK (no trap)');

    console.log('rms dry note ..... ' + rDry.toFixed(6));
    console.log('rms isolator ..... ' + rWet.toFixed(6));
    console.log('rms siren ........ ' + rSiren.toFixed(6));
    const pass = rDry > 0.0001 && rWet > 0.0001 && rSiren > 0.0001;
    console.log(pass ? 'AUDIO-PATH-OK' : 'AUDIO-PATH-SUSPECT');
    process.exit(pass ? 0 : 1);
})().catch((x) => { console.error('FAIL', x.message); process.exit(1); });
