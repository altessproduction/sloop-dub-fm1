#!/usr/bin/env python3
# Re-derive the sw.js STAMP recipe (validated against the v1.4 stamp 7c169c5d45),
# then print the v1.5 stamp. The FILES list is relative to docs/webapp; folders
# resolve to their index.html.
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "docs" / "webapp"

FILES = ["../firmware/sloop-dub-1.4.fwsc", "editor/", "editor/FUKIAI-LICENSE.txt",
         "editor/fukiai.ttf", "editor/preview-worklet.js", "editor/preview.js",
         "editor/sloop-preview.wasm", "icon-192.png", "icon-512.png",
         "icon-maskable-512.png", "installer/", "sloop.webmanifest"]

EXPECTED = "7c169c5d45"


def content(rel):
    """the file's bytes; a folder path resolves to its index.html"""
    p = WEB / rel
    if rel.endswith("/"):
        p = p / "index.html"
    if p.exists():
        return p.read_bytes()
    # the build changed it (fwsc, wasm): take the committed v1.4 version
    import os
    gitpath = os.path.normpath((Path("docs/webapp") / rel).as_posix())
    return subprocess.run(["git", "show", f"HEAD:{gitpath}"],
                          cwd=ROOT, capture_output=True, check=True).stdout


def per_file_sha(rel):
    return hashlib.sha256(content(rel)).hexdigest()


recipes = {}
# A: sha256 of the concatenated bytes
recipes["A concat-bytes"] = hashlib.sha256(b"".join(content(f) for f in FILES)).hexdigest()
# B: sha256 of path+bytes for each
h = hashlib.sha256()
for f in FILES:
    h.update(f.encode())
    h.update(content(f))
recipes["B path+bytes"] = h.hexdigest()
# C: concat of per-file hex digests
h = hashlib.sha256("".join(per_file_sha(f) for f in FILES).encode())
recipes["C concat-hex"] = h.hexdigest()
# D: concat of per-file raw digests
h = hashlib.sha256(b"".join(hashlib.sha256(content(f)).digest() for f in FILES))
recipes["D concat-raw"] = h.hexdigest()
# E: paths only
h = hashlib.sha256("".join(FILES).encode())
recipes["E paths"] = h.hexdigest()

for name, dig in recipes.items():
    ok = "  <== MATCH" if dig[:10] == EXPECTED else ""
    print(f"{name}: {dig[:16]}{ok}")
