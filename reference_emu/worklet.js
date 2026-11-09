/* SPDX-License-Identifier: GPL-3.0-only
 * SLOOP web emulator: the AudioWorklet hosts the whole firmware (wasm).
 * process() renders audio with mix_block; every few blocks a UI frame runs
 * and the framebuffer + LED state are posted to the main thread. */
class SloopProcessor extends AudioWorkletProcessor {
    constructor(options) {
        super();
        const mod = new WebAssembly.Module(options.processorOptions.wasmBytes);
        this.e = new WebAssembly.Instance(mod, {}).exports;
        const img = options.processorOptions.flashImage;
        if (img && img.byteLength) {        // restore the saved flash before boot
            const fl = new Uint8Array(this.e.memory.buffer, this.e.emu_flash_ptr(), this.e.emu_flash_size());
            fl.set(new Uint8Array(img, 0, Math.min(img.byteLength, fl.length)));
        }
        this.lastFlashGen = 0;
        this.e.emu_init();
        this.lastFlashGen = this.e.emu_flash_gen();   // boot-time writes need no save
        this.fbPtr = this.e.emu_fb_ptr();
        this.audioPtr = this.e.emu_audio_ptr();
        this.ledPtr = this.e.emu_led_ptr();
        this.ledDimPtr = this.e.emu_led_dim_ptr();
        this.lastGen = -1;
        this.blocks = 0;
        this.running = true;
        this.port.onmessage = (ev) => {
            const m = ev.data;
            if (m.t === 'input') this.e.emu_input(m.notes, m.buttons);
            else if (m.t === 'enc') this.e.emu_enc(m.e, m.steps);
            else if (m.t === 'start') this.e.emu_start();
            else if (m.t === 'adc') this.e.emu_adc_set(m.ch, m.v);
            else if (m.t === 'midi') this.e.emu_midi(m.p);
            else if (m.t === 'dub-enable') this.e.emu_dub_enable(m.on ? 1 : 0);
            else if (m.t === 'dub-siren') {
                this.e.emu_dub_siren(m.level || 0, m.frequency || 740, m.depth || 96);
                if (m.rate != null && typeof this.e.emu_dub_siren_rate === 'function')
                    this.e.emu_dub_siren_rate(m.rate);   // wasm rebuilt from the Dub pages firmware and later
            }
            else if (m.t === 'dub-siren-type') { if (typeof this.e.emu_dub_siren_type === 'function') this.e.emu_dub_siren_type(m.type || 0); }
            else if (m.t === 'dub-siren-wave') { if (typeof this.e.emu_dub_siren_wave === 'function') this.e.emu_dub_siren_wave(m.wave || 0); }
            else if (m.t === 'dub-siren-sym') { if (typeof this.e.emu_dub_siren_sym === 'function') this.e.emu_dub_siren_sym(m.sym || 0); }
            else if (m.t === 'dub-siren-send') { if (typeof this.e.emu_dub_siren_send === 'function') this.e.emu_dub_siren_send(m.send || 0); }
            else if (m.t === 'dub-siren-freq') { if (typeof this.e.emu_dub_siren_freq === 'function') this.e.emu_dub_siren_freq(m.frequency || 740); }
            else if (m.t === 'dub-siren-depth') { if (typeof this.e.emu_dub_siren_depth === 'function') this.e.emu_dub_siren_depth(m.depth || 96); }
            else if (m.t === 'dub-siren-rate') { if (typeof this.e.emu_dub_siren_rate === 'function') this.e.emu_dub_siren_rate(m.rate || 8); }
            else if (m.t === 'dub-siren-level') {
                if (typeof this.e.emu_dub_siren_level === 'function') this.e.emu_dub_siren_level(m.level || 0);
                else this.e.emu_dub_siren(m.level || 0, 740, 96);   // the old shim's way
            }
            else if (m.t === 'dub-band') this.e.emu_dub_band(m.band || 0, m.gain || 0, m.mute ? 1 : 0);
            else if (m.t === 'dub-mix') { if (typeof this.e.emu_dub_mix === 'function') this.e.emu_dub_mix(m.mix || 0); }
            else if (m.t === 'dub-seq-length') this.e.emu_dub_seq_length(m.length || 16);
            else if (m.t === 'dub-seq-step') {
                if (m.track != null && typeof this.e.emu_dub_riddim_count === 'function')
                    this.e.emu_dub_seq_step(m.track || 0, m.step || 0, m.note || 60, m.velocity || 0);   // 2.9.2's four tracks
                else this.e.emu_dub_seq_step(m.step || 0, m.note || 60, m.velocity || 0);   // the older wasm's single track
            }
            else if (m.t === 'dub-riddim') { if (typeof this.e.emu_dub_riddim_load === 'function') this.e.emu_dub_riddim_load(m.riddim || 0); }   // the RIDDIM page's loads
            else if (m.t === 'dub-seq-dump') {   // (2.9.6) what the SLOOP sequencer's tracks hold:
                                                 // each track's LEN + the 4 tracks' steps (255 rest, 254 tie)
                if (typeof this.e.emu_dub_seq_note === 'function') {
                    const notes = new Uint8Array(4 * 64);
                    const lens = new Uint8Array(4);
                    for (let tr = 0; tr < 4; tr++) {
                        lens[tr] = typeof this.e.emu_dub_seq_track_len === 'function'
                            ? this.e.emu_dub_seq_track_len(tr) : 64;
                        for (let st = 0; st < 64; st++)
                            notes[tr * 64 + st] = this.e.emu_dub_seq_note(tr, st);
                    }
                    this.port.postMessage({ t: 'dub-seq-dump', len: this.e.emu_dub_seq_len(), lens, notes });
                } else this.port.postMessage({ t: 'dub-seq-dump', len: 0, notes: null });
            }
            else if (m.t === 'dub-riddim-track') { if (typeof this.e.emu_dub_riddim_track === 'function') this.e.emu_dub_riddim_track(m.riddim || 0, m.track || 0); }
            else if (m.t === 'dub-sound') { if (typeof this.e.emu_dub_sound_load === 'function') this.e.emu_dub_sound_load(m.role || 0, m.index || 0); }   // the PRESET page's loads
            else if (m.t === 'dub-skank') this.e.emu_dub_skank(m.root || 0, m.quality || 0, m.octave || 3, m.velocity || 100);
            else if (m.t === 'dub-preset') this.e.emu_dub_preset(m.index || 0);
            else if (m.t === 'stop') this.running = false;
        };
        this.postFrame();           // the splash, before audio starts
    }

