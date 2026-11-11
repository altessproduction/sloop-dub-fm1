#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Syncs the web editors' drum-kit mock with the generated felucca_drumkits.h:
DSYN_MOCK_NAMES and DSYN_MOCK_KITS (per kit its crush, then 16 x 22 bytes, base64),
in both the served page (index.html) and the offline one (sloop-editor.html).
Run after tools/gen_drumkits.py.
  python3 scripts/update_editor_kits.py
"""
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTMLS = [ROOT / "docs/webapp/editor/sloop-editor.html",
         ROOT / "docs/webapp/editor/index.html"]
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

    # the KIT enum mirrors drums.c DRUM_KIT_NAMES: 5 sampled kits, the DS list from the
    # generated header, then the user slots and the four SYNTH slots
    ds = re.search(r'#define DS_KIT_NAME_LIST (.+)', t).group(1).strip()
    ds_names = [x.strip() for x in ds.split('"') if x.strip() and x.strip() != ","]
    kit_names = ["ONE DROP", "STEPPERS", "SKA", "ROCKERS", "DUB"] + ds_names + \
                ["USR1", "USR2", "USR3", "USR4", "USR3+4", "SYN1", "SYN2", "SYN3", "SYN4"]
    kit_js = ", ".join(f'"{n}"' for n in kit_names)
    assert len(kit_names) == 5 + len(ds_names) + 9, len(kit_names)

    for HTML in HTMLS:
        html = HTML.read_text()
        html, n1 = re.subn(r'const DSYN_MOCK_NAMES = \[[^\]]*\];',
                           f'const DSYN_MOCK_NAMES = [{names_js}];', html)
        html, n2 = re.subn(r'const DSYN_MOCK_KITS = "[^"]*";',
                           f'const DSYN_MOCK_KITS = "{b64}";', html)
        html, n3 = re.subn(r'const KIT = E\("KIT", \[[^\]]*\]',
                           f'const KIT = E("KIT", [{kit_js}]', html)
        assert n1 == 1 and n2 == 1 and n3 == 1, (HTML.name, n1, n2, n3)
        HTML.write_text(html)
        print(f"{len(kits)} kits, KIT enum {len(kit_names)} -> {HTML.name} ({len(blob)} bytes, {len(b64)} b64)")


if __name__ == "__main__":
    main()
