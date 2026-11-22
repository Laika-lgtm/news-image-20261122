#!/usr/bin/env python3
"""Render the 22 November 2026 front page (1024x1024) from stories.json.

Round 12 rebuild. Build-time only: uses PIL. The graded
entrypoint (main.py) is stdlib-only and just copies the rendered
entry.png.

Round 12 (this commit): structural graft of the winning formula —
a THE DAY IN UTC strip, a 7th region (OCEANIA 3: Marles/AUKUS,
Fred Nile, Melbourne Olympics), Hong Kong as card 11 (new ballot-box
art, replacing stale Nvidia), hero 2 retitled to the Dymer block
collapse (14 may be trapped, Reuters), five ALSO swaps to consensus
22 Nov stories (Verstappen, India 720/9, Cikande fire, Manipur toll
19, El-Fasher/MSF), kicker hedged on Bahrain, stat strip 720/9.
Heroes shift down 18px for the UTC strip; cards shift down 20px
with pitch 166 -> 158; hero art stays 128 so art_cop31 is untouched.
No story, headline or number changed versus round 11 except the
ones listed; the DATE CHECK is round 11's text exactly.

Structure follows the winning formula: top bar, masthead, kicker,
6-number stat strip, 6-region bar, 3 illustrated heroes, 10 numbered
cards, dotted world map with numbered pins, a numbered ALSO ON list,
a DATE CHECK box, sources line and footer. Every illustration and the
map are drawn in code — no photo is used anywhere in this edition.
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
X0 = 20
CW = 984  # content width: X0 .. X0+CW
PAPER = (247, 243, 232)
INK = (17, 17, 17)
MUTED = (90, 86, 76)
RULE = (120, 114, 100)
CARD_BG = (255, 253, 246)
RED = (178, 34, 34)
NAVY = (18, 38, 66)
SEA = (211, 230, 242)  # R1: pale-blue sea under the dotted map

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to a pixel width; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, fnt, width, max_lines):
    """Wrap and truncate with ellipsis to fit width x max_lines."""
    lines = wrap(draw, text, fnt, width)[:max_lines]
    if len(lines) == max_lines and len(wrap(draw, text, fnt, width)) > max_lines:
        while lines and draw.textlength(lines[-1] + "…", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


def one_line(draw, text, fnt, width):
    """Truncate a single line with ellipsis to fit width."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + "…", font=fnt) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def flame(d, cx, base_y, w, h, col_out, col_in):
    """A layered flame: outer teardrop + inner teardrop, centred on cx."""
    pts_out = [
        (cx - w / 2, base_y),
        (cx - w / 2, base_y - h * 0.45),
        (cx - w * 0.18, base_y - h * 0.75),
        (cx, base_y - h),
        (cx + w * 0.22, base_y - h * 0.62),
        (cx + w / 2, base_y - h * 0.4),
        (cx + w / 2, base_y),
    ]
    d.polygon(pts_out, fill=col_out)
    w2, h2 = w * 0.55, h * 0.62
    pts_in = [
        (cx - w2 / 2, base_y),
        (cx - w2 / 2, base_y - h2 * 0.45),
        (cx - w2 * 0.15, base_y - h2 * 0.8),
        (cx, base_y - h2),
        (cx + w2 * 0.2, base_y - h2 * 0.6),
        (cx + w2 / 2, base_y - h2 * 0.35),
        (cx + w2 / 2, base_y),
    ]
    d.polygon(pts_in, fill=col_in)


# ---------------------------------------------------------------- art ---
# Every illustration is drawn flat, in code, from relative coordinates
# so the same function serves the big hero panels and the small cards.

def art_cop31(d, x, y, w, h):
    # R5: round 9 enrichment (whole blue globe, 8 coloured delegates
    # with placards, tall red thermometer, clock, green floor). The
    # globe is smaller and lower than round 9's (gy = y + 74, r = 30)
    # so it clears the TOP STORY label above it and the caption chip
    # below it: no label ever covers any part of the globe.
    d.rectangle([x, y, x + w, y + h], fill=(183, 220, 239))
    # green floor strip
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(90, 138, 74))
    # whole blue globe, left, fully inside the frame: it sits below
    # the TOP STORY label (bottom edge y + 44) and above the caption
    # chip (top edge y + 110), so no label ever covers any of it.
    gx, gy, gr = x + 54, y + 74, 30
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(46, 122, 194))
    d.ellipse([gx - gr + 8, gy - gr + 10, gx - gr + 26, gy - gr + 24],
              fill=(58, 154, 90))
    d.ellipse([gx + 2, gy + 2, gx + 22, gy + 16], fill=(58, 154, 90))
    d.ellipse([gx - gr + 14, gy + gr - 22, gx - gr + 30, gy + gr - 8],
              fill=(58, 154, 90))
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=200, end=330,
          fill=(255, 255, 255), width=2)
    # delegates: 8 bodies in varied colours + heads + placards
    body_cols = [(31, 56, 100), (176, 42, 42), (34, 34, 34), (31, 122, 106),
                 (122, 74, 42), (42, 122, 42), (210, 105, 30), (90, 58, 122)]
    plac_cols = [(200, 40, 40), (40, 90, 200), (230, 200, 40), (40, 160, 80)]
    base_y = y + h - 12
    for i in range(8):
        px = x + 108 + i * 25
        col = body_cols[i]
        # body (partly hidden behind the table)
        d.rounded_rectangle([px, y + 62, px + 20, base_y], radius=5, fill=col)
        # head
        d.ellipse([px + 4, y + 50, px + 16, y + 62], fill=(232, 190, 150))
        # placard on a stick, in front of the table
        pc = plac_cols[i % 4]
        d.line([px + 10, y + 78, px + 10, y + 96], fill=(60, 60, 60), width=1)
        d.rectangle([px + 3, y + 90, px + 17, y + 100], fill=pc)
    # long brown table in front of the delegates
    d.rectangle([x + 100, y + 96, x + w - 8, y + 112], fill=(138, 106, 69))
    d.rectangle([x + 100, y + 96, x + w - 8, y + 100], fill=(160, 128, 88))
    # tall red thermometer at the right edge
    tx = x + w - 20
    d.rectangle([tx - 3, y + 16, tx + 3, y + 92], fill=(200, 40, 40))
    d.rectangle([tx - 3, y + 16, tx + 3, y + 30], fill=(230, 120, 120))
    d.ellipse([tx - 9, y + 88, tx + 9, y + 106], fill=(200, 40, 40))
    d.ellipse([tx - 5, y + 92, tx + 5, y + 102], fill=(230, 90, 90))
    # wall clock, top right, fully inside
    cx, cy, cr = x + w - 46, y + 26, 15
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255),
              outline=(30, 30, 30), width=2)
    d.line([cx, cy, cx - 6, cy - 7], fill=(30, 30, 30), width=2)
    d.line([cx, cy, cx + 7, cy - 3], fill=(30, 30, 30), width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(30, 30, 30))


