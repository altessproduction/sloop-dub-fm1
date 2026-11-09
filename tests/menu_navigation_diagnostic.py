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
    server = ThreadingHTTPServer(("127.0.0.1", 8767), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto("http://127.0.0.1:8767/dub/", wait_until="networkidle")
            page.click("#power")
            page.wait_for_timeout(2600)
            page.keyboard.down("7")
            page.wait_for_timeout(1200)
            page.keyboard.up("7")
            page.wait_for_timeout(600)
            page.screenshot(path=str(OUT / "menu_diag_home.png"))
            for i in range(1, 9):
                page.keyboard.press("ArrowUp")
                page.wait_for_timeout(250)
                page.screenshot(path=str(OUT / f"menu_diag_up_{i}.png"))
            browser.close()
    finally:
        server.shutdown()
    print("menu navigation diagnostic completed")

if __name__ == "__main__":
    main()
