#!/usr/bin/env python3
"""RIDDIM probe v2: per-knob ground truth on the firmware path.

For every knob (K1..K4 = enc 3..6) on the RDM page: turn once, hash the LCD
(did the selection change?), press OCT+, dump the four tracks (did the load
land?).  Also plays at the end and measures the audio.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import sys
import time
import hashlib
import base64

OUT = Path(__file__).resolve().parents[1] / "build" / "riddim-probe"
OUT.mkdir(parents=True, exist_ok=True)
URL = sys.argv[1] if len(sys.argv) > 1 else None


def lcd(page):
    png = page.evaluate("""() => {
        const c = document.getElementById('screen');
        return c ? c.toDataURL('image/png') : '';
    }""")
    return hashlib.md5(png.split(",", 1)[1].encode()).hexdigest()[:8] if png else "?"


def shot(page, name):
    png = page.evaluate("""() => {
        const c = document.getElementById('screen');
        return c ? c.toDataURL('image/png') : '';
    }""")
    if png:
        (OUT / f"{name}.png").write_bytes(base64.b64decode(png.split(",", 1)[1]))


def seq_counts(page):
    page.evaluate("() => { dubSeqRefresh(); }")
    time.sleep(0.35)
    return page.evaluate("""() => {
        if (!dubSeqNotes) return null;
        const c = [0, 0, 0, 0];
        for (let t = 0; t < 4; t++)
            for (let s = 0; s < 64; s++)
                if (dubSeqNotes[t * 64 + s] !== 255) c[t]++;
        return { counts: c, len: dubSeqLen };
    }""")


def rms(page, ms):
    return page.evaluate("""async (ms) => {
        const acc = new Float32Array(2048);
        let sum = 0, n = 0;
        const t0 = performance.now();
        while (performance.now() - t0 < ms) {
            window.__an.getFloatTimeDomainData(acc);
            for (let i = 0; i < acc.length; i++) sum += acc[i] * acc[i];
            n += acc.length;
            await new Promise(r => setTimeout(r, 40));
        }
        return Math.sqrt(sum / n);
    }""", ms)


def press(page, btn, hold=160):
    page.evaluate(f"btnDown({btn})")
    page.wait_for_timeout(hold)
    page.evaluate(f"btnUp({btn})")


def main():
    url = URL or "https://altessproduction.github.io/sloop-dub-fm1/dub/"
    print("URL:", url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        page = browser.new_context(viewport={"width": 1400, "height": 1000}).new_page()
        page.on("pageerror", lambda e: print("PAGE ERROR:", e))
        page.goto(url, wait_until="networkidle")
        page.locator("#power").click()
        time.sleep(2.6)
        page.evaluate("""() => {
            window.__an = ctx.createAnalyser();
            window.__an.fftSize = 2048;
            node.connect(window.__an);
        }""")

        press(page, 8, 1200)      # long HOME: the menu opens
        time.sleep(0.5)
        for _ in range(10):
            page.evaluate("enc(0, 1)")
            page.wait_for_timeout(70)
        time.sleep(0.4)
        shot(page, "v2-0-rdm")
        h0 = lcd(page)
        print("RDM page LCD:", h0)

        # K1: one turn -> does the RIDDIM name change?
        page.evaluate("enc(3, 1)")
        time.sleep(0.35)
        h1 = lcd(page)
        shot(page, "v2-1-k1-turned")
        print(f"after K1 +1: {h1}  name {'CHANGED' if h1 != h0 else 'UNCHANGED!'}")

        # K1: one more turn
        page.evaluate("enc(3, 1)")
        time.sleep(0.35)
        h2 = lcd(page)
        shot(page, "v2-2-k1-turned2")
        print(f"after K1 +2: {h2}  name {'CHANGED' if h2 != h1 else 'UNCHANGED!'}")

        # OCT+ on the RDM page: the whole riddim must land in all four tracks
        press(page, 1)
        time.sleep(0.3)
        shot(page, "v2-3-oct")
        print("after OCT+ LCD:", lcd(page), "(a RIDDIM LOADED message flashes)")
        time.sleep(1.3)
        print("1.3s later LCD:", lcd(page), "(the message cleared)")
        sc = seq_counts(page)
        print(f"sequence after OCT+: counts(bass/sknk/mel/drum)={sc['counts'] if sc else None} len={sc['len'] if sc else None}")

        # K2 + OCT+: the bass motif must replace track 1 only
        page.evaluate("enc(4, 1)")
        time.sleep(0.3)
        hb = lcd(page)
        shot(page, "v2-4-k2")
        print(f"after K2 +1: {hb}  {'CHANGED' if hb != h2 else 'UNCHANGED!'}")
        press(page, 1)
        time.sleep(0.5)
        sc = seq_counts(page)
        print(f"sequence after K2+OCT+: {sc['counts'] if sc else None} len={sc['len'] if sc else None}")

        # K3 + OCT+: the skank motif must replace track 2 only
        page.evaluate("enc(5, 1)")
        time.sleep(0.3)
        press(page, 1)
        time.sleep(0.5)
        sc = seq_counts(page)
        print(f"sequence after K3+OCT+: {sc['counts'] if sc else None} len={sc['len'] if sc else None}")

        # K4 + OCT+: the drum motif must replace track 4 only
        page.evaluate("enc(6, 1)")
        time.sleep(0.3)
        press(page, 1)
        time.sleep(0.5)
        sc = seq_counts(page)
        print(f"sequence after K4+OCT+: {sc['counts'] if sc else None} len={sc['len'] if sc else None}")

        # PLAY: does it sound?
        press(page, 12)
        time.sleep(0.5)
        r = rms(page, 2000)
        print(f"PLAY: rms {r:.4f} -> {'SOUND' if r > 0.02 else 'SILENT!'}")
        press(page, 12)
        browser.close()


if __name__ == "__main__":
    main()
