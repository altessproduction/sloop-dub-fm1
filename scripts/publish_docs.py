#!/usr/bin/env python3
"""Publishes release X.Y: copies the built package and the editor preview into docs/,
rewrites the installer's meta, the service worker's STAMP and the site's download link.
Run after `tools/build.py --release X.Y` and the wasm/preview builds:
  python3 scripts/publish_docs.py 1.4
"""
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REL = sys.argv[1] if len(sys.argv) > 1 else "1.4"

fw = ROOT / "build" / f"sloop-dub-{REL}.fwsc"
if not fw.exists():
    sys.exit(f"{fw}: build it first (tools/build.py --release {REL})")

sha = hashlib.sha256(fw.read_bytes()).hexdigest()

# 1. the package into docs/firmware/, the old one out
fw_dir = ROOT / "docs" / "firmware"
for old in fw_dir.glob("sloop-dub-*.fwsc"):
    if old.name != fw.name:
        old.unlink()
        print("removed", old.relative_to(ROOT))
shutil.copy(fw, fw_dir / fw.name)
print("copied", fw.name, f"{fw.stat().st_size} B")

# 2. the editor's preview wasm (the freshly compiled one)
pv = ROOT / "build" / "preview" / "sloop-preview.wasm"
if pv.exists():
    shutil.copy(pv, ROOT / "docs" / "webapp" / "editor" / "sloop-preview.wasm")
    print("copied sloop-preview.wasm", pv.stat().st_size, "B")

# 3. the offline editor snapshot under its version name
ed = ROOT / "docs" / "webapp" / "editor" / "sloop-editor.html"
if ed.exists():
    for old in (ROOT / "docs" / "webapp" / "editor").glob("sloop-editor-*.html"):
        old.unlink()
    snap = ed.with_name(f"sloop-editor-{REL}.html")
    shutil.copy(ed, snap)
    print("copied", snap.name)

# 4. the installer's meta line
inst = ROOT / "docs" / "webapp" / "installer" / "index.html"
txt = inst.read_text()
meta_line = re.search(r'^const meta = \{.*\};$', txt, re.M)
if meta_line:
    meta = {"version": REL, "product": "FM-1_234",
            "pkg": f"../../firmware/sloop-dub-{REL}.fwsc", "sha256": sha}
    txt = txt.replace(meta_line.group(0), "const meta = " + json.dumps(meta) + ";")
    inst.write_text(txt)
    print("installer meta ->", meta["version"], sha[:16], "…")

# 5. the service worker: the file list follows the release, the STAMP follows the bytes
sw = ROOT / "docs" / "webapp" / "sw.js"
txt = sw.read_text()
txt = re.sub(r'"../firmware/sloop-dub-[\d.]+\.fwsc"',
             f'"../firmware/sloop-dub-{REL}.fwsc"', txt)
sw.write_text(txt)
m = re.search(r'const FILES = \[(.*?)\];', txt, re.S)
files = re.findall(r'"([^"]+)"', m.group(1))
h = hashlib.sha256()
for f in files:
    p = ROOT / "docs" / "webapp" / f
    if p.is_file():
        h.update(p.read_bytes())
stamp = f"{REL}-{h.hexdigest()[:12]}"
txt = txt.replace(re.search(r'const STAMP = "[^"]*"', txt).group(0),
                  f'const STAMP = "{stamp}"')
sw.write_text(txt)
print("sw STAMP ->", stamp)

# 6. the site page's download link
idx = ROOT / "docs" / "index.html"
txt = idx.read_text()
txt = re.sub(r'firmware/sloop-dub-[\d.]+\.fwsc', f'firmware/sloop-dub-{REL}.fwsc', txt)
txt = re.sub(r'sloop-dub-[\d.]+\.fwsc', f'sloop-dub-{REL}.fwsc', txt)
idx.write_text(txt)
print("docs/index.html ->", REL)
