#!/usr/bin/env python3
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

def main():
    os.chdir(ROOT / "docs")
    server = ThreadingHTTPServer(("127.0.0.1", 8766), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto("http://127.0.0.1:8766/dub/", wait_until="networkidle")
            page.click("#power")
            page.wait_for_timeout(1800)
            # HOME is key 7 in the emulator keyboard map. Hold long enough for BT_HOLD.
            page.keyboard.down("7")
            page.wait_for_timeout(900)
            page.screenshot(path=str(OUT / "menu_home_long.png"))
            page.keyboard.up("7")
            page.wait_for_timeout(250)
            # SELECT encoder is ArrowUp/ArrowDown; advance through sections to DUB, DSEQ, ISO.
            for name, key in [("dub", "ArrowDown"), ("dseq", "ArrowDown"), ("iso", "ArrowDown")]:
                page.keyboard.press(key)
                page.wait_for_timeout(180)
                page.screenshot(path=str(OUT / ("menu_" + name + ".png")))
            # Use K1 (not directly keyboard-mapped) through the browser-side encoder message.
            page.evaluate("""() => { if (window.node) window.node.port.postMessage({t:'enc', e:2, steps:1}); }""")
            page.wait_for_timeout(180)
            browser.close()
    finally:
        server.shutdown()
    print("menu navigation scenario completed")

if __name__ == "__main__":
    main()
