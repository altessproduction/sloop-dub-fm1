#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Syncs the web editor's drum-kit mock (docs/webapp/editor/sloop-editor.html) with the
generated felucca_drumkits.h: DSYN_MOCK_NAMES and DSYN_MOCK_KITS (per kit its crush, then
16 x 22 bytes, base64). Run after tools/gen_drumkits.py.
  python3 scripts/update_editor_kits.py
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "docs/webapp/editor/sloop-editor.html"
HDR = ROOT / "build/gen/felucca_drumkits.h"


def main():
    t = HDR.read_text()
    # every kit: {"NAME", "STYLE", 0xCRUSH, { {22 bytes}, ... x16 } }
    kits = []
    for m in re.finditer(r'\{"([^"]+)", "([^"]+)", (0x[0-9A-F]{2}), \{\n((?:        \{[^}]*\},?\s*(?:/\*[^*]*\*/)?\s*\n)+)    \}\}', t):
        name, style, crush_s, body = m.group(1), m.group(2), m.group(3), m.group(4)
        sounds = []
        for sm in re.finditer(r'\{([^}]*)\}', body):
            sounds += [int(x.strip()) for x in sm.group(1).split(",") if x.strip()]
        assert len(sounds) == 16 * 22, (name, len(sounds))
        kits.append((name, int(crush_s, 16), sounds))
    assert len(kits) == 32, len(kits)
    blob = bytearray()
    for name, crush, sounds in kits:
        blob.append(crush)
        blob += bytes(sounds)
    b64 = base64.b64encode(bytes(blob)).decode()
    names_js = ", ".join(f'"{n}"' for n, _, _ in kits)

    html = HTML.read_text()
    html, n1 = re.subn(r'const DSYN_MOCK_NAMES = \[[^\]]*\];',
                       f'const DSYN_MOCK_NAMES = [{names_js}];', html)
    html, n2 = re.subn(r'const DSYN_MOCK_KITS = "[^"]*";',
                       f'const DSYN_MOCK_KITS = "{b64}";', html)
    assert n1 == 1 and n2 == 1, (n1, n2)
    HTML.write_text(html)
    print(f"{len(kits)} kits -> editor mock ({len(blob)} bytes, {len(b64)} b64)")


if __name__ == "__main__":
    main()
