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
            browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
            context = browser.new_context(
                bypass_csp=True,
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            page.on("requestfailed", lambda r: failed.append({"url": r.url, "failure": r.failure}))
            page.on("response", lambda r: responses.append({"url": r.url, "status": r.status}))
            page.goto("http://127.0.0.1:8765/dub/", wait_until="networkidle")
            assert page.evaluate("document.readyState") == "complete"

            assert page.locator("#dub-app").is_visible()
            assert page.locator("#seq-grid button").count() == 64
            assert page.locator(".band-card").count() == 4
            assert page.locator("#preset-grid button").count() == 5
            duplicate_ids = page.evaluate("""() => {
              const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
              return ids.filter((x,i)=>ids.indexOf(x)!==i);
            }""")
            assert duplicate_ids == [], duplicate_ids

            page.click("#seq-length-32")
            assert page.locator("#seq-grid button:disabled").count() == 32
            page.click("#seq-length-64")
            assert page.locator("#seq-grid button:disabled").count() == 0
            page.click("#seq-grid button[data-step='1']")
            assert page.locator("#seq-grid button[data-step='1']").get_attribute("aria-pressed") == "true"

            page.click("#preset-siren")
            assert "DUB SIREN" in page.locator("#preset-name").inner_text()
            page.click("#siren-trigger")
            assert page.locator("#siren-trigger").get_attribute("aria-pressed") == "true"
            page.click("#siren-trigger")
            assert page.locator("#siren-trigger").get_attribute("aria-pressed") == "false"

            page.click("#skank-pad")
            assert page.locator("#skank-readout").inner_text().count("+") == 2
            page.click("#iso-toggle")
            assert page.locator("#iso-toggle").get_attribute("aria-pressed") == "true"
            page.click("#mute-sub")
            assert page.locator("#mute-sub").get_attribute("aria-pressed") == "true"
            page.click("#mute-sub")

            page.click("#play-toggle")
            assert page.locator("#play-toggle").get_attribute("aria-pressed") == "true"
            page.wait_for_timeout(350)
            assert page.locator("#step-position").inner_text().startswith("STEP")
            page.click("#play-toggle")

            for w, h in [(390, 844), (768, 1024), (1280, 800), (1920, 1080)]:
                page.set_viewport_size({"width": w, "height": h})
                page.wait_for_timeout(150)
                assert not page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"), f"overflow at {w}x{h}"

            page.set_viewport_size({"width": 1280, "height": 800})
            page.goto("http://127.0.0.1:8765/dub/", wait_until="networkidle")
            page.screenshot(path=str(OUT / "desktop_top.png"))
            page.locator("#isolator").scroll_into_view_if_needed()
            page.screenshot(path=str(OUT / "desktop_isolator.png"))
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto("http://127.0.0.1:8765/dub/", wait_until="networkidle")
            page.screenshot(path=str(OUT / "mobile_top.png"))

            buttons = page.locator("button")
            for i in range(buttons.count()):
                button = buttons.nth(i)
                assert button.inner_text().strip() or button.get_attribute("aria-label"), f"unnamed button {i}"
            assert not errors, errors
            assert not page_errors, page_errors
            assert not failed, failed
            http_errors = [r for r in responses if r["status"] >= 400]
            assert not http_errors, http_errors
            browser.close()
    finally:
        server.shutdown()
    print("SLOOP Dub emulator browser checks: passed")


if __name__ == "__main__":
    main()
