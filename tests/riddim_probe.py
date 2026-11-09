#!/usr/bin/env python3
"""Live probe: the exact user flow on the RIDDIM page, LCD screenshots at each step.

Flow: power -> long HOME -> RDM page -> KN1 select -> OCT+ load -> DSQ page -> PLAY.
Each step is screenshotted (LCD canvas) and the audio RMS is measured after PLAY.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import sys
import time
import base64

OUT = Path(__file__).resolve().parents[1] / "build" / "riddim-probe"
OUT.mkdir(parents=True, exist_ok=True)
URL = sys.argv[1] if len(sys.argv) > 1 else "https://altessproduction.github.io/sloop-dub-fm1/dub/"


def shot(page, name):
    png = page.evaluate("""() => {
        const c = document.getElementById('screen');
        return c ? c.toDataURL('image/png') : '';
    }""")
    if png:
        (OUT / f"{name}.png").write_bytes(base64.b64decode(png.split(",", 1)[1]))
        print(f"  shot: {name}.png")


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


def press(page, btn, hold=140):
    page.evaluate(f"btnDown({btn})")
    page.wait_for_timeout(hold)
    page.evaluate(f"btnUp({btn})")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        page = browser.new_context(viewport={"width": 1400, "height": 1000}).new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(URL, wait_until="networkidle")
        page.locator("#power").click()
        time.sleep(2.6)
        page.evaluate("""() => {
            window.__an = ctx.createAnalyser();
            window.__an.fftSize = 2048;
            node.connect(window.__an);
        }""")

        # 1. open the menu, walk to the RDM page: 10 rights from SCR 1/13 -> RDM 11/13
        press(page, 8, 1200)
        time.sleep(0.5)
        for _ in range(10):
            page.evaluate("enc(0, 1)")   # one page right
            page.wait_for_timeout(80)
        time.sleep(0.4)
        shot(page, "01-rdm-page")          # must show the header "RDM 11/13"

        # 2. turn KN1 twice: the riddim selection changes
        page.evaluate("enc(3, 1)")
        time.sleep(0.2)
        page.evaluate("enc(3, 1)")
        time.sleep(0.3)
        shot(page, "02-kn1-selected")

        # 3. OCT+ loads the whole riddim
        press(page, 1)
        time.sleep(0.4)
        shot(page, "03-after-oct-plus")    # does the LCD show ANY load feedback?

        # 4. walk left to the DSQ page and look at the sequence
        page.evaluate("enc(0, -1)")
        time.sleep(0.4)
        shot(page, "04-dsq-page")          # does the DSQ page show the loaded steps?

        # 5. PLAY from the DSQ page: does it sound?
        press(page, 12)
        time.sleep(0.5)
        r = rms(page, 2200)
        print(f"  PLAY after firmware load: rms {r:.4f}  -> {'SOUND' if r > 0.02 else 'SILENT!'}")
        shot(page, "05-playing")
        press(page, 12)
        time.sleep(0.3)

        # 6. the web console's own readback: the DSQ tab's steps per track
        page.locator('.dub-tab[data-dub-page="dseq"]').click()
        time.sleep(0.4)
        counts = page.evaluate("""() => [0,1,2,3].map(t =>
            document.querySelectorAll(`#dub-steps button.active[data-trk="${t}"]`).length)""")
        print(f"  DSQ tab readback: bass/skank/mel/drum active steps = {counts}")
        length = page.evaluate("document.getElementById('dub-length').value")
        print(f"  DSQ length select = {length}")

        # 7. the RDM web tab: what does the status line say (it reflects the last firmware load?)
        page.locator('.dub-tab[data-dub-page="rdm"]').click()
        time.sleep(0.3)
        st = page.locator("#dub-riddim-status").inner_text()
        print(f"  RDM tab status: '{st}'")

        browser.close()
    if errs:
        print("PAGE ERRORS:", errs[:5])
    print("done ->", OUT)


if __name__ == "__main__":
    main()
