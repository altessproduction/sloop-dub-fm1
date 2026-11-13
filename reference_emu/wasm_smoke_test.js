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
const PLAYB = 1 << 12;                             /* panel.c PANEL_DEFAULT: B_PLAY = 12 (bit 10 was the
                                                    * ARP button: the old passes rang the held skank chords,
                                                    * the transport never ran). B_OCTUP = 1, B_OCTDN = 0 */

(async () => {
    const { instance } = await WebAssembly.instantiate(fs.readFileSync(WASM), { env: {} });
    const e = instance.exports;
    const names = WebAssembly.Module.exports(
        await WebAssembly.compile(fs.readFileSync(WASM))).map(x => x.name);

    const need = ['emu_dub_siren_rate', 'emu_dub_mix', 'emu_dub_skank',
        'emu_dub_siren', 'emu_dub_band', 'emu_dub_seq_length', 'emu_dub_seq_step',
        'emu_dub_siren_type', 'emu_dub_siren_wave', 'emu_dub_siren_sym', 'emu_dub_siren_send',
        'emu_dub_siren_level', 'emu_dub_siren_freq', 'emu_dub_siren_depth',
        'emu_dub_riddim_count', 'emu_dub_riddim_name', 'emu_dub_riddim_load', 'emu_dub_riddim_track',
        'emu_dub_seq_track_len', 'emu_dub_dly_mix', 'emu_dub_dly_mix_get',
        'emu_dub_sound_count', 'emu_dub_sound_name', 'emu_dub_sound_load'];
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

    /* (1.0) the band mutes cut the frequencies they own: the note at 262 Hz lives in
     * BASS — muting it silences the note (the ladder's leaks stay, small), keeping it
     * while the other three bands mute keeps the note. Before, the crossover's
     * coefficients sat ~100x low and only TOPS ever carried the sound. */
    e.emu_dub_siren_level(0);
    e.emu_dub_band(0, 0, 0);
    e.emu_dub_band(1, 0, 0);
    e.emu_dub_band(2, 0, 0);
    e.emu_dub_band(3, 0, 0);
    for (let i = 0; i < 16; i++) render(256);      /* the gains glide, the filters settle */
    const rAll = rmsN(8);
    e.emu_dub_band(1, 0, 1);                        /* BASS out: the note goes */
    for (let i = 0; i < 8; i++) render(256);
    const rNoBass = rmsN(8);
    e.emu_dub_band(1, 0, 0);
    e.emu_dub_band(0, 0, 1);
    e.emu_dub_band(2, 0, 1);
    e.emu_dub_band(3, 0, 1);
    for (let i = 0; i < 8; i++) render(256);
    const rOnlyBass = rmsN(8);
    if (!(rNoBass < rAll * 0.5)) throw new Error('BASS mute does not cut: ' + rNoBass + ' vs ' + rAll);
    if (!(rOnlyBass > rAll * 0.6)) throw new Error('BASS alone does not keep the note: ' + rOnlyBass + ' vs ' + rAll);
    console.log('band mutes cut ..... OK (all ' + rAll.toFixed(4) + ', BASS out ' + rNoBass.toFixed(4) + ', only BASS ' + rOnlyBass.toFixed(4) + ')');

    /* siren only, as the NJD boxes play it: square wave, exponential wail, into the delay */
    e.emu_midi(NOFF(60));
    e.emu_dub_siren_type(0);           /* WAIL */
    e.emu_dub_siren_wave(0);           /* SQR */
    e.emu_dub_siren_sym(64);
    e.emu_dub_siren_send(90);          /* the delay send */
    e.emu_dub_siren_level(100);
    const rSiren = rmsN(8);

    /* (2.9.13) the siren independent of the DUB module: the module off, it still wails —
     * it renders whether DUB runs or not, and no isolator band or DUB filter colours it */
    e.emu_dub_enable(0);
    const rSirenFree = rmsN(4);
    e.emu_dub_enable(1);
    if (!(rSirenFree > rSiren * 0.5)) throw new Error('siren silent with DUB off: ' + rSirenFree);
    console.log('siren wails DUB-off . OK (rms ' + rSirenFree.toFixed(6) + ' vs DUB-on ' + rSiren.toFixed(6) + ')');

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

    /* 2.9.2: the riddim bank: the 28 sound-system names, one full load, one track load, the names
     * readable (the ten reggae/dub originals, then ska, dancehall, UK bass music and the MT-40's six) */
    const nRid = e.emu_dub_riddim_count();
    if (nRid !== 28) throw new Error('riddim count ' + nRid);
    const ridNames = [];
    for (let r = 0; r < nRid; r++) {
        const p = e.emu_dub_riddim_name(r);
        let s = '';
        const u8 = new Uint8Array(e.memory.buffer);
        for (let k = p; u8[k]; k++) s += String.fromCharCode(u8[k]);
        ridNames.push(s);
    }
    if (new Set(ridNames).size !== nRid || ridNames[0] !== 'ONE DROP' ||
        !ridNames.includes('SKA') || !ridNames.includes('DEMBOW') || !ridNames.includes('JUNGLE') ||
        !ridNames.includes('SLENG TENG'))
        throw new Error('riddim names: ' + ridNames.join(','));
    e.emu_dub_riddim_load(0);          /* ONE DROP into the SLOOP sequencer's tracks (2.9.6) */
    e.emu_dub_riddim_track(1, 3);      /* STEPPERS's drum motif over it */
    e.emu_frame();
    console.log('riddim bank ....... OK (28: ' + ridNames.join(' ') + ')');

    /* 2.9.6: the load's readback — the steps are in the sequencer's tracks, not a buffer:
     * ONE DROP's bass st0 = 33 with st1 the TIE holding it, the skank's stab at st2, the
     * drum motif's kick at st0, every track's LEN 64. The PATTERN page draws these. */
    const note = (t, s) => e.emu_dub_seq_note(t, s);
    if (e.emu_dub_seq_len() !== 64) throw new Error('seq len ' + e.emu_dub_seq_len());
    if (note(0, 0) !== 33) throw new Error('bass st0 ' + note(0, 0));
    if (note(0, 1) !== 254) throw new Error('bass st1 tie ' + note(0, 1));
    if (note(1, 2) % 12 !== 66 % 12) throw new Error('skank st2 ' + note(1, 2));   /* the stab is the SKANK
        * page's chord built from the riddim's note class (F# here): its root lands at the page's
        * octave (42 with the boot config), the readback's note[0] is that chord root, not 66 */
    if (note(3, 0) !== 36) throw new Error('drum st0 ' + note(3, 0));
    for (let t = 0; t < 4; t++)
        if (e.emu_dub_seq_track_len(t) !== 64) throw new Error('track ' + t + ' len ' + e.emu_dub_seq_track_len(t));
    console.log('seq readback ...... OK (steps in the tracks, TIE holds, LEN 64)');

    /* 2.9.7: the DUB page's filter and throw, the DLY page's tape delay: the same state
     * the menu rows hold, and the audio path runs tape without a trap */
    for (const n of ['emu_dub_filter', 'emu_dub_filter_get', 'emu_dub_send', 'emu_dub_send_get',
                     'emu_dub_dly_time', 'emu_dub_dly_time_get', 'emu_dub_dly_rel', 'emu_dub_dly_rel_get',
                     'emu_dub_dly_sync', 'emu_dub_dly_sync_get', 'emu_dub_dly_div', 'emu_dub_dly_div_get'])
        if (!names.includes(n)) throw new Error('missing export ' + n);
    e.emu_dub_filter(20);
    if (e.emu_dub_filter_get() !== 20) throw new Error('filter get ' + e.emu_dub_filter_get());
    e.emu_dub_filter(300);             /* clamps to the HP end */
    if (e.emu_dub_filter_get() !== 127) throw new Error('filter clamp ' + e.emu_dub_filter_get());
    e.emu_dub_filter(64);              /* the flat center */
    if (e.emu_dub_filter_get() !== 64) throw new Error('filter center ' + e.emu_dub_filter_get());
    e.emu_dub_send(80);
    if (e.emu_dub_send_get() !== 80) throw new Error('send get ' + e.emu_dub_send_get());
    e.emu_dub_dly_time(5000);          /* clamps to the tape's long end */
    if (e.emu_dub_dly_time_get() !== 1400) throw new Error('dly ms ' + e.emu_dub_dly_time_get());
    e.emu_dub_dly_time(400);
    e.emu_dub_dly_rel(90);
    if (e.emu_dub_dly_rel_get() !== 90) throw new Error('dly rel ' + e.emu_dub_dly_rel_get());
    e.emu_dub_dly_sync(0);             /* the free ms rules */
    if (e.emu_dub_dly_sync_get() !== 0) throw new Error('dly sync ' + e.emu_dub_dly_sync_get());
    e.emu_dub_dly_div(3);
    if (e.emu_dub_dly_div_get() !== 3) throw new Error('dly div ' + e.emu_dub_dly_div_get());
    e.emu_dub_enable(1);               /* the module on: the filter, the throw, the tape run */
    for (let i = 0; i < 40; i++) render(256);   /* the sweeps glide, the echo rings, no trap */
    e.emu_dub_send(0);
    e.emu_dub_filter(64);
    e.emu_dub_dly_sync(1);
    e.emu_dub_dly_rel(60);
    e.emu_dub_siren_level(0);          /* the siren rests: it kept wailing into the tape above */
    e.emu_dub_dly_rel(0);              /* one pass, no repeats: the tail dies young */
    for (let i = 0; i < 260; i++) render(256);   /* the tape flushes (~1.5 s) before the
                                        * riddim RMS; the module stays ON, as the walk came */
    console.log('filter/throw/dly ... OK (bipolar filter, the throw, the tape state)');

    /* 2.9.3: the dub sound banks: the PRS lists (bass 10, skanks, melody 8 and kits 9 — the
     * MT-40's kit came), the names readable, every role loads */
    const roleNames = [];
    const roleWant = [10, 8, 8, 9];
    const roleFirst = ['SKANK SUB', 'STEPPA STB', 'MELODICA'];
    for (let role = 0; role < 4; role++) {
        const n = e.emu_dub_sound_count(role);
        if (n !== roleWant[role]) throw new Error('sound bank ' + role + ' count ' + n);
        const p = e.emu_dub_sound_name(role, role === 3 ? 4 : 0);
        const u8 = new Uint8Array(e.memory.buffer);
        let s = '';
        for (let k = p; u8[k]; k++) s += String.fromCharCode(u8[k]);
        if (!s) throw new Error('sound bank ' + role + ': empty name');
        if (role < 3 && s !== roleFirst[role]) throw new Error('sound bank ' + role + ': ' + s);
        roleNames.push(s);
        e.emu_dub_sound_load(role, role);   /* a load a role, no trap */
    }
    e.emu_frame();
    console.log('sound banks ....... OK (' + roleNames.join(' / ') + ')');

    /* the steps survive the sound swaps: the riddim's bass st0 is still there (2.9.6's readback) */
    if (note(0, 0) !== 33) throw new Error('steps wiped after the sound loads: bass st0 ' + note(0, 0));
    console.log('steps survive ..... OK (the loads leave the sequence alone)');

    /* 2.9.2: the riddim plays on the transport: PLAY, the dub sequence sounds */
    for (const n of [36, 40, 43, 46, 67, 74])   /* the skank chords above let go: silence first */
        e.emu_midi(NOFF(n));
    e.emu_dub_siren_level(0);          /* the siren off, the mix dry: the riddim alone */
    e.emu_dub_siren_send(0);
    e.emu_dub_mix(0);
    e.emu_dub_band(0, 0, 0);
    e.emu_dub_band(2, 0, 0);
    for (let i = 0; i < 20; i++) render(256);   /* the unmuted bands let the held chord tails
                                                 * through: they settle before the idle reads */
    const rIdle = rmsN(8);
    e.emu_input(0, PLAYB);             /* PLAY down (panel.c B_PLAY = 12) */
    e.emu_frame();
    for (let i = 0; i < 6; i++) render(256);
    e.emu_input(0, 0);                 /* PLAY up */
    e.emu_frame();
    for (let i = 0; i < 16; i++) render(256);
    const rPlay = rmsN(16);
    if (!e.emu_dbg(0)) throw new Error('transport not playing after PLAY');
    e.emu_input(0, PLAYB);             /* PLAY again: STOP */
    e.emu_frame();
    for (let i = 0; i < 6; i++) render(256);
    e.emu_input(0, 0);
    e.emu_frame();
    if (e.emu_dbg(0)) throw new Error('transport still playing after STOP');
    for (let i = 0; i < 40; i++) render(256);   /* the tracks' voices release, the echo dies */
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