    postFrame() {
        const gen = this.e.emu_fb_gen();
        const leds = new Uint8Array(this.e.memory.buffer, this.ledPtr, 11).slice();
        const dims = new Uint8Array(this.e.memory.buffer, this.ledDimPtr, 11).slice();
        const seq = this.seqState();        // (2.9.4) the dub sequencer's playhead, for the DSQ view
        if (gen !== this.lastGen) {
            this.lastGen = gen;
            const fb = new Uint16Array(this.e.memory.buffer, this.fbPtr, 240 * 240).slice();
            this.port.postMessage({ t: 'frame', fb, leds, dims, seq }, [fb.buffer]);
        } else {
            this.port.postMessage({ t: 'leds', leds, dims, seq });
        }
    }

    seqState() {                        // (2.9.4) len / playhead / running, an older wasm lacks them
        const e = this.e;
        return typeof e.emu_dub_seq_len === 'function'
            ? { len: e.emu_dub_seq_len(), pos: e.emu_dub_seq_pos(), playing: !!e.emu_dub_seq_playing() }
            : null;
    }

    process(inputs, outputs) {
        const out = outputs[0];
        const n = out[0].length;             // 128
        this.e.emu_render(n);
        const a = new Float32Array(this.e.memory.buffer, this.audioPtr, 2 * n);
        const L = out[0], R = out[1] || out[0];
        for (let i = 0; i < n; i++) {
            L[i] = a[2 * i];
            R[i] = a[2 * i + 1];
        }
        if (++this.blocks % 6 === 0) {       // a UI frame every ~17 ms
            this.e.emu_frame();
            this.postFrame();
        }
        if (this.blocks % 256 === 0) {       // ~0.75 s: ship changed flash to be saved
            const gen = this.e.emu_flash_gen();
            if (gen !== this.lastFlashGen) {
                this.lastFlashGen = gen;
                const fl = new Uint8Array(this.e.memory.buffer, this.e.emu_flash_ptr(), this.e.emu_flash_size()).slice();
                this.port.postMessage({ t: 'flash', data: fl.buffer }, [fl.buffer]);
            }
        }
        return this.running;
    }
}
registerProcessor('sloop', SloopProcessor);
