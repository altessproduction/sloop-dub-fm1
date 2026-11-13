#!/usr/bin/env python3
# Swaps the version digit on assets/hub-card.png: clears the old glyph (gray 232)
# and draws the new one from assets/fonts/ter-u16b.bdf at x3 NEAREST.
import sys
from PIL import Image

CARD = "assets/hub-card.png"
BDF = "assets/fonts/ter-u16b.bdf"
REGION = (380, 840, 470, 960)          # where the version digit lives
DIGIT = sys.argv[1] if len(sys.argv) > 1 else "5"
GRAY = 232


def bdf_glyph(ch):
    """one glyph as a list of row bitmasks, plus its advance and offset"""
    with open(BDF) as f:
        lines = f.read().splitlines()
    rows, bb = [], None
    in_glyph, in_bitmap = False, False
    for ln in lines:
        if ln.startswith("STARTCHAR") and in_glyph:
            break
        if ln.startswith(f"ENCODING {ord(ch)}"):
            in_glyph = True
        elif in_glyph and ln.startswith("BBX"):
            _, w, h, ox, oy = ln.split()
            bb = (int(w), int(h), int(ox), int(oy))
        elif in_glyph and ln.startswith("BITMAP"):
            in_bitmap = True
        elif in_glyph and in_bitmap and ln.strip() and all(c in "0123456789abcdefABCDEF" for c in ln.strip()):
            rows.append(int(ln.strip(), 16))
        elif in_glyph and ln.startswith("ENDCHAR"):
            break
    return rows, bb


im = Image.open(CARD).convert("RGB")
# 1. the old digit's bounding box (the gray-232 pixels in the region)
px = im.load()
xs, ys = [], []
for y in range(REGION[1], REGION[3]):
    for x in range(REGION[0], REGION[2]):
        if px[x, y] == (GRAY, GRAY, GRAY):
            xs.append(x)
            ys.append(y)
assert xs, "no old digit found"
old = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
print("old digit bbox:", old)
for y in range(old[1] - 1, old[3] + 1):
    for x in range(old[0] - 1, old[2] + 1):
        px[x, y] = (0, 0, 0)

# 2. the new glyph, x3, NEAREST
rows, (gw, gh, gox, goy) = bdf_glyph(DIGIT)
# Terminus 16: the glyph's bitmap rows fill the 16-row cell directly (16 rows, the
# BBX oy of -4 sits the baseline at the cell's bottom)
full = list(rows)
# paste pixels from the 16-row mask
bits = ((gw + 7) // 8) * 8          # the row's byte-padded width: the leftmost pixel is its top bit
cols = bits
src = Image.new("1", (cols, 16), 0)
sp = src.load()
for ry, mask in enumerate(full):
    for cx in range(gw):
        if mask & (1 << (bits - 1 - cx)):
            sp[gox + cx, ry] = 1
big = src.resize((cols * 3, 48), Image.NEAREST)
bw, bh = big.load(), big.size
new_im = Image.new("RGB", big.size, (0, 0, 0))
np_ = new_im.load()
for y in range(big.size[1]):
    for x in range(big.size[0]):
        if bw[x, y]:
            np_[x, y] = (GRAY, GRAY, GRAY)
bbox = new_im.getbbox()
assert bbox, f"the glyph {DIGIT} drew nothing: the bit order is wrong"
glyph = new_im.crop(bbox)
# centre it on the old digit's box
cx = (old[0] + old[2]) // 2
ty = old[1] + (old[3] - old[1] - glyph.size[1]) // 2
im.paste(glyph, (cx - glyph.size[0] // 2, ty))
im.save(CARD)
print("new digit:", DIGIT, "pasted at", (cx - glyph.size[0] // 2, ty), "size", glyph.size)
