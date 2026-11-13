/* Verify the note repetitions after the dub_tracks_load fix: a loaded riddim's bass
 * strikes again on every written note — the same-pitch repeats too (the Sleng Teng's
 * bounce, the MT-40's plucks) — and only the rests hold (TIE, read back as 254).
 * The Sleng Teng's bars 1-2 play the sleng groove, bars 3-4 the sleng_b turnaround;
 * steps 3-4 and 11-12 (sleng) and 8, 11-12 (sleng_b) are the same-pitch repeats the
 * old load glued into one held note.
 *   node scripts/verify_sleng_bounce.js [path/to/sloop.wasm]
 */
'use strict';
const fs = require('fs');
const path = require('path');

const WASM = process.argv[2] || path.join(__dirname, '..', 'docs', 'dub', 'sloop.wasm');
const SLENG = 16;                                  /* the bank's index of SLENG TENG */
const TIE = 254, REST = 255;
const ROOTS = [37, 35, 33, 35];                    /* C#m B A B, one root a bar */
/* the two bass grooves (tools/gen_riddims.py), {step: degree} */
const GROOVES = [
    { 0: 0, 3: 0, 4: 0, 6: 12, 8: 0, 11: 0, 12: 0, 14: 10 },    /* sleng: bars 1-2 */
    { 0: 12, 2: 10, 4: 7, 6: 0, 8: 0, 11: 0, 12: 0, 14: 7 },    /* sleng_b: bars 3-4 */
];

/* the load's semantics (seq.c dub_tracks_load, after the fix): a written note is an
 * attack (even the same pitch), a rest holds the current note (TIE) or stays silent */
function expect_bar(groove, root) {
    const out = [];
    let held = REST;
    for (let st = 0; st < 16; st++) {
        if (groove[st] !== undefined) {
            held = root + groove[st];
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

    let attacks = 0, repeats = 0;
    for (let bar = 0; bar < 4; bar++) {
        const want = expect_bar(GROOVES[bar < 2 ? 0 : 1], ROOTS[bar]);
        for (let st = 0; st < 16; st++) {
            const got = note(0, bar * 16 + st);
            if (got !== want[st])
                throw new Error(`bass bar ${bar + 1} st${st}: got ${got}, want ${want[st]}`);
            if (got !== TIE && got !== REST) {
                attacks++;
                if (st > 0 && want[st - 1] !== REST && want[st - 1] !== TIE && want[st - 1] === got)
                    repeats++;                     /* a same-pitch re-strike: the bounce */
            }
        }
    }
    if (repeats < 4)
        throw new Error('only ' + repeats + ' same-pitch re-strikes, the bounce is gone');
    for (let st = 0; st < 64; st++)
        if (note(3, st) === TIE)
            throw new Error('drum step ' + st + ' reads back as a TIE');
    console.log(`SLENG-BOUNCE-OK (${attacks} bass attacks over the four bars, ` +
        `${repeats} same-pitch re-strikes; rests hold, drums never tie)`);
})().catch(err => { console.error('FAIL:', err.message); process.exit(1); });