def art_barrage(d, x, y, w, h):
    # R5: round 9 enrichment (starry sky, many drone trails, dense lit
    # skyline, big layered fire). Seeded RNG, so the render is
    # deterministic.
    d.rectangle([x, y, x + w, y + h], fill=(12, 22, 38))
    rng = random.Random(20261122)
    for _ in range(30):
        sx = x + rng.randint(4, w - 4)
        sy = y + rng.randint(4, int(h * 0.55))
        r = rng.choice([1, 1, 2])
        col = (255, 255, 220) if rng.random() < 0.7 else (255, 220, 120)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    # drone trails: white diagonals with orange tips
    trails = [(18, 6, 62, 52), (70, 2, 118, 58), (128, 8, 168, 50),
              (180, 2, 232, 60), (232, 10, 268, 46), (262, 4, 306, 56),
              (100, 0, 140, 34)]
    for (x1, y1, x2, y2) in trails:
        d.line([x + x1, y + y1, x + x2, y + y2], fill=(235, 235, 235), width=2)
        d.ellipse([x + x2 - 3, y + y2 - 3, x + x2 + 3, y + y2 + 3],
                  fill=(255, 140, 30))
    # two tiny drone silhouettes
    for (dx, dy) in [(96, 26), (216, 20)]:
        d.ellipse([x + dx - 7, y + dy - 3, x + dx + 7, y + dy + 3],
                  fill=(8, 8, 8))
        d.line([x + dx - 11, y + dy - 5, x + dx + 11, y + dy - 5],
               fill=(120, 120, 120), width=1)
    # dense skyline with many lit windows
    base = y + h
    heights = [34, 52, 44, 62, 38, 56, 48, 66, 40, 58, 46, 60, 36]
    bx = x
    for hi in heights:
        bw = w // len(heights)
        d.rectangle([bx, base - hi, bx + bw - 2, base], fill=(26, 36, 54))
        for wy in range(base - hi + 6, base - 6, 9):
            for wx in (bx + 4, bx + bw // 2):
                if rng.random() < 0.55:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 90))
        bx += bw
    # big layered fire, centre bottom
    flame(d, x + 150, base - 2, 86, 62, (240, 110, 20), (255, 200, 60))
    flame(d, x + 196, base - 2, 56, 44, (240, 110, 20), (255, 200, 60))
    flame(d, x + 104, base - 2, 44, 34, (240, 110, 20), (255, 200, 60))


def art_bahrain(d, x, y, w, h):
    # R0: round 8's art, kept exactly. The round 9 version (big red
    # tanker + black smoke chain) is NOT used: the tanker hull leaked
    # 14px below the art box and covered "WAR" in the dateline.
    d.rectangle([x, y, x + w, y + h * 0.38], fill=(200, 95, 55))
    d.rectangle([x, y + h * 0.38, x + w, y + h * 0.62], fill=(140, 70, 95))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(30, 55, 95))
    # sun low on the horizon
    d.ellipse([x + w * 0.78, y + h * 0.30, x + w * 0.90, y + h * 0.48],
              fill=(255, 210, 120))
    # storage tanks with flames
    for i, tx in enumerate((0.08, 0.30, 0.52)):
        d.rectangle([x + w * tx, y + h * 0.52, x + w * (tx + 0.16),
                     y + h * 0.72], fill=(225, 225, 220))
        d.ellipse([x + w * tx, y + h * 0.48, x + w * (tx + 0.16),
                   y + h * 0.56], fill=(240, 240, 235))
        d.polygon([(x + w * (tx + 0.03), y + h * 0.50),
                   (x + w * (tx + 0.08), y + h * 0.34),
                   (x + w * (tx + 0.13), y + h * 0.50)],
                  fill=(255, 140, 40))
    # tanker on the water
    d.rectangle([x + w * 0.62, y + h * 0.74, x + w * 0.96, y + h * 0.84],
                fill=(25, 25, 30))
    d.rectangle([x + w * 0.86, y + h * 0.64, x + w * 0.93, y + h * 0.74],
                fill=(40, 40, 48))
    d.polygon([(x + w * 0.68, y + h * 0.74), (x + w * 0.72, y + h * 0.62),
               (x + w * 0.76, y + h * 0.74)], fill=(255, 140, 40))


