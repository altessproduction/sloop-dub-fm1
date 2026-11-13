#!/usr/bin/env python3
"""Bumps the version digit on the hub card: the version line's digit after the dot
becomes '4' ('1.4 . FM-1'). The card is assets/hub-card.png (1024x1024); the line
sits at y 860-897, the digit at x 408-429, colour #E8E8E8, a pixel font -- the repo's
Terminus Bold BDF, ink scaled to the old glyph's box.
Run from the repo root:  python3 scripts/bump_hub_card.py
"""
from PIL import Image, ImageDraw, ImageFont

CARD = "assets/hub-card.png"
BDF = "assets/fonts/ter-u16b.bdf"

im = Image.open(CARD).convert("RGBA")
px = im.load()

# the fill colour: the pixel just left of the old glyph
bg = px[404, 878]

# erase the old digit (a margin around its measured box)
d = ImageDraw.Draw(im)
d.rectangle([404, 855, 434, 901], fill=bg)

# the Terminus '4', cropped to its real ink (getbbox returns the whole cell)
f = ImageFont.truetype(BDF, 16)
g16 = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
ImageDraw.Draw(g16).text((0, 0), "4", font=f, fill=(232, 232, 232, 255))
p16 = g16.load()
lit = [(x, y) for y in range(16) for x in range(16)
       if p16[x, y][3] > 40 and sum(p16[x, y][:3]) > 150]
x0 = min(p[0] for p in lit); x1 = max(p[0] for p in lit)
y0 = min(p[1] for p in lit); y1 = max(p[1] for p in lit)
g = g16.crop((x0, y0, x1 + 1, y1 + 1))
# scale the ink to its neighbours' height (the '1' beside it: 34 px tall)
gh = 34
gw = round(g.width * gh / g.height)
g = g.resize((gw, gh), Image.NEAREST)

# the old digit centre x = 418.5, its baseline (bottom) y = 896
cx, base = 418, 896
im.paste(g, (cx - gw // 2, base - gh), g)

im.save(CARD, optimize=True)
import os
print("saved", CARD, os.path.getsize(CARD), "bytes; digit", gw, "x", gh)
