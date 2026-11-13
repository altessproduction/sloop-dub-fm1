#!/usr/bin/env python3
# Compute the sw.js STAMP exactly like the SLOOP fork's web/make_site.py:
# sha256 over sorted(keep) entries, each (relative_path + b"\0" + file_bytes),
# a folder entry resolving to its index.html. STAMP = version + "-" + digest[:12].
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "docs" / "webapp"
FW_NAME = sys.argv[1] if len(sys.argv) > 1 else "sloop-dub-1.5.fwsc"
VERSION = sys.argv[2] if len(sys.argv) > 2 else "1.5"
EXPECTED_V14 = "7c169c5d45"


def read(rel, fw_name):
    """the file's bytes; a folder entry resolves to its index.html; the firmware and
    the editor wasm come from the working tree when they exist, else from git HEAD"""
    p = (WEB / rel).resolve() if not rel.endswith("/") else WEB / rel / "index.html"
    p = Path(os.path.normpath(p))
    if p.exists():
        return p.read_bytes()
    gitpath = os.path.relpath(p, ROOT).replace(os.sep, "/")
    return subprocess.run(["git", "show", f"HEAD:{gitpath}"],
                          cwd=ROOT, capture_output=True, check=True).stdout


def keep_paths(fw_name):
    return ["../firmware/" + fw_name, "editor/", "editor/FUKIAI-LICENSE.txt",
            "editor/fukiai.ttf", "editor/preview-worklet.js", "editor/preview.js",
            "editor/sloop-preview.wasm", "icon-192.png", "icon-512.png",
            "icon-maskable-512.png", "installer/", "sloop.webmanifest"]


def stamp(paths, version):
    h = hashlib.sha256()
    for k in sorted(paths):
        h.update(k.encode() + b"\0" + read(k, os.path.basename(k)))
    return f"{version}-{h.hexdigest()[:12]}"


# sanity: the recipe reproduces the committed v1.4 stamp (first 10 hex)
v14 = stamp(keep_paths("sloop-dub-1.4.fwsc"), "1.4")
print("v1.4 recheck:", v14, "<== expected 1.4-7c169c5d45"[:40], "MATCH" if v14[:10] == EXPECTED_V14 else "MISMATCH")
print("STAMP for sw.js:", stamp(keep_paths(FW_NAME), VERSION))
