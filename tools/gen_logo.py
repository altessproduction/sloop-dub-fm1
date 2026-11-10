#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""The SLOOP Dub logo: the sound-system tower — the scoops' grid at the bottom, four
coloured cones on the third row, the horns and the bullet tweeters on top — over the
rounded "sloop-DUB" wordmark. The drawing is the master art, everything else derives
from it (the sail of the base SLOOP is gone).

  tools/gen_logo.py OUT.h          firmware boot splash (RLE, 16-colour palette, RGB565)
  tools/gen_logo.py --assets DIR   sloop-logo.png, sloop-icon.png, sloop-splash.png in DIR,
                                   plus the web icons (docs/webapp, docs/dub, reference_emu)
"""
import colorsys
import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "assets/logo/sloop-dub-tower.png"
SPLASH_W, SPLASH_H = 240, 188
WHITE, BLACK = (242, 242, 242), (0, 0, 0)
FALLBACK = {"blue": (40, 124, 255), "green": (30, 204, 112),
            "yellow": (255, 198, 24), "red": (230, 36, 40)}


def master():
    return Image.open(MASTER).convert("RGB")


# ---- reading the master art -------------------------------------------------------------------
def ink_rows(im, thr=40):
    """the rows that carry ink (step 2: the halftone dots count too)"""
    g = im.convert("L")
    p, W = g.load(), g.size[0]
    return [y for y in range(g.size[1]) if any(p[x, y] > thr for x in range(0, W, 2))]


def runs_of(seq):
    """consecutive runs [(a, b), ...], gaps narrower than 12 rows merged"""
    out = []
    for v in seq:
        if out and v <= out[-1][1] + 12:
            out[-1][1] = v
        else:
            out.append([v, v])
    return out


def bbox_cols(im, y0, y1, thr=40):
    g = im.convert("L")
    p = g.load()
    xs = [x for x in range(g.size[0]) if any(p[x, y] > thr for y in range(y0, y1 + 1, 2))]
    return min(xs), max(xs)


def tower_box(im):
    """the tower: the tallest ink run, before the wordmark's gap"""
    rr = runs_of(ink_rows(im))
    t = max(rr, key=lambda r: r[1] - r[0])
    x0, x1 = bbox_cols(im, t[0], t[1])
    return (x0, t[0], x1, t[1])


def content_box(im):
    """the whole drawing (tower, wordmark, caption)"""
    rr = runs_of(ink_rows(im))
    y0, y1 = rr[0][0], rr[-1][1]
    x0, x1 = bbox_cols(im, y0, y1)
    return (x0, y0, x1, y1)


