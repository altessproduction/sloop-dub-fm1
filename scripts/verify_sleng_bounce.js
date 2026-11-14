/* Verify the Sleng Teng's bass after the verified transcription (1.6): the MT-40 Rock
 * preset's stutter, Noel Davey's own tab at 82 bpm — the root on every beat, three
 * sixteenths a semitone above it, each one a fresh strike, the tail G–F# cut off
 * plucked-short. The bar is static (the bass key held down on the MT-40); the chords
 * move C#m–B–A–B above it. Every written note strikes again (1.5's fix); a DUB_SEQ_CUT
 * step ends the held note and reads back as a bare rest, not a TIE.
 *   node scripts/verify_sleng_bounce.js [path/to/sloop.wasm]
 */
'use strict';
const fs = require('fs');
const path = require('path');

const WASM = process.argv[2] || path.join(__dirname, '..', 'docs', 'dub', 'sloop.wasm');
const SLENG = 16;                                  /* the bank's index of SLENG TENG */
const TIE = 254, REST = 255, CUT = 253;
const ANCHOR = 37;                                 /* C#2, the static bass key */
/* the verified figure (tools/gen_riddims.py's mtstut), {step: degree or 'c'} */
const FIGURE = {
    0: 0, 1: 1, 2: 1, 3: 1, 4: 0, 5: 1, 6: 1, 7: 1,
    8: 0, 9: 1, 10: 1, 11: 1, 12: 6, 13: 'c', 14: 5, 15: 'c',
};

/* the load's semantics (seq.c dub_tracks_load): a written note is an attack (even the
 * same pitch), a plain rest holds the current note (TIE) or stays silent, a CUT ends it */
function expect_bar(figure, root) {
    const out = [];
    let held = REST;
    for (let st = 0; st < 16; st++) {
        if (figure[st] === 'c') {
            held = REST;
            out.push(REST);                        /* the cut: a bare rest, never a TIE */
        } else if (figure[st] !== undefined) {
            held = root + figure[st];
            out.push(held);                        /* an attack: every note strikes again */
        } else {
            out.push(held !== REST ? TIE : REST);  /* the glue holds over the rest */
        }
    }
    return out;
}

(async () => {
    const { instance } = await WebAssembly.instantiate(fs.readFileSync(WASM), { env: {} });
    const e = instance.exports;
    e.emu_init();
    e.emu_start();

    const u8 = new Uint8Array(e.memory.buffer);
    let slengName = '';
    for (let k = e.emu_dub_riddim_name(SLENG); u8[k]; k++) slengName += String.fromCharCode(u8[k]);
    if (slengName !== 'SLENG TENG')
        throw new Error('riddim ' + SLENG + ' is ' + slengName + ', not SLENG TENG');

    e.emu_dub_riddim_load(SLENG);
    e.emu_frame();
    const note = (t, s) => e.emu_dub_seq_note(t, s);

    const want = expect_bar(FIGURE, ANCHOR);
    let attacks = 0, repeats = 0, cuts = 0;
    for (let bar = 0; bar < 4; bar++) {
        for (let st = 0; st < 16; st++) {
            const got = note(0, bar * 16 + st);
            if (got !== want[st])
                throw new Error(`bass bar ${bar + 1} st${st}: got ${got}, want ${want[st]}`);
            if (got !== TIE && got !== REST) {
                attacks++;
                if (st > 0 && want[st - 1] !== REST && want[st - 1] !== TIE && want[st - 1] === got)
                    repeats++;                     /* a same-pitch re-strike: the stutter */
            }
            if (st === 13 || st === 15)
                if (got !== REST) throw new Error(`cut at st${st} did not cut: ${got}`);
        }
        if (note(0, bar * 16 + 12) !== ANCHOR + 6 || note(0, bar * 16 + 14) !== ANCHOR + 5)
            throw new Error(`bar ${bar + 1}: the G–F# tail is not there`);
    }
    if (repeats < 18)
        throw new Error('only ' + repeats + ' same-pitch re-strikes, the stutter is gone');
    for (let st = 0; st < 64; st++)
        if (note(3, st) === TIE)
            throw new Error('drum step ' + st + ' reads back as a TIE');
    console.log(`SLENG-BOUNCE-OK (${attacks} bass attacks over the four bars, ` +
        `${repeats} same-pitch re-strikes, the tail cut short; drums never tie)`);
})().catch(err => { console.error('FAIL:', err.message); process.exit(1); });
