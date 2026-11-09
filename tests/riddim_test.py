#!/usr/bin/env python3
"""RIDDIM page regression (2.9.4): what OCT+ / CHARGER loads must be visible and audible.

1. The web RDM tab's CHARGER TOUT loads the whole riddim; the DSQ tab's four-track view
   shows the loaded steps (the readback), the length select follows the sequence's 64.
2. PLAY starts the transport while the firmware menu is open (the 2.9.4 fix: the menu
   swallowed PLAY, so a riddim loaded on its page could never be heard).
3. A bass / skank / drum pattern load (OCT+ semantics) changes what the sequence plays.
4. The playhead moves while playing, the RDM tab tells the load ("CHARGÉ ...").
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
import os
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "riddim-test"
OUT.mkdir(parents=True, exist_ok=True)
PORT = 8772


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    os.chdir(ROOT / "docs")
    server = ThreadingHTTPServer(("127.0.0.1", PORT), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    return server


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


def active_steps(page, trk=None):
    sel = f'[data-trk="{trk}"]' if trk is not None else ""
    return page.evaluate(f"document.querySelectorAll('#dub-steps button.active{sel}').length")


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else f"http://127.0.0.1:{PORT}/dub/"
    live = url.startswith("http") and "127.0.0.1" not in url and "localhost" not in url
    server = serve() if not live else None
    if live:
        time.sleep(0.2)
    else:
        time.sleep(0.2)
    errs, fails = [], []
    def check(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
        if not ok:
            fails.append(name)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required",
                                                         "--no-proxy-server"])
        page = browser.new_context(viewport={"width": 1400, "height": 1000}).new_page()
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs.append("PAGE: " + str(e)))
        page.goto(url, wait_until="networkidle")
        page.locator("#power").click()
        time.sleep(2.6)
        page.evaluate("""() => {
            window.__an = ctx.createAnalyser();
            window.__an.fftSize = 2048;
            node.connect(window.__an);
        }""")

        # 1. the DSQ view exists: four tracks x 64 steps, built from JS
        page.locator('.dub-tab[data-dub-page="dseq"]').click()
        time.sleep(0.4)
        check("DSQ grid: 256 step buttons", page.locator("#dub-steps button").count() == 256,
              f"({page.locator('#dub-steps button').count()})")
        check("DSQ grid: 4 track labels", page.locator(".dub-trk-label").count() == 4)

        # 2. load the whole riddim from the RDM tab; the DSQ view must show it
        page.locator('.dub-tab[data-dub-page="rdm"]').click()
        page.evaluate("() => { document.getElementById('dub-riddim').value = '3'; }")   # DUBWALK
        page.locator("#dub-riddim-load").click()
        time.sleep(0.4)
        check("RDM tab tells the load", "CHARGÉ" in (page.locator("#dub-riddim-status").inner_text() or ""),
              f"('{page.locator('#dub-riddim-status').inner_text()}')")
        page.locator('.dub-tab[data-dub-page="dseq"]').click()
        time.sleep(0.4)
        n_bass, n_dr = active_steps(page, 0), active_steps(page, 3)
        check("DSQ readback: the riddim's bass steps", n_bass > 0, f"({n_bass} steps)")
        check("DSQ readback: the riddim's drum steps", n_dr > 0, f"({n_dr} steps)")
        check("DSQ length follows the 64-step riddim",
              page.evaluate("document.getElementById('dub-length').value") == "64")

        # 3. PLAY while the firmware menu is open (the 2.9.4 fix): the riddim must sound
        press(page, 8, 1200)                     # long HOME: the menu opens
        time.sleep(0.5)
        press(page, 12)                          # PLAY inside the menu
        time.sleep(0.5)
        r_menu = rms(page, 2200)
        check("PLAY inside the menu sounds the riddim", r_menu > 0.02, f"(rms {r_menu:.4f})")
        # the playhead runs (a .play column follows)
        moved = page.evaluate("""() => new Promise(res => {
            const a = document.querySelector('#dub-steps button.play')?.dataset.step;
            setTimeout(() => {
                const b = document.querySelector('#dub-steps button.play')?.dataset.step;
                res(a !== undefined && b !== undefined && a !== b);
            }, 500);
        })""")
        check("the playhead moves while playing", moved)
        press(page, 12)                          # PLAY again: stop
        time.sleep(0.4)

        # 4. pattern loads change what the sequence holds (OCT+ semantics, per track)
        page.locator('.dub-tab[data-dub-page="rdm"]').click()
        page.evaluate("() => { document.getElementById('dub-rbass').value = '5'; }")    # LOVERS bass
        page.locator("#dub-rbass-load").click()
        time.sleep(0.3)
        page.evaluate("() => { document.getElementById('dub-rskank').value = '6'; }")   # MEDITATE skank
        page.locator("#dub-rskank-load").click()
        time.sleep(0.3)
        page.evaluate("() => { document.getElementById('dub-rdrum').value = '7'; }")    # SKANKIN drums
        page.locator("#dub-rdrum-load").click()
        time.sleep(0.3)
        check("the load status names the track", "PISTE" in (page.locator("#dub-riddim-status").inner_text() or ""),
              f"('{page.locator('#dub-riddim-status').inner_text()}')")
        press(page, 12)                          # PLAY from the menu (menu is closed here: web flow)
        time.sleep(0.4)
        r_pat = rms(page, 2200)
        check("the recombined patterns sound", r_pat > 0.02, f"(rms {r_pat:.4f})")
        press(page, 12)
        time.sleep(0.3)

        # 5. the firmware path on the LCD: RDM page, KNOB 1 (enc 2) selects, OCT+ loads,
        #    all four tracks land in the sequence (the DSQ view reads the wasm back).
        #    Deterministic: close whatever menu state step 3 left (a long HOME over an
        #    open menu goes to ABOUT, where every input is swallowed), reopen, clamp to
        #    the first page with 15 lefts, then 10 rights is the RDM page (11/13).
        press(page, 0)                           # OCT- closes the menu (or ABOUT -> menu)
        time.sleep(0.3)
        press(page, 0)                           # (a second one if ABOUT ate the first)
        time.sleep(0.3)
        press(page, 8, 1200)                     # long HOME: the menu opens
        time.sleep(0.5)
        for _ in range(15):
            page.evaluate("enc(0, -1)")          # hard left: the SCR page (clamped)
            page.wait_for_timeout(60)
        for _ in range(10):
            page.evaluate("enc(0, 1)")           # SCR 1/13 -> RDM 11/13
            page.wait_for_timeout(60)
        time.sleep(0.3)
        page.evaluate("enc(2, 1)")               # KNOB 1 (enc 2): the next riddim
        time.sleep(0.2)
        page.evaluate("enc(2, 1)")               # one more: the selection is 2 = ROCKERS
        time.sleep(0.2)
        lcd0 = page.evaluate("document.getElementById('screen').toDataURL('image/png')")
        press(page, 1)                           # OCT+ on the RDM page: load
        time.sleep(0.25)                         # a few frames paint the header's message
        lcd1 = page.evaluate("document.getElementById('screen').toDataURL('image/png')")
        check("the menu tells the load (a RIDDIM LOADED flash)", lcd1 != lcd0)
        time.sleep(0.6)                          # the message's 40 frames run out
        page.evaluate("dubSeqRefresh()")         # the DSQ view reads the sequence back
        time.sleep(0.5)
        n_fw = [active_steps(page, t) for t in range(4)]
        check("firmware OCT+ loads the whole ROCKERS (all four tracks, exact)",
              n_fw == [24, 24, 6, 36], f"({n_fw})")
        check("firmware OCT+ load kept the sequence at 64",
              page.evaluate("document.getElementById('dub-length').value") == "64")

        browser.close()
    if server:
        server.shutdown()

    if errs:
        print("console errors:", errs[:6])
    print(f"\n{'ALL PASS' if not fails and not errs else 'FAILURES: ' + ', '.join(fails + ['console'] if errs else fails)}")
    return 1 if fails or errs else 0


if __name__ == "__main__":
    sys.exit(main())