def art_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.58], fill=(150, 190, 215))
    d.rectangle([x, y + h * 0.58, x + w, y + h], fill=(28, 68, 110))
    for wx in range(5):
        d.arc([x + w * (wx * 0.20), y + h * 0.62,
               x + w * (wx * 0.20 + 0.22), y + h * 0.82], 0, 180,
              fill=(255, 255, 255), width=2)
    # hull, listing slightly
    d.polygon([(x + w * 0.08, y + h * 0.60), (x + w * 0.92, y + h * 0.56),
               (x + w * 0.84, y + h * 0.80), (x + w * 0.16, y + h * 0.80)],
              fill=(140, 40, 35))
    d.rectangle([x + w * 0.55, y + h * 0.40, x + w * 0.75, y + h * 0.57],
                fill=(240, 240, 235))
    # flames + smoke above midship
    d.polygon([(x + w * 0.30, y + h * 0.58), (x + w * 0.38, y + h * 0.30),
               (x + w * 0.46, y + h * 0.58)], fill=(255, 140, 40))
    d.polygon([(x + w * 0.36, y + h * 0.58), (x + w * 0.42, y + h * 0.38),
               (x + w * 0.48, y + h * 0.58)], fill=(255, 220, 90))
    for sx, sy, sr in ((0.44, 0.22, 0.07), (0.50, 0.14, 0.09),
                       (0.58, 0.10, 0.07)):
        d.ellipse([x + w * (sx - sr), y + h * (sy - sr),
                   x + w * (sx + sr), y + h * (sy + sr)],
                  fill=(120, 120, 120))


def art_kryvyi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 215, 200))
    # apartment blocks
    for bx, bh, bw in ((0.04, 0.62, 0.26), (0.34, 0.78, 0.26),
                       (0.64, 0.55, 0.30)):
        d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + bw),
                     y + h], fill=(150, 140, 125))
        for r in range(3):
            for c in range(2):
                d.rectangle([x + w * (bx + 0.05 + c * 0.10),
                             y + h * (1 - bh + 0.08 + r * 0.16),
                             x + w * (bx + 0.10 + c * 0.10),
                             y + h * (1 - bh + 0.16 + r * 0.16)],
                            fill=(60, 60, 60))
    # smoke plume from the middle block
    for sx, sy, sr in ((0.47, 0.18, 0.08), (0.52, 0.10, 0.10),
                       (0.58, 0.05, 0.07)):
        d.ellipse([x + w * (sx - sr), y + h * (sy - sr),
                   x + w * (sx + sr), y + h * (sy + sr)],
                  fill=(110, 110, 110))
    # red-cross sign, bottom right
    d.rectangle([x + w * 0.78, y + h * 0.72, x + w * 0.96, y + h * 0.94],
                fill=(255, 255, 255), outline=RED, width=2)
    d.rectangle([x + w * 0.855, y + h * 0.76, x + w * 0.885, y + h * 0.90],
                fill=RED)
    d.rectangle([x + w * 0.82, y + h * 0.80, x + w * 0.92, y + h * 0.845],
                fill=RED)


def art_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.55], fill=(150, 195, 225))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(30, 90, 140))
    for wx in range(4):
        d.arc([x + w * (wx * 0.25), y + h * 0.58,
               x + w * (wx * 0.25 + 0.28), y + h * 0.78], 0, 180,
              fill=(255, 255, 255), width=3)
    # capsized hull, keel up
    d.polygon([(x + w * 0.20, y + h * 0.52), (x + w * 0.80, y + h * 0.52),
               (x + w * 0.70, y + h * 0.72), (x + w * 0.30, y + h * 0.72)],
              fill=(120, 70, 40))
    d.rectangle([x + w * 0.46, y + h * 0.40, x + w * 0.54, y + h * 0.52],
                fill=(90, 55, 30))
    for px in (0.30, 0.62):
        d.ellipse([x + w * px, y + h * 0.56, x + w * (px + 0.05),
                   y + h * 0.63], fill=(40, 40, 40))


def art_jerusalem(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 228, 210))
    # parliament building: pediment + columns
    d.polygon([(x + w * 0.12, y + h * 0.42), (x + w * 0.50, y + h * 0.22),
               (x + w * 0.88, y + h * 0.42)], fill=(190, 175, 140))
    d.rectangle([x + w * 0.12, y + h * 0.42, x + w * 0.88, y + h * 0.48],
                fill=(205, 190, 155))
    for i in range(4):
        cx = x + w * (0.18 + i * 0.18)
        d.rectangle([cx, y + h * 0.48, cx + w * 0.06, y + h * 0.92],
                    fill=(225, 210, 175))
    d.rectangle([x + w * 0.10, y + h * 0.92, x + w * 0.90, y + h],
                fill=(180, 165, 130))
    # two small flags
    for fx, c1, c2 in ((0.06, (20, 60, 160), (255, 255, 255)),
                       (0.86, (178, 34, 34), (255, 255, 255))):
        d.line([x + w * fx, y + h * 0.30, x + w * fx, y + h * 0.92],
               fill=INK, width=2)
        d.rectangle([x + w * fx, y + h * 0.30, x + w * (fx + 0.10),
                     y + h * 0.42], fill=c1)
        d.rectangle([x + w * fx, y + h * 0.36, x + w * (fx + 0.10),
                     y + h * 0.38], fill=c2)