def square(im, box, margin=0.03):
    """the crop, padded to a square with black"""
    c = im.crop(box)
    side = int(max(c.size) * (1 + 2 * margin))
    out = Image.new("RGB", (side, side), BLACK)
    out.paste(c, ((side - c.size[0]) // 2, (side - c.size[1]) // 2))
    return out


def cropped(im, box, margin=0.03):
    """the crop with a margin, kept as it is"""
    x0, y0, x1, y1 = box
    mx, my = int((x1 - x0) * margin), int((y1 - y0) * margin)
    return im.crop((max(0, x0 - mx), max(0, y0 - my),
                    min(im.size[0], x1 + mx), min(im.size[1], y1 + my)))


def save_p(im, path, colors=256):
    path = Path(path).resolve()
    im.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=colors).save(path, optimize=True)
    print(f"logo: {path.relative_to(ROOT)} {im.size[0]}x{im.size[1]}")


# ---- the palette of the splash ----------------------------------------------------------------
def art_hues(im):
    """the four cone colours, sampled out of the art (hue bands, saturated pixels only)"""
    hsv = im.resize((192, 192)).convert("HSV")
    p = hsv.load()
    buckets = {b: [] for b in ("red", "yellow", "green", "blue")}
    for y in range(192):
        for x in range(192):
            h, s, v = p[x, y]
            if s > 90 and v > 115:
                deg = h * 360 / 256
                b = ("red" if deg >= 330 or deg < 30 else "yellow" if deg < 82
                     else "green" if deg < 190 else "blue" if deg < 290 else "red")
                buckets[b].append((h, s, v))
    out = {}
    for b, v in buckets.items():
        if not v:
            out[b] = FALLBACK[b]
            continue
        n = len(v)
        r, g, c = colorsys.hsv_to_rgb(sum(q[0] for q in v) / n / 255,
                                      sum(q[1] for q in v) / n / 255,
                                      sum(q[2] for q in v) / n / 255)
        out[b] = (round(r * 255), round(g * 255), round(c * 255))
    return out


def splash_palette(im):
    """black, the white's three shades, then each cone colour at 1/3, 2/3 and full"""
    cols = [BLACK]
    for c in (WHITE,) + tuple(art_hues(im)[b] for b in ("blue", "green", "yellow", "red")):
        cols += [tuple(round(v * f) for v in c) for f in (1 / 3, 2 / 3, 1.0)]
    return cols


def rgb565(c):
    r, g, b = c
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


# ---- the boot splash --------------------------------------------------------------------------
def splash_render():
    """the drawing fitted in the 240 x 188 canvas (the version stays at the bottom)"""
    im = master()
    box = content_box(im)
    art = cropped(im, box, margin=0.015)
    k = min((SPLASH_W - 8) / art.size[0], (SPLASH_H - 8) / art.size[1])
    art = art.resize((round(art.size[0] * k), round(art.size[1] * k)), Image.LANCZOS)
    cv = Image.new("RGB", (SPLASH_W, SPLASH_H), BLACK)
    cv.paste(art, ((SPLASH_W - art.size[0]) // 2, (SPLASH_H - art.size[1]) // 2))
    return cv.filter(ImageFilter.GaussianBlur(0.7))   # the halftone's dots merge at this scale


def splash_header(path):
    cv, cols = splash_render(), splash_palette(master())
    src, cache, px = cv.tobytes(), {}, []
    for i in range(0, len(src), 3):
        p = (src[i], src[i + 1], src[i + 2])
        if p not in cache:
            cache[p] = min(range(len(cols)), key=lambda k: sum((p[j] - cols[k][j]) ** 2 for j in range(3)))
        px.append(cache[p])
    rle = bytearray()                                 # (run - 1) << 4 | index, runs of 1..16
    i = 0
    while i < len(px):
        j = i
        while j < len(px) and px[j] == px[i] and j - i < 16:
            j += 1
        rle.append(((j - i - 1) << 4) | px[i])
        i = j
    L = ["/* generated by tools/gen_logo.py from assets/logo/sloop-dub-tower.png: the sound-system boot splash */",
         "#pragma once", "#include <stdint.h>",
         f"#define SLOOP_SPLASH_W {SPLASH_W}", f"#define SLOOP_SPLASH_H {SPLASH_H}",
         "static const uint16_t SLOOP_SPLASH_PAL[16] = {" + ", ".join(f"0x{rgb565(c):04X}" for c in cols) + "};",
         f"static const uint8_t SLOOP_SPLASH_RLE[{len(rle)}] = {{"]
    for k in range(0, len(rle), 24):
        L.append("    " + ", ".join(str(b) for b in rle[k:k + 24]) + ",")
    L.append("};")
    Path(path).write_text("\n".join(L) + "\n")
    print(f"logo: splash {SPLASH_W}x{SPLASH_H}, {len(rle)} B RLE -> {path}")


# ---- the assets -------------------------------------------------------------------------------
def web_icons(tower):
    """the PWA's icons: the tower only (the wordmark would drown at 192 px)"""
    web, dub = ROOT / "docs/webapp", ROOT / "docs/dub"
    for size, path in ((192, web / "icon-192.png"), (512, web / "icon-512.png"),
                       (192, dub / "icon-192.png"), (512, dub / "icon-512.png"),
                       (180, dub / "apple-touch-icon.png"), (180, ROOT / "reference_emu/apple-touch-icon.png")):
        save_p(tower.resize((size, size), Image.LANCZOS), path)
    m = Image.new("RGB", (512, 512), BLACK)           # maskable: the tower inside the safe zone
    m.paste(tower.resize((368, 368), Image.LANCZOS), ((512 - 368) // 2,) * 2)
    save_p(m, web / "icon-maskable-512.png")


def assets(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    im = master()
    tower = square(im, tower_box(im))
    banner = cropped(im, content_box(im), margin=0.03)
    banner = banner.resize((1080, round(1080 * banner.size[1] / banner.size[0])), Image.LANCZOS)
    save_p(banner, out / "sloop-logo.png")
    save_p(tower.resize((512, 512), Image.LANCZOS), out / "sloop-icon.png")
    web_icons(tower)
    splash_render().resize((SPLASH_W * 2, SPLASH_H * 2), Image.NEAREST).save(out / "sloop-splash.png")
    print(f"logo: splash preview -> {out / 'sloop-splash.png'}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--assets":
        assets(sys.argv[2])
    elif len(sys.argv) == 2:
        splash_header(sys.argv[1])
    else:
        sys.exit(__doc__)
