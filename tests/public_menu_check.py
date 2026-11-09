#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path('/workspace/sloop-dub-fm1/build/dub-emulator-test')
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://altessproduction.github.io/sloop-dub-fm1/dub/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    errors = []
    page.on('console', lambda msg: errors.append('console: ' + msg.text) if msg.type == 'error' else None)
    page.on('pageerror', lambda exc: errors.append('page: ' + str(exc)))
    page.goto(URL, wait_until='networkidle', timeout=60000)
    page.click('#power')
    page.wait_for_timeout(2600)
    page.keyboard.down('7')
    page.wait_for_timeout(1200)
    page.keyboard.up('7')
    page.wait_for_timeout(700)
    screen = page.locator('#screen').inner_text()
    page.screenshot(path=str(OUT / 'public_menu_home.png'))
    for _ in range(5):
        page.keyboard.press('ArrowUp')
        page.wait_for_timeout(220)
    dub_screen = page.locator('#screen').inner_text()
    page.screenshot(path=str(OUT / 'public_menu_dub.png'))
    for _ in range(1):
        page.keyboard.press('ArrowUp')
        page.wait_for_timeout(220)
    dseq_screen = page.locator('#screen').inner_text()
    page.screenshot(path=str(OUT / 'public_menu_dseq.png'))
    print('home_has_menu=', 'MENU' in screen)
    print('dub_has_dub=', 'DUB' in dub_screen and 'DUB ENABLE' in dub_screen)
    print('dseq_has_dseq=', 'DSEQ' in dseq_screen and 'SEQ LENGTH' in dseq_screen)
    print('errors=', errors)
    browser.close()