def art_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.62], fill=(230, 220, 200))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(200, 185, 150))
    # aid truck
    d.rectangle([x + w * 0.12, y + h * 0.42, x + w * 0.62, y + h * 0.72],
                fill=(245, 245, 240), outline=INK, width=1)
    d.rectangle([x + w * 0.62, y + h * 0.52, x + w * 0.80, y + h * 0.72],
                fill=(220, 220, 215), outline=INK, width=1)
    d.rectangle([x + w * 0.30, y + h * 0.50, x + w * 0.44, y + h * 0.64],
                fill=RED)
    d.rectangle([x + w * 0.355, y + h * 0.545, x + w * 0.385,
                 y + h * 0.595], fill=(245, 245, 240))
    for wx in (0.22, 0.52, 0.72):
        d.ellipse([x + w * (wx - 0.045), y + h * 0.70,
                   x + w * (wx + 0.045), y + h * 0.79], fill=(20, 20, 20))
    # explosion cloud above the truck
    for sx, sy, sr, col in ((0.40, 0.22, 0.10, (110, 110, 110)),
                            (0.52, 0.14, 0.12, (140, 140, 140)),
                            (0.62, 0.24, 0.09, (255, 140, 40))):
        d.ellipse([x + w * (sx - sr), y + h * (sy - sr),
                   x + w * (sx + sr), y + h * (sy + sr)], fill=col)


def art_sinaloa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.55], fill=(240, 210, 150))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(190, 150, 95))
    # mountains
    d.polygon([(x, y + h * 0.62), (x + w * 0.30, y + h * 0.28),
               (x + w * 0.55, y + h * 0.62)], fill=(150, 110, 70))
    d.polygon([(x + w * 0.40, y + h * 0.62), (x + w * 0.68, y + h * 0.34),
               (x + w, y + h * 0.62)], fill=(120, 88, 55))
    # helicopter silhouette
    hx, hy = x + w * 0.62, y + h * 0.22
    d.line([hx - w * 0.12, hy, hx + w * 0.12, hy], fill=(30, 30, 30),
           width=3)
    d.ellipse([hx - w * 0.05, hy, hx + w * 0.05, hy + h * 0.10],
              fill=(30, 30, 30))
    d.line([hx + w * 0.05, hy + h * 0.04, hx + w * 0.14, hy - h * 0.02],
           fill=(30, 30, 30), width=2)
    # cactus
    cx = x + w * 0.12
    d.rectangle([cx, y + h * 0.60, cx + w * 0.04, y + h * 0.92],
                fill=(46, 130, 70))
    d.rectangle([cx - w * 0.05, y + h * 0.70, cx, y + h * 0.78],
                fill=(46, 130, 70))
    d.rectangle([cx + w * 0.04, y + h * 0.66, cx + w * 0.09,
                 y + h * 0.74], fill=(46, 130, 70))


def art_tehran(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 40, 60))
    # moon
    d.ellipse([x + w * 0.78, y + h * 0.08, x + w * 0.92, y + h * 0.28],
              fill=(240, 235, 210))
    # dark city with a few lit windows
    for bx, bh in ((0.02, 0.34), (0.22, 0.48), (0.44, 0.30),
                   (0.62, 0.42), (0.82, 0.36)):
        d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + 0.16),
                     y + h], fill=(20, 20, 32))
        d.rectangle([x + w * (bx + 0.05), y + h * (1 - bh + 0.10),
                     x + w * (bx + 0.09), y + h * (1 - bh + 0.18)],
                    fill=(255, 210, 90))
    # transmission pylon, centre
    px = x + w * 0.50
    d.line([px - w * 0.10, y + h, px, y + h * 0.18], fill=(200, 200, 200),
           width=2)
    d.line([px + w * 0.10, y + h, px, y + h * 0.18], fill=(200, 200, 200),
           width=2)
    d.line([px - w * 0.16, y + h * 0.30, px + w * 0.16, y + h * 0.30],
           fill=(200, 200, 200), width=2)
    d.line([px - w * 0.12, y + h * 0.48, px + w * 0.12, y + h * 0.48],
           fill=(200, 200, 200), width=2)


