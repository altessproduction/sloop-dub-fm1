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
        'emu_dub_siren', 'emu_dub_band', 'emu_dub_seq_length', 'emu_dub_seq_step',
        'emu_dub_siren_type', 'emu_dub_siren_wave', 'emu_dub_siren_sym', 'emu_dub_siren_send',
        'emu_dub_siren_level', 'emu_dub_siren_freq', 'emu_dub_siren_depth',
        'emu_dub_riddim_count', 'emu_dub_riddim_name', 'emu_dub_riddim_load', 'emu_dub_riddim_track'];
    for (const n of need)
        if (!names.includes(n)) throw new Error('missing export ' + n);
    console.log('exports .......... OK (' + names.length + ' total, all dub exports present)');

    e.emu_init();
    e.emu_start();
    const ap = e.emu_audio_ptr();
    const f32 = () => new Float32Array(e.memory.buffer);
    const render = (n) => { e.emu_render(n); return f32().slice(ap / 4, ap / 4 + n); };
    const rms = (x) => { let s = 0; for (const v of x) s += v * v; return Math.sqrt(s / x.length); };
    const rmsN = (chunks) => { let s = 0, c = 0; for (let i = 0; i < chunks; i++) { const x = render(256); for (const v of x) s += v * v; c += x.length; } return Math.sqrt(s / c); };   /* (the buffer is 512 frames: 256 a call) */

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

    /* siren only, as the NJD boxes play it: square wave, exponential wail, into the delay */
    e.emu_midi(NOFF(60));
    e.emu_dub_siren_type(0);           /* WAIL */
    e.emu_dub_siren_wave(0);           /* SQR */
    e.emu_dub_siren_sym(64);
    e.emu_dub_siren_send(90);          /* the delay send */
    e.emu_dub_siren_level(100);
    const rSiren = rmsN(8);

    /* every siren type and wave must render without trapping */
    for (let t = 0; t < 5; t++) {
        e.emu_dub_siren_type(t);
        for (let w = 0; w < 5; w++) {
            e.emu_dub_siren_wave(w);
            render(256);
        }
    }
    e.emu_dub_siren_type(0);
    e.emu_dub_siren_wave(0);
    console.log('siren types/waves . OK (25 combos, no trap)');

    /* 5-voice skank chords must not crash */
    e.emu_dub_skank(0, 4, 3, 100);     /* C 7TH oct 3 */
    e.emu_dub_skank(7, 7, 5, 127);     /* B PWR oct 5 */
    e.emu_dub_seq_length(16);
    e.emu_dub_seq_step(0, 0, 60, 100); /* (2.9.2: track, step, note, velocity) */
    e.emu_frame();
    console.log('skank/seq/frame .. OK (no trap)');

    /* 2.9.2: the riddim bank: ten names, one full load, one track load, the names readable */
    const nRid = e.emu_dub_riddim_count();
    if (nRid !== 10) throw new Error('riddim count ' + nRid);
    const ridNames = [];
    for (let r = 0; r < nRid; r++) {
        const p = e.emu_dub_riddim_name(r);
        let s = '';
        const u8 = new Uint8Array(e.memory.buffer);
        for (let k = p; u8[k]; k++) s += String.fromCharCode(u8[k]);
        ridNames.push(s);
    }
    if (new Set(ridNames).size !== nRid || ridNames[0] !== 'ONE DROP')
        throw new Error('riddim names: ' + ridNames.join(','));
    e.emu_dub_riddim_load(0);          /* ONE DROP into the dub sequence */
    e.emu_dub_riddim_track(1, 3);      /* STEPPERS's drum motif over it */
    e.emu_frame();
    console.log('riddim bank ....... OK (10: ' + ridNames.join(' ') + ')');

    /* 2.9.2: the riddim plays on the transport: PLAY, the dub sequence sounds */
    for (const n of [36, 40, 43, 46, 67, 74])   /* the skank chords above let go: silence first */
        e.emu_midi(NOFF(n));
    e.emu_dub_siren_level(0);          /* the siren off, the mix dry: the riddim alone */
    e.emu_dub_siren_send(0);
    e.emu_dub_mix(0);
    e.emu_dub_band(0, 0, 0);
    e.emu_dub_band(2, 0, 0);
    for (let i = 0; i < 8; i++) render(256);
    const rIdle = rmsN(8);
    e.emu_input(0, 1 << 10);           /* PLAY down (panel.c B_PLAY) */
    for (let i = 0; i < 6; i++) render(256);
    e.emu_input(0, 0);                 /* PLAY up */
    for (let i = 0; i < 16; i++) render(256);
    const rPlay = rmsN(16);
    e.emu_input(0, 1 << 10);           /* PLAY again: STOP */
    for (let i = 0; i < 6; i++) render(256);
    e.emu_input(0, 0);
    for (let i = 0; i < 8; i++) render(256);
    const rStop = rmsN(8);
    console.log('rms riddim idle ... ' + rIdle.toFixed(6));
    console.log('rms riddim playing  ' + rPlay.toFixed(6));
    console.log('rms riddim stopped  ' + rStop.toFixed(6));
    const riddimPlays = rPlay > 0.008 && rPlay > rIdle * 2 && rStop < rPlay / 1.5;
    console.log(riddimPlays ? 'DUB-SEQ-PLAYS-OK' : 'DUB-SEQ-PLAYS-SUSPECT');

    console.log('rms dry note ..... ' + rDry.toFixed(6));
    console.log('rms isolator ..... ' + rWet.toFixed(6));
    console.log('rms siren ........ ' + rSiren.toFixed(6));
    const pass = rDry > 0.0001 && rWet > 0.0001 && rSiren > 0.0001;
    console.log(pass ? 'AUDIO-PATH-OK' : 'AUDIO-PATH-SUSPECT');
    process.exit(pass ? 0 : 1);
})().catch((x) => { console.error('FAIL', x.message); process.exit(1); });
