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
            # The Dub controls are part of this same firmware emulator page.
            assert page.locator("#dub-console").is_visible()
            assert page.locator("#dub-enabled").count() == 1
            assert page.locator("#dub-siren").count() == 1
            assert page.locator("#dub-skank").count() == 1
            assert page.locator("#dub-steps button").count() == 16
            assert page.locator("#dub-console [data-dub-band]").count() == 4
            assert page.locator("#dub-presets button").count() == 5
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
