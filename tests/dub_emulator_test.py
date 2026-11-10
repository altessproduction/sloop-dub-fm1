#!/usr/bin/env python3
"""2.9.16: the Dub console is gone — the page is the FM-1 faceplate and the firmware's own
menu, and the fork's features are explained in #dub-manual. The tests read the firmware's
own state through the emu_dbg probe (sloop_wasm.c: 6 sir level, 7 sir active, 11 dly sync,
17 menu open, 19 the siren's level setting, 20 the OCT+ hold armed, 22 the menu page).

The scenario here is the 2.9.16 one: OCT+ held on SIR keeps the siren sounding while
SELECT walks to SR2 and on to DLY; released there it stops; pressed again it re-arms;
DLY's OCT+ has no other life (no mode toggle), the knobs still work under the hold."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
import os

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "dub-emulator-test"
OUT.mkdir(parents=True, exist_ok=True)
OUT2 = ROOT / "build"
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
    server = ThreadingHTTPServer(("127.0.0.1", 8766), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required", "--no-proxy-server"])
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto("http://127.0.0.1:8766/dub/", wait_until="networkidle")

            # the page: no console any more, the feature manual in its place
            check(page.locator("#dub-console").count() == 0, "the Dub console is gone")
            check(page.locator("#dub-manual").count() == 1, "the fork's features are explained below the emulator")
            check("SLOOP DUB — LES FONCTIONS AJOUTÉES" in page.locator("#dub-manual h2").inner_text(),
                  "the manual names the added functions")
            check(page.locator("#device").count() == 1, "the faceplate stays")

            page.click("#power")
            page.wait_for_timeout(2200)

            def dbg(idx):
                return page.evaluate(f"window.emuDbg ? emuDbg({idx}) : null")

            for _ in range(50):                     # the worklet boots, the probe starts answering
                if dbg(17) is not None:
                    break
                page.wait_for_timeout(200)
            check(dbg(17) is not None, "the dbg probe answers (the firmware's own state)")

            # the menu: HOME held opens it, the walk lands on SIR (page 6, MS_SIREN)
            page.keyboard.down("7")
            page.wait_for_timeout(900)
            page.keyboard.up("7")
            page.wait_for_timeout(300)
            check(dbg(17) == 1, "HOME held opens the Dub menu")
            for _ in range(16):
                if dbg(22) == 6:
                    break
                page.keyboard.press("ArrowUp")
                page.wait_for_timeout(120)
            check(dbg(22) == 6, "SELECT walks to SIR (the siren page)")
            page.screenshot(path=str(OUT / "face_sir.png"))

            level = dbg(19)
            check(level is not None and level > 0, f"the siren's level setting is on ({level}, the SR2 row's)")

            # the 2.9.16 hold: OCT+ down, the pages walk, the siren never stops
            page.keyboard.down("x")
            page.wait_for_timeout(400)
            check(dbg(7) == 1, "OCT+ held on SIR: the siren sounds")
            page.keyboard.press("ArrowUp")
            page.wait_for_timeout(250)
            check(dbg(22) == 7, "SELECT walks to SR2 under the held OCT+")
            check(dbg(7) == 1, "the siren keeps sounding across the page")
            page.keyboard.press("ArrowUp")
            page.wait_for_timeout(200)
            page.keyboard.press("ArrowUp")
            page.wait_for_timeout(250)
            check(dbg(22) == 9, "SELECT walks through SKANK on to DLY")
            check(dbg(7) == 1, "the siren still sounds at the delay page")
            page.screenshot(path=str(OUT / "face_dly_siren.png"))

            sync0 = dbg(11)
            page.keyboard.up("x")
            page.wait_for_timeout(300)
            check(dbg(7) == 0, "OCT+ released on DLY: the siren stops")
            page.keyboard.down("x")
            page.wait_for_timeout(150)
            page.keyboard.up("x")
            page.wait_for_timeout(300)
            check(dbg(7) == 0, "a tap on DLY: no row action, the siren stays quiet")
            check(dbg(11) == sync0, "DLY's mode untouched (OCT+ has no other life here)")
            page.keyboard.down("x")
            page.wait_for_timeout(400)
            check(dbg(7) == 1, "OCT+ pressed again on DLY: the siren re-arms")
            page.keyboard.up("x")
            page.wait_for_timeout(250)
            check(dbg(7) == 0, "released again: the siren off")

            # OCT- closes the menu
            page.keyboard.press("z")
            page.wait_for_timeout(300)
            check(dbg(17) == 0, "OCT- closes the menu")
            page.screenshot(path=str(OUT / "face_home.png"))
            browser.close()
    finally:
        server.shutdown()
    if fails:
        raise SystemExit(f"{len(fails)} check(s) failed")
    print("dub emulator scenario completed")


if __name__ == "__main__":
    main()
