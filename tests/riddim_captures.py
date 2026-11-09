#!/usr/bin/env python3
"""Deliverable captures (2.9.4): the DSQ four-track view with a loaded riddim and its
playhead, the LCD's RDM page and the DSQ page showing LEN 64 — from the live site."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import base64
import time
import sys

OUT = Path("/home/z/my-project/download")
URL = "https://altessproduction.github.io/sloop-dub-fm1/dub/"


def lcd_b64(page):
    return page.evaluate("() => document.getElementById('screen').toDataURL('image/png')")


def press(page, btn, hold=140):
    page.evaluate(f"btnDown({btn})")
    page.wait_for_timeout(hold)
    page.evaluate(f"btnUp({btn})")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    page = browser.new_context(viewport={"width": 1400, "height": 1050}).new_page()
    page.goto(URL, wait_until="networkidle")
    page.locator("#power").click()
    time.sleep(2.8)

    # load ONE DROP from the RDM tab, then show the DSQ four-track view, PLAY running
    page.locator('.dub-tab[data-dub-page="rdm"]').click()
    time.sleep(0.2)
    page.locator("#dub-riddim-load").click()
    time.sleep(0.4)
    page.screenshot(path=str(OUT / "riddim-load-RDM-tab-live.png"), full_page=False)

    page.locator('.dub-tab[data-dub-page="dseq"]').click()
    time.sleep(0.4)
    press(page, 12)                       # PLAY (menu closed: the web flow)
    time.sleep(0.9)
    page.screenshot(path=str(OUT / "sequencer-DSQ-view-playing-live.png"), full_page=False)
    press(page, 12)

    # the firmware LCD: long HOME, RDM page, K1 turn, OCT+ -> "RIDDIM LOADED"
    press(page, 8, 1200)
    time.sleep(0.5)
    for _ in range(10):
        page.evaluate("enc(0, 1)")
        page.wait_for_timeout(90)
    time.sleep(0.4)
    (OUT / "riddim-page-RDM-live.png").write_bytes(base64.b64decode(lcd_b64(page).split(",", 1)[1]))
    page.evaluate("enc(3, 1)")
    time.sleep(0.2)
    press(page, 1)                        # OCT+ load
    time.sleep(0.35)
    (OUT / "riddim-loaded-message-live.png").write_bytes(base64.b64decode(lcd_b64(page).split(",", 1)[1]))
    page.evaluate("enc(0, -1)")           # the DSQ page: LEN 64
    time.sleep(0.35)
    (OUT / "riddim-page-DSEQ-LEN64-live.png").write_bytes(base64.b64decode(lcd_b64(page).split(",", 1)[1]))

    browser.close()
print("captures saved")
