#!/usr/bin/env python3
"""Browser checks for the SLOOP Dub emulator page (Tier 2)."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
import os
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "dub-emulator-test"
OUT.mkdir(parents=True, exist_ok=True)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve():
    os.chdir(ROOT / "docs")
    server = ThreadingHTTPServer(("127.0.0.1", 8765), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    return server


def main():
    server = serve()
    time.sleep(0.2)
    errors, page_errors, failed, responses = [], [], [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            page.on("requestfailed", lambda r: failed.append({"url": r.url, "failure": r.failure}))
            page.on("response", lambda r: responses.append({"url": r.url, "status": r.status}))
            page.goto("http://127.0.0.1:8765/dub/", wait_until="networkidle")
            assert page.evaluate("document.readyState") == "complete"

            # The page is the complete FM-1 faceplate, not the former Dub demo.
            assert page.locator("#device").is_visible()
            assert page.locator("#power").is_visible()
            assert page.locator("#screen").count() == 1
            assert page.locator(".cap").count() == 8
            assert page.locator(".btn").count() == 14
            assert page.locator(".pill").count() == 27
            assert "FIRMWARE RÉEL" in page.locator("#firmware-badge").inner_text()
            assert "SLOOP DUB" in page.locator("#title").inner_text()
            assert "FELUCCA" not in page.locator("body").inner_text()
            # The Dub controls are part of this same firmware emulator page: the tabbed
            # mirror of the firmware's Dub pages (long HOME press: DUB SIR SR2 SKANK DSEQ RDM ISO).
            assert page.locator("#dub-console").is_visible()
            assert page.locator(".dub-tab").count() == 8
            assert page.locator(".dub-page").count() == 8
            assert page.locator(".dub-page.on").count() == 1
            assert page.locator("#dub-enabled").count() == 1
            assert page.locator("#dub-mix").count() == 1
            assert page.locator("#dub-siren").count() == 1
            assert page.locator("#dub-siren-freq").count() == 1
            assert page.locator("#dub-siren-depth").count() == 1
            assert page.locator("#dub-siren-rate").count() == 1
            assert page.locator("#dub-siren-type option").count() == 5
            assert page.locator("#dub-siren-wave option").count() == 5
            assert page.locator("#dub-siren-sym").count() == 1
            assert page.locator("#dub-siren-send").count() == 1
            assert page.locator("#dub-siren-level").count() == 1
            assert page.locator("#dub-skank").count() == 1
            assert page.locator("#dub-skank-vel").count() == 1
            assert page.locator("#dub-root option").count() == 12
            assert page.locator("#dub-quality option").count() == 8
            assert page.locator("#dub-octave option").count() == 3
            # 2.9.4: the DSQ view is built from JS: four tracks x 64 steps plus their labels
            assert page.locator("#dub-steps button").count() == 256
            assert page.locator(".dub-trk-label").count() == 4
            assert page.locator("#dub-trks button").count() == 4
            assert page.locator("#dub-console [data-dub-band]").count() == 4
            assert page.locator("#dub-presets button").count() == 5
            # The tabs mirror the LCD: one tab shows its page, the others wait.
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "dub"
            page.click('.dub-tab[data-dub-page="sir"]')
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "sir"
            assert page.locator('[data-dub-panel="sir"]').is_visible()
            assert not page.locator('[data-dub-panel="dub"]').is_visible()
            page.click('.dub-tab[data-dub-page="sr2"]')
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "sr2"
            assert page.locator('[data-dub-panel="sr2"]').is_visible()
            page.click('.dub-tab[data-dub-page="dub"]')
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "dub"
            # 2.9.3: the PRESET tab: four selectors of the dub sound banks and their loads
            page.click('.dub-tab[data-dub-page="prs"]')
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "prs"
            for sel_id, n in [("dub-sbass", 8), ("dub-sskank", 8), ("dub-smel", 8), ("dub-skit", 8)]:
                assert page.locator("#" + sel_id + " option").count() == n
            for b in ["dub-sbass-load", "dub-sskank-load", "dub-smel-load", "dub-skit-load"]:
                assert page.locator("#" + b).count() == 1
            page.select_option("#dub-sskank", "3")          # REGGAE ORG
            page.click("#dub-sskank-load")
            page.wait_for_timeout(400)
            page.select_option("#dub-skit", "1")            # DUST
            page.click("#dub-skit-load")
            page.wait_for_timeout(300)
            page.click('.dub-tab[data-dub-page="dub"]')
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "dub"
            # 2.9.2: the RIDDIM tab: four selectors of the ten riddims, the four load buttons
            page.click('.dub-tab[data-dub-page="rdm"]')
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "rdm"
            assert page.locator("#dub-riddim option").count() == 10
            assert page.locator("#dub-rbass option").count() == 10
            assert page.locator("#dub-rskank option").count() == 10
            assert page.locator("#dub-rdrum option").count() == 10
            for b in ["dub-riddim-load", "dub-rbass-load", "dub-rskank-load", "dub-rdrum-load"]:
                assert page.locator("#" + b).count() == 1
            page.select_option("#dub-riddim", "3")
            page.click("#dub-riddim-load")
            page.wait_for_timeout(400)
            page.select_option("#dub-rdrum", "5")
            page.click("#dub-rdrum-load")
            page.wait_for_timeout(300)
            page.click('.dub-tab[data-dub-page="dub"]')
            assert page.locator(".dub-page.on").get_attribute("data-dub-panel") == "dub"
            duplicate_ids = page.evaluate("""() => {
              const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
              return ids.filter((x,i)=>ids.indexOf(x)!==i);
            }""")
            assert duplicate_ids == [], duplicate_ids

            # Boot the real firmware in the AudioWorklet and exercise hardware I/O.
            page.click("#power")
            page.wait_for_timeout(1400)
            assert page.locator("#power").count() == 0
            assert page.locator("#screen").evaluate("c => c.width") == 240
            page.keyboard.down("a")
            page.wait_for_timeout(80)
            page.keyboard.up("a")
            page.keyboard.press("ArrowUp")
            page.keyboard.press(" ")
            page.wait_for_timeout(120)
            assert page.locator("#device").is_visible()

            for w, h in [(390, 844), (768, 1024), (1280, 800), (1920, 1080)]:
                page.set_viewport_size({"width": w, "height": h})
                page.wait_for_timeout(150)
                assert not page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"), f"overflow at {w}x{h}"

            page.set_viewport_size({"width": 1280, "height": 800})
            page.goto("http://127.0.0.1:8765/dub/", wait_until="networkidle")
            page.screenshot(path=str(OUT / "desktop_top.png"))
            page.locator("#device").scroll_into_view_if_needed()
            page.screenshot(path=str(OUT / "desktop_device.png"))
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto("http://127.0.0.1:8765/dub/", wait_until="networkidle")
            page.screenshot(path=str(OUT / "mobile_top.png"))

            assert not errors, errors
            assert not page_errors, page_errors
            assert not failed, failed
            http_errors = [r for r in responses if r["status"] >= 400]
            assert not http_errors, http_errors
            browser.close()
    finally:
        server.shutdown()
    print("SLOOP Dub full FM-1 firmware emulator browser checks: passed")


if __name__ == "__main__":
    main()