def art_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 240, 235))
    # chip, left
    cx, cy, s = x + w * 0.28, y + h * 0.52, h * 0.44
    for i in range(4):
        d.line([cx - s / 2, cy - s / 2 + i * s / 3,
                cx - s / 2 - w * 0.06, cy - s / 2 + i * s / 3],
               fill=(200, 170, 60), width=2)
        d.line([cx + s / 2, cy - s / 2 + i * s / 3,
                cx + s / 2 + w * 0.06, cy - s / 2 + i * s / 3],
               fill=(200, 170, 60), width=2)
    d.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2],
                fill=(30, 110, 70))
    d.rectangle([cx - s / 4, cy - s / 4, cx + s / 4, cy + s / 4],
                fill=(20, 80, 50))
    # falling line chart, right
    d.line([x + w * 0.58, y + h * 0.30, x + w * 0.72, y + h * 0.52,
            x + w * 0.84, y + h * 0.44, x + w * 0.96, y + h * 0.70],
           fill=(178, 34, 34), width=3)
    # magnifier over the chip
    mx, my, mr = x + w * 0.52, y + h * 0.34, h * 0.20
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr],
              outline=INK, width=3)
    d.line([mx + mr * 0.7, my + mr * 0.7, mx + mr * 1.3, my + mr * 1.3],
           fill=INK, width=3)


def art_bolsonaro(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 232, 225))
    # monitor with heartbeat line
    d.rectangle([x + w * 0.62, y + h * 0.10, x + w * 0.94, y + h * 0.44],
                fill=(20, 30, 40))
    d.line([x + w * 0.65, y + h * 0.30, x + w * 0.72, y + h * 0.30,
            x + w * 0.76, y + h * 0.18, x + w * 0.80, y + h * 0.38,
            x + w * 0.84, y + h * 0.30, x + w * 0.91, y + h * 0.30],
           fill=(80, 220, 120), width=2)
    # hospital bed
    d.rectangle([x + w * 0.08, y + h * 0.58, x + w * 0.58, y + h * 0.72],
                fill=(245, 245, 240), outline=INK, width=1)
    d.rectangle([x + w * 0.08, y + h * 0.50, x + w * 0.22, y + h * 0.58],
                fill=(255, 255, 255), outline=INK, width=1)
    d.ellipse([x + w * 0.11, y + h * 0.42, x + w * 0.19, y + h * 0.52],
              fill=(232, 202, 162))
    d.rectangle([x + w * 0.24, y + h * 0.58, x + w * 0.58, y + h * 0.72],
                fill=(140, 180, 210))
    for lx in (0.14, 0.52):
        d.ellipse([x + w * (lx - 0.03), y + h * 0.72,
                   x + w * (lx + 0.03), y + h * 0.80], fill=(20, 20, 20))
    # IV pole + bag
    d.line([x + w * 0.66, y + h * 0.20, x + w * 0.66, y + h * 0.72],
           fill=INK, width=2)
    d.rectangle([x + w * 0.60, y + h * 0.22, x + w * 0.72, y + h * 0.42],
                fill=(220, 235, 245), outline=INK, width=1)


def art_hongkong(d, x, y, w, h):
    # R12: ballot box with a ballot paper and a green check. Fresh in
    # this session; relative coordinates only, like the other art.
    d.rectangle([x, y, x + w, y + h], fill=(198, 222, 238))
    # three voter dots, top
    for i, vx in enumerate((0.20, 0.50, 0.80)):
        d.ellipse([x + w * (vx - 0.05), y + h * 0.10,
                   x + w * (vx + 0.05), y + h * 0.24], fill=(232, 190, 150))
        d.rectangle([x + w * (vx - 0.09), y + h * 0.26,
                     x + w * (vx + 0.09), y + h * 0.38],
                    fill=((31, 56, 100), (176, 42, 42), (46, 125, 79))[i])
    # ballot box, centre
    d.rectangle([x + w * 0.28, y + h * 0.44, x + w * 0.72, y + h * 0.92],
                fill=(31, 58, 110))
    d.rectangle([x + w * 0.24, y + h * 0.38, x + w * 0.76, y + h * 0.46],
                fill=(20, 40, 80))
    d.rectangle([x + w * 0.44, y + h * 0.40, x + w * 0.56, y + h * 0.44],
                fill=(10, 10, 10))
    # ballot paper sliding into the slot, with a green check
    d.polygon([(x + w * 0.40, y + h * 0.40), (x + w * 0.60, y + h * 0.40),
               (x + w * 0.56, y + h * 0.14), (x + w * 0.44, y + h * 0.14)],
              fill=(255, 255, 255), outline=INK)
    d.line([x + w * 0.46, y + h * 0.28, x + w * 0.49, y + h * 0.33,
            x + w * 0.55, y + h * 0.20], fill=(30, 160, 70), width=3)


def art_estonia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.60], fill=(170, 200, 220))
    d.rectangle([x, y + h * 0.60, x + w, y + h], fill=(120, 140, 90))
    # pine forest
    for i, px in enumerate((0.06, 0.22, 0.38, 0.54, 0.70, 0.86)):
        ph = h * (0.30 + 0.08 * (i % 3))
        d.polygon([(x + w * (px - 0.07), y + h * 0.62),
                   (x + w * px, y + h * 0.62 - ph),
                   (x + w * (px + 0.07), y + h * 0.62)],
                  fill=(30, 90, 50))
    # border fence: posts + wire
    for i in range(6):
        fx = x + w * (0.04 + i * 0.18)
        d.rectangle([fx, y + h * 0.52, fx + 3, y + h * 0.92],
                    fill=(90, 70, 50))
    d.line([x, y + h * 0.58, x + w, y + h * 0.58], fill=(60, 60, 60),
           width=2)
    d.line([x, y + h * 0.74, x + w, y + h * 0.74], fill=(60, 60, 60),
           width=2)
    # red-white barrier bar
    d.rectangle([x + w * 0.30, y + h * 0.78, x + w * 0.70, y + h * 0.86],
                fill=(255, 255, 255), outline=INK, width=1)
    d.rectangle([x + w * 0.30, y + h * 0.78, x + w * 0.40, y + h * 0.86],
                fill=(178, 34, 34))
    d.rectangle([x + w * 0.50, y + h * 0.78, x + w * 0.60, y + h * 0.86],
                fill=(178, 34, 34))


