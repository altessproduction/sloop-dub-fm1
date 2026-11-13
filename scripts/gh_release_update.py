#!/usr/bin/env python3
# Updates an existing GitHub release: PATCH the body from a notes file and swap the
# .fwsc asset (delete + re-upload) for the corrected package.
#   GHTOKEN=... python3 scripts/gh_release_update.py TAG NOTES.md ASSET
import hashlib
import json
import os
import sys
import urllib.request

API = "https://api.github.com/repos/altessproduction/sloop-dub-fm1"
UP = "https://uploads.github.com/repos/altessproduction/sloop-dub-fm1/releases"


def call(url, data=None, token=None, ctype="application/json", method=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "sloop-release-script")
    if token:
        req.add_header("Authorization", f"token {token}")
    if ctype:
        req.add_header("Content-Type", ctype)
    with urllib.request.urlopen(req) as r:
        body = r.read().decode()
    return json.loads(body) if body else {}


def main():
    tag, notes, asset = sys.argv[1], sys.argv[2], sys.argv[3]
    token = os.environ["GHTOKEN"]
    rel = call(f"{API}/releases/tags/{tag}", token=token)
    rid = rel["id"]
    print("release:", rid, rel["html_url"])

    body = open(notes, encoding="utf-8").read()
    call(f"{API}/releases/{rid}", json.dumps({"body": body}).encode(), token, method="PATCH")
    print("body patched,", len(body), "chars")

    for a in rel["assets"]:
        if a["name"] == asset.split("/")[-1]:
            call(f"{API}/releases/assets/{a['id']}", token=token, method="DELETE")
            print("asset deleted:", a["name"], a["size"])
    raw = open(asset, "rb").read()
    up = call(f"{UP}/{rid}/assets?name={asset.split('/')[-1]}",
              raw, token, "application/octet-stream")
    print("asset:", up["name"], up["size"], "bytes, state", up["state"])
    print("sha256:", hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    main()
