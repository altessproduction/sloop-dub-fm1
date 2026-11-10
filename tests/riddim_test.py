#!/usr/bin/env python3
"""RIDDIM page regression (2.9.16, faceplate-driven — the old console is gone):

1. The menu's RDM page: KN1 picks a riddim, OCT+ loads it — the sequencer's steps
   change (the emu_dbg pattern hash proves the load).
2. PLAY starts the transport while the firmware menu is open (the 2.9.4 fix: the menu
   swallowed PLAY, so a riddim loaded on its page could never be heard).
The firmware's own state is read through the emu_dbg probe (21 = a hash of the four
tracks' first steps, 0 = playing, 17 menu open, 22 the menu page)."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
import os

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "dub-emulator-test"
OUT.mkdir(parents=True, exist_ok=True)
fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main():
    os.chdir(ROOT / "docs")
    server = ThreadingHTTPServer(("127.0.0.1", 8767), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required", "--no-proxy-server"])
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto("http://127.0.0.1:8767/dub/", wait_until="networkidle")
            page.click("#power")
            page.wait_for_timeout(2200)

            def dbg(idx):
                return page.evaluate(f"window.emuDbg ? emuDbg({idx}) : null")

            for _ in range(50):
                if dbg(17) is not None:
                    break
                page.wait_for_timeout(200)
            check(dbg(17) is not None, "the dbg probe answers")

            page.keyboard.down("7")
            page.wait_for_timeout(900)
            page.keyboard.up("7")
            page.wait_for_timeout(300)
            check(dbg(17) == 1, "HOME held opens the menu")
            for _ in range(16):
                if dbg(22) == 11:                   # MS_RDM
                    break
                page.keyboard.press("ArrowUp")
                page.wait_for_timeout(120)
            check(dbg(22) == 11, "SELECT walks to RDM (the riddim page)")
            page.screenshot(path=str(OUT / "face_rdm.png"))

            h0 = dbg(21)
            check(h0 is not None, "the pattern hash reads")
            page.evaluate("node.port.postMessage({t:'enc', e:2, steps:2})")   # KN1: the riddim moves
            page.wait_for_timeout(200)
            page.keyboard.down("x")                 # OCT+ on the RIDDIM row: the load
            page.wait_for_timeout(250)
            page.keyboard.up("x")
            page.wait_for_timeout(600)
            h1 = dbg(21)
            check(h1 is not None and h1 != h0, f"OCT+ loaded the riddim: the steps changed ({h0} -> {h1})")
            page.screenshot(path=str(OUT / "face_rdm_loaded.png"))

            page.keyboard.press(" ")
            page.wait_for_timeout(900)
            check(dbg(0) == 1, "PLAY runs the transport with the menu open (the 2.9.4 fix)")
            page.screenshot(path=str(OUT / "face_rdm_playing.png"))
            page.keyboard.press(" ")
            page.wait_for_timeout(400)
            check(dbg(0) == 0, "PLAY again stops")
            browser.close()
    finally:
        server.shutdown()
    if fails:
        raise SystemExit(f"{len(fails)} check(s) failed")
    print("riddim scenario completed")


if __name__ == "__main__":
    main()
