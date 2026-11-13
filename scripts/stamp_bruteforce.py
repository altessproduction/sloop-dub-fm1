#!/usr/bin/env python3
# Brute-force the sw.js STAMP recipe against the known v1.4 stamp 7c169c5d45.
import hashlib
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "docs" / "webapp"
EXPECTED = "7c169c5d45"
FILES = ["../firmware/sloop-dub-1.4.fwsc", "editor/", "editor/FUKIAI-LICENSE.txt",
         "editor/fukiai.ttf", "editor/preview-worklet.js", "editor/preview.js",
         "editor/sloop-preview.wasm", "icon-192.png", "icon-512.png",
         "icon-maskable-512.png", "installer/", "sloop.webmanifest"]


def content(rel):
    p = WEB / rel
    if rel.endswith("/"):
        p = p / "index.html"
    if p.exists():
        return p.read_bytes()
    gitpath = os.path.normpath((Path("docs/webapp") / rel).as_posix())
    return subprocess.run(["git", "show", f"HEAD:{gitpath}"],
                          cwd=ROOT, capture_output=True, check=True).stdout


def all_dir_files(rel):
    """every file under the folder (sorted), bytes; committed versions for changed ones"""
    d = WEB / rel
    out = []
    for p in sorted(d.rglob("*")):
        if p.is_file():
            out.append((str(p.relative_to(WEB)), p.read_bytes()))
    return out


def item(rel):
    """candidate item streams for one FILES entry"""
    c = content(rel)
    yield "plain", c
    if rel.endswith("/"):
        for path, data in all_dir_files(rel):
            yield f"all:{path}", data
            yield f"allpath:{path}", path.encode() + data


def run(name, items, algo="sha256", version=None):
    h = hashlib.new(algo)
    if version:
        h.update(version.encode())
    for label, data in items:
        h.update(data)
    dig = h.hexdigest()
    if dig[:10] == EXPECTED:
        print(f"MATCH {name}")


# iterate over combinations
for version in (None, "1.4"):
    for algo in ("sha256", "sha1", "blake2b"):
        for mode in ("plain", "allfiles", "allpath"):
            items = []
            for f in FILES:
                if mode == "plain":
                    items.append((f, content(f)))
                elif f.endswith("/"):
                    if mode == "allfiles":
                        items += all_dir_files(f)
                    else:
                        items += [(p, f.encode() + d) for p, d in all_dir_files(f)]
                else:
                    items.append((f, f.encode() + content(f) if mode == "allpath" else content(f)))
            run(f"{version}/{algo}/{mode}", items, algo, version)
            # per-file digest chains
            for chained in (True, False):
                pass
# per-file sha256 concatenated (raw and hex), with/without path prefix
for withpath in (False, True):
    for raw in (False, True):
        acc = b""
        for f in FILES:
            c = content(f)
            h = hashlib.sha256((f.encode() + c) if withpath else c).digest()
            acc += h if raw else h.hex().encode()
        for prefix in (b"", b"1.4"):
            if hashlib.sha256(prefix + acc).hexdigest()[:10] == EXPECTED:
                print(f"MATCH chain withpath={withpath} raw={raw} prefix={prefix!r}")
print("done")