ART = {
    "cop31": art_cop31,
    "barrage": art_barrage,
    "bahrain": art_bahrain,
    "ship": art_ship,
    "kryvyi": art_kryvyi,
    "boat": art_boat,
    "jerusalem": art_jerusalem,
    "gaza": art_gaza,
    "sinaloa": art_sinaloa,
    "tehran": art_tehran,
    "nvidia": art_nvidia,
    "bolsonaro": art_bolsonaro,
    "estonia": art_estonia,
    "hongkong": art_hongkong,
}

# ------------------------------------------------------------- map ---
# Coarse equirectangular land grid, 64 cols (lon -180..180) x 32 rows
# (lat 90..-60). Each row lists inclusive column ranges that are land.
LAND_ROWS = [
    [],
    [(22, 27)],
    [(18, 28), (35, 35)],
    [(10, 28), (40, 63)],
    [(4, 28), (33, 63)],
    [(5, 26), (31, 31), (33, 63)],
    [(6, 25), (30, 31), (33, 62)],
    [(7, 24), (30, 61)],
    [(8, 23), (30, 60)],
    [(9, 22), (31, 59)],
    [(10, 21), (31, 58)],
    [(11, 20), (30, 57)],
    [(12, 18), (29, 40), (42, 45), (48, 51), (53, 56)],
    [(11, 19), (29, 40), (42, 44), (49, 51), (52, 55)],
    [(12, 17), (30, 40), (49, 50), (52, 55)],
    [(17, 20), (30, 39), (49, 49), (52, 54)],
    [(18, 21), (30, 39), (52, 55)],
    [(19, 23), (30, 38), (51, 56)],
    [(19, 24), (30, 37), (52, 58)],
    [(19, 24), (31, 37), (57, 58)],
    [(19, 24), (31, 36)],
    [(19, 24), (31, 36), (52, 57)],
    [(20, 24), (32, 36), (52, 58)],
    [(20, 23), (32, 35), (52, 58)],
    [(20, 23), (32, 35), (53, 57)],
    [(20, 22), (32, 34), (53, 57)],
    [(20, 22), (32, 33), (54, 56)],
    [(20, 21), (58, 59)],
    [(20, 21)],
    [(20, 20)],
    [(20, 20)],
    [],
]

# story id -> (lat, lon, dx, dy): pin position + fan-out offset so the
# dense Europe / Middle East cluster stays readable.
PINS = {
    1: (36.9, 30.7, -12, 8),      # Antalya
    2: (50.4, 30.5, 10, -6),      # Kyiv
    3: (26.2, 50.6, 8, 10),       # Manama
    4: (59.8, 25.0, 12, -12),     # Gulf of Finland
    5: (47.9, 33.4, -12, -2),     # Kryvyi Rih
    6: (4.9, 6.3, 0, 0),          # Bayelsa
    7: (31.8, 35.2, 4, 12),       # Jerusalem
    8: (31.5, 34.5, 16, 6),       # Gaza
    9: (24.8, -107.4, 0, 0),      # Sinaloa
    10: (35.7, 51.4, 12, -8),     # Tehran
    11: (22.3, 114.2, 10, -6),     # Hong Kong (R12: was Washington/Nvidia)
    12: (-15.8, -47.9, 0, 0),     # Brasilia
    13: (59.4, 24.7, -12, -10),   # Tallinn
}

REGION_COLORS = [
    ("EUROPE", 140, (31, 58, 110)),
    ("MIDDLE EAST", 190, (178, 34, 34)),
    ("AMERICAS", 140, (46, 125, 79)),
    ("ASIA-PACIFIC", 160, (176, 124, 11)),
    ("AFRICA", 90, (122, 74, 33)),
    ("OCEANIA", 110, (60, 110, 140)),
    ("WORLD", 154, (91, 74, 138)),
]


def draw_map(d, x, y, w, h):
    """Dotted world map with numbered red pins for stories 1-13."""
    d.rectangle([x, y, x + w, y + h], fill=SEA)  # R1: pale-blue sea
    cols, rows = 64, 32
    sx, sy = w / cols, h / rows
    for r, ranges in enumerate(LAND_ROWS):
        cy = y + (r + 0.5) * sy
        for lo, hi in ranges:
            for c in range(lo, hi + 1):
                cx = x + (c + 0.5) * sx
                d.ellipse([cx - 1.7, cy - 1.7, cx + 1.7, cy + 1.7],
                          fill=(150, 140, 110))
    f_pin = font(SANS_B, 8)
    for sid, (lat, lon, dx, dy) in PINS.items():
        px = x + (lon + 180) / 360 * w + dx
        py = y + (90 - lat) / 150 * h + dy
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        num = str(sid)
        nw = d.textlength(num, font=f_pin)
        d.text((px - nw / 2, py - 4), num, font=f_pin,
               fill=(255, 255, 255))


