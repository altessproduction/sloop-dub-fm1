#!/usr/bin/env python3
# Creates a GitHub release on altessproduction/sloop-dub-fm1 and uploads the .fwsc asset.
#   GHTOKEN=... python3 scripts/gh_release.py TAG NAME NOTES.md ASSET
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
        return json.loads(r.read().decode())


def main():
    tag, name, notes, asset = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    token = os.environ["GHTOKEN"]
    body = open(notes, encoding="utf-8").read()
    rel = call(f"{API}/releases", json.dumps({
        "tag_name": tag, "target_commitish": "main", "name": name,
        "body": body, "draft": False, "prerelease": False,
    }).encode(), token)
    print("release:", rel["id"], rel["html_url"])
    raw = open(asset, "rb").read()
    up = call(f"{UP}/{rel['id']}/assets?name={asset.split('/')[-1]}",
              raw, token, "application/octet-stream")
    print("asset:", up["name"], up["size"], "bytes, state", up["state"])


if __name__ == "__main__":
    main()
