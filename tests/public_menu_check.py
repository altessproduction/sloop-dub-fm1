#!/usr/bin/env python3
# Public-site check: the deployed emulator's HOME menu walks the twelve pages and
# the six Dub pages show their rows. Run after deploying docs/ to GitHub Pages
# with the rebuilt sloop.wasm (reference_emu/build.sh).
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[1] / 'build' / 'dub-emulator-test'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://altessproduction.github.io/sloop-dub-fm1/dub/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required", "--no-proxy-server"])
    page = browser.new_page(viewport={'width': 1280, 'height': 800})
    errors = []
    page.on('console', lambda msg: errors.append('console: ' + msg.text) if msg.type == 'error' else None)
    page.on('pageerror', lambda exc: errors.append('page: ' + str(exc)))
    page.goto(URL, wait_until='networkidle', timeout=60000)
    page.click('#power')
    page.wait_for_timeout(2600)
    # HOME held opens the menu; SELECT is ArrowUp (next page) / ArrowDown.
    page.keyboard.down('7')
    page.wait_for_timeout(1200)
    page.keyboard.up('7')
    page.wait_for_timeout(700)
    page.screenshot(path=str(OUT / 'public_menu_home.png'))
    # The Dub pages follow SYSTEM by SELECT: DUB SIR SR2 SKK DLY SND RDM PRS ISO.
    # The LCD is a canvas (no text nodes), so each page is judged by its lit-pixel
    # share and kept as a screenshot for the eye.
    lit = """() => {
      const c = document.getElementById('screen');
      const d = c.getContext('2d').getImageData(0, 0, 240, 240).data;
      let n = 0;
      for (let k = 0; k < d.length; k += 4) if (d[k] + d[k+1] + d[k+2] > 60) n++;
      return n / (240 * 240);
    }"""
    for name, steps in [('dub', 5), ('siren', 1), ('siren2', 1), ('skank', 1), ('dly', 1), ('snd', 1), ('riddim', 1), ('preset', 1), ('iso', 1)]:
        for _ in range(steps):
            page.keyboard.press('ArrowUp')
            page.wait_for_timeout(220)
        page.screenshot(path=str(OUT / ('public_menu_' + name + '.png')))
        print(name + '_lit=', round(page.evaluate(lit), 3))
    print('errors=', errors)
    browser.close()