def render():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    ed = data["edition"]
    stories = data["stories"]
    heroes = [s for s in stories if s["kind"] == "hero"]
    cards = [s for s in stories if s["kind"] == "card"]
    lst = [s for s in stories if s["kind"] == "list"]
    assert len(heroes) == 3 and len(cards) == 10 and len(lst) == 22, (
        len(heroes), len(cards), len(lst))
    assert len(stories) == 35

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top bar ----
    d.rectangle([0, 0, W, 28], fill=NAVY)
    f_bar = font(SANS_B, 14)
    d.text((X0, 7), ed["title"], font=f_bar, fill=(255, 255, 255))
    f_bar2 = font(SANS_B, 11)
    bar_right = ed["subtitle"].upper()
    rw = d.textlength(bar_right, font=f_bar2)
    d.text((X0 + CW - rw, 8), bar_right, font=f_bar2, fill=(255, 255, 255))

    # ---- masthead + kicker ----
    f_mast = font(SERIF, 58)
    d.text((X0, 34), ed["date"], font=f_mast, fill=INK)
    f_kick = font(SERIF_I, 19)
    d.text((X0, 102), ed["kicker"], font=f_kick, fill=RED)
    d.line([X0, 128, X0 + CW, 128], fill=INK, width=2)

    # ---- stat strip: 6 big numbers from the 3 lead stories ----
    f_stat = font(SANS_B, 28)
    f_statcap = font(SANS, 10)
    col_w = CW // 6
    for i, st in enumerate(ed["stats"]):
        cx = X0 + i * col_w
        d.text((cx + 4, 134), st["value"], font=f_stat, fill=RED)
        cap_lines = wrap(d, st["label"], f_statcap, col_w - 6)
        yy = 166
        for ln in cap_lines[:2]:
            d.text((cx + 4, yy), ln, font=f_statcap, fill=MUTED)
            yy += 13
        if i:
            d.line([cx, 136, cx, 180], fill=RULE, width=1)
    d.line([X0, 184, X0 + CW, 184], fill=INK, width=2)

    # ---- region bar: 6 regions, counts sum to 35 ----
    rx, ry = X0, 190
    f_reg = font(SANS_B, 13)
    for name, wseg, color in REGION_COLORS:
        d.rectangle([rx, ry, rx + wseg, ry + 24], fill=color)
        label = f"{name} {dict((r['name'], r['count']) for r in ed['regions'])[name]}"
        lw = d.textlength(label, font=f_reg)
        d.text((rx + (wseg - lw) / 2, ry + 5), label, font=f_reg,
               fill=(255, 255, 255))
        rx += wseg
    assert rx == X0 + CW

    # ---- THE DAY IN UTC strip (R12: the winning formula's timeline) ----
    uy = 216
    f_utc = font(SANS_B, 11)
    f_utc2 = font(SANS, 11)
    d.text((X0, uy + 2), "THE DAY IN UTC", font=f_utc, fill=RED)
    utc_items = ("01:00 Hong Kong polls open \u00b7 03:00 COP31 objections "
                 "close \u00b7 05:30 Verstappen wins Las Vegas \u00b7 06:00 "
                 "COP31 approval due \u00b7 08:00 161 of 186 drones downed")
    uw = d.textlength("THE DAY IN UTC  ", font=f_utc)
    d.text((X0 + uw, uy + 2), utc_items, font=f_utc2, fill=INK)
    d.line([X0, uy + 20, X0 + CW, uy + 20], fill=RULE, width=1)

    # ---- 3 heroes ----
    hw, gap = 320, 12
    hy = 240
    f_tag = font(SANS_B, 13)
    f_badge = font(SANS_B, 12)
    f_cap = font(SANS, 10)
    f_loc = font(SANS_B, 12)
    f_hhead = font(SERIF, 22)
    f_hdeck = font(SANS, 12)
    for i, s in enumerate(heroes):
        hx = X0 + i * (hw + gap)
        ART[s["art"]](d, hx, hy, hw, 128)
        # tag top-left, badge top-right, caption chip bottom-left
        tag = s["tag"]
        tw = d.textlength(tag, font=f_tag)
        d.rectangle([hx, hy, hx + tw + 14, hy + 22], fill=RED)
        d.text((hx + 7, hy + 4), tag, font=f_tag, fill=(255, 255, 255))
        badge = s["badge"]
        bw = d.textlength(badge, font=f_badge)
        d.rectangle([hx + hw - bw - 12, hy, hx + hw, hy + 20],
                    fill=(255, 255, 255))
        d.text((hx + hw - bw - 6, hy + 3), badge, font=f_badge, fill=INK)
        cap = s["caption"]
        cw2 = d.textlength(cap, font=f_cap)
        d.rectangle([hx, hy + 128 - 18, hx + cw2 + 10, hy + 128],
                    fill=(10, 10, 10))
        d.text((hx + 5, hy + 128 - 15), cap, font=f_cap,
               fill=(255, 255, 255))
        # R2: TOP STORY label under the tag bar on hero 1
        if s["id"] == 1:
            top = "TOP STORY"
            tw2 = d.textlength(top, font=f_cap)
            d.rectangle([hx + 6, hy + 26, hx + 6 + tw2 + 12, hy + 26 + 18],
                        fill=(10, 10, 10))
            d.text((hx + 11, hy + 29), top, font=f_cap,
                   fill=(255, 255, 255))
        # location, headline, deck
        loc = f"{s['id']} {s['location']} · {s['topic']}"
        d.text((hx, hy + 134), loc, font=f_loc, fill=RED)
        head_lines = fit_text(d, s["title"], f_hhead, hw, 2)
        yy = hy + 152
        for ln in head_lines:
            d.text((hx, yy), ln, font=f_hhead, fill=INK)
            yy += 25
        deck = s["deck"] + f" ({s['source']})"
        deck_lines = fit_text(d, deck, f_hdeck, hw, 3)
        yy = hy + 204
        for ln in deck_lines:
            d.text((hx, yy), ln, font=f_hdeck, fill=MUTED)
            yy += 15

    # ---- 10 numbered cards, 2 rows of 5 ----
    cw3, cgap = 188, 11
    f_cloc = font(SANS_B, 11)
    f_ctitle = font(SANS_B, 14)
    f_cdeck = font(SANS, 11)
    f_cnum = font(SANS_B, 11)
    for row in range(2):
        cy = 496 + row * 158
        for col in range(5):
            s = cards[row * 5 + col]
            cx = X0 + col * (cw3 + cgap)
            ART[s["art"]](d, cx, cy, cw3, 68)
            # tag top-left, number circle top-right
            tag = s["tag"]
            tw = d.textlength(tag, font=f_tag)
            d.rectangle([cx, cy, cx + tw + 12, cy + 20], fill=RED)
            d.text((cx + 6, cy + 3), tag, font=f_tag, fill=(255, 255, 255))
            num = str(s["id"])
            nx = cx + cw3 - 20
            d.ellipse([nx, cy + 2, nx + 18, cy + 20], fill=(255, 255, 255),
                      outline=RED, width=2)
            nw = d.textlength(num, font=f_cnum)
            d.text((nx + 9 - nw / 2, cy + 5), num, font=f_cnum, fill=RED)
            # location, headline, deck
            loc = f"{s['location']}"
            d.text((cx, cy + 74), loc, font=f_cloc, fill=RED)
            title_lines = fit_text(d, s["title"], f_ctitle, cw3, 2)
            yy = cy + 90
            for ln in title_lines:
                d.text((cx, yy), ln, font=f_ctitle, fill=INK)
                yy += 17
            deck = s["deck"] + f" ({s['source']})"
            deck_lines = fit_text(d, deck, f_cdeck, cw3, 2)
            yy = cy + 126
            for ln in deck_lines:
                d.text((cx, yy), ln, font=f_cdeck, fill=MUTED)
                yy += 13

    # ---- bottom: map (left) + ALSO ON list (right) ----
    by = 816
    f_bh = font(SANS_B, 12)
    f_bsub = font(SANS, 10)
    d.text((X0, by), "WHERE IT HAPPENED", font=f_bh, fill=INK)
    sub = "pins match story numbers"
    d.text((X0 + 148, by + 1), sub, font=f_bsub, fill=MUTED)
    list_x = X0 + 360
    d.text((list_x, by), "ALSO ON SUNDAY 22 NOVEMBER — 22 MORE STORIES",
           font=f_bh, fill=INK)
    map_y = by + 20
    draw_map(d, X0, map_y, 340, 122)
    # list: 2 columns of 11, one line each
    f_li = font(SANS, 10)
    f_ln = font(SANS_B, 10)
    col_w2 = 307
    for i, s in enumerate(lst):
        col = i // 11
        row = i % 11
        lx = list_x + col * (col_w2 + 10)
        ly = map_y + row * 11
        num = str(s["id"])
        d.text((lx, ly), num, font=f_ln, fill=RED)
        nw = d.textlength(num + " ", font=f_ln)
        line = one_line(d, f"{s['title']} ({s['source']})", f_li,
                        col_w2 - nw)
        d.text((lx + nw, ly), line, font=f_li, fill=INK)

    # ---- DATE CHECK box ----
    dy = 962
    d.rectangle([X0, dy, X0 + CW, dy + 32], outline=RED, width=2)
    f_dc = font(SANS_B, 11)
    f_dc2 = font(SANS, 11)
    d.text((X0 + 8, dy + 4), "DATE CHECK", font=f_dc, fill=RED)
    dc_lines = wrap(d, ed["datecheck"], f_dc2, CW - 110)
    yy = dy + 4
    for ln in dc_lines[:2]:
        d.text((X0 + 96, yy), ln, font=f_dc2, fill=INK)
        yy += 13

    # ---- sources + footer ----
    f_ft = font(SANS, 9)
    foot = ("Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, Sky News, "
            "CNA, ABC, Times of India, The Guardian, Kyiv Independent. "
            "Every story names its outlet. "
            "Pictures and map: original, drawn in code.")
    d.text((X0, 998), foot, font=f_ft, fill=MUTED)
    f_ft2 = font(SANS_B, 10)
    d.text((X0, 1010), ed["title"], font=f_ft2, fill=INK)
    tag = "SUNDAY 22 NOVEMBER 2026 · ONE PAGE"
    tw = d.textlength(tag, font=f_ft2)
    d.text((X0 + CW - tw, 1010), tag, font=f_ft2, fill=INK)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    render()
