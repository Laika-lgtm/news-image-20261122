#!/usr/bin/env python3
"""Render the one-page front page for news-image-20261122 (round 9).

Draws the whole page with PIL from stories.json: masthead, title, kicker,
stat strip, region bar, three hero stories, ten small cards, dotted world
map with numbered pins, the ALSO list, a DATE CHECK box, sources and footer.
Every picture on the page is drawn in code (flat original illustrations).
Run:  python3 render_frontpage.py   ->  writes entry.png (1024x1024).
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
LIB_DIR = "/usr/share/fonts/truetype/liberation"

SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_IT = os.path.join(LIB_DIR, "LiberationSerif-Italic.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

W, H = 1024, 1024
MARGIN = 20
CW = W - 2 * MARGIN  # 984

CREAM = (247, 242, 227)
INK = (28, 28, 28)
NAVY = (27, 42, 74)
RED = (168, 31, 31)
RED_DK = (140, 22, 22)
GRAY = (96, 90, 78)
GRAY_LT = (190, 184, 168)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
SEA = (211, 230, 242)
LAND = (184, 168, 136)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def chip(draw, x, y, text, fnt, fg, bg, pad=5, h=None):
    """Small rounded label; returns its width."""
    tw = text_w(draw, text, fnt)
    hh = h if h else fnt.size + 2 * pad - 2
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + hh], radius=3, fill=bg)
    draw.text((x + pad, y + (hh - fnt.size) // 2 - 1), text, font=fnt, fill=fg)
    return tw + 2 * pad


def number_circle(draw, cx, cy, n, r=11):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=2)
    fnt = font(SANS_B, 12)
    label = str(n)
    tw = text_w(draw, label, fnt)
    draw.text((cx - tw / 2, cy - 8), label, font=fnt, fill=WHITE)


def flame(draw, cx, base_y, w, h, col_out, col_in):
    """A layered flame: outer teardrop + inner teardrop, centred on cx."""
    # outer flame: polygon with a wavy top
    pts_out = [
        (cx - w / 2, base_y),
        (cx - w / 2, base_y - h * 0.45),
        (cx - w * 0.18, base_y - h * 0.75),
        (cx, base_y - h),
        (cx + w * 0.22, base_y - h * 0.62),
        (cx + w / 2, base_y - h * 0.4),
        (cx + w / 2, base_y),
    ]
    draw.polygon(pts_out, fill=col_out)
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
    draw.polygon(pts_in, fill=col_in)


# ---------------------------------------------------------------- art: heroes

def art_hero_cop31(draw, x, y, w, h):
    """B1: COP31 summit. Whole blue globe, 8 coloured delegates with
    placards behind a table, tall red thermometer, clock, green floor."""
    draw.rectangle([x, y, x + w, y + h], fill=(183, 220, 239))
    # green floor strip
    draw.rectangle([x, y + h - 12, x + w, y + h], fill=(90, 138, 74))
    # whole blue globe, left, fully inside the frame
    gx, gy, gr = x + 54, y + 52, 36
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(46, 122, 194))
    draw.ellipse([gx - gr + 8, gy - gr + 10, gx - gr + 26, gy - gr + 24],
                 fill=(58, 154, 90))
    draw.ellipse([gx + 2, gy + 2, gx + 22, gy + 16], fill=(58, 154, 90))
    draw.ellipse([gx - gr + 14, gy + gr - 22, gx - gr + 30, gy + gr - 8],
                 fill=(58, 154, 90))
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], start=200, end=330,
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
        draw.rounded_rectangle([px, y + 62, px + 20, base_y], radius=5, fill=col)
        # head
        draw.ellipse([px + 4, y + 50, px + 16, y + 62], fill=(232, 190, 150))
        # placard on a stick, in front of the table
        pc = plac_cols[i % 4]
        draw.line([px + 10, y + 78, px + 10, y + 96], fill=(60, 60, 60), width=1)
        draw.rectangle([px + 3, y + 90, px + 17, y + 100], fill=pc)
    # long brown table in front of the delegates
    draw.rectangle([x + 100, y + 96, x + w - 8, y + 112], fill=(138, 106, 69))
    draw.rectangle([x + 100, y + 96, x + w - 8, y + 100], fill=(160, 128, 88))
    # tall red thermometer at the right edge
    tx = x + w - 20
    draw.rectangle([tx - 3, y + 16, tx + 3, y + 92], fill=(200, 40, 40))
    draw.rectangle([tx - 3, y + 16, tx + 3, y + 30], fill=(230, 120, 120))
    draw.ellipse([tx - 9, y + 88, tx + 9, y + 106], fill=(200, 40, 40))
    draw.ellipse([tx - 5, y + 92, tx + 5, y + 102], fill=(230, 90, 90))
    # wall clock, top right, fully inside
    cx, cy, cr = x + w - 46, y + 26, 15
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=WHITE,
                 outline=(30, 30, 30), width=2)
    draw.line([cx, cy, cx - 6, cy - 7], fill=(30, 30, 30), width=2)
    draw.line([cx, cy, cx + 7, cy - 3], fill=(30, 30, 30), width=2)
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(30, 30, 30))


def art_hero_ukraine(draw, x, y, w, h):
    """B3: night barrage. Starry dark sky, many white drone trails with
    orange dots and small drone silhouettes, dense lit skyline, big
    layered fire at centre bottom."""
    draw.rectangle([x, y, x + w, y + h], fill=(12, 22, 38))
    rng = random.Random(20261122)
    for _ in range(30):
        sx = x + rng.randint(4, w - 4)
        sy = y + rng.randint(4, int(h * 0.55))
        r = rng.choice([1, 1, 2])
        col = (255, 255, 220) if rng.random() < 0.7 else (255, 220, 120)
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=col)
    # drone trails: white diagonals with orange tips
    trails = [(18, 6, 62, 52), (70, 2, 118, 58), (128, 8, 168, 50),
              (180, 2, 232, 60), (232, 10, 268, 46), (262, 4, 306, 56),
              (100, 0, 140, 34)]
    for (x1, y1, x2, y2) in trails:
        draw.line([x + x1, y + y1, x + x2, y + y2], fill=(235, 235, 235), width=2)
        draw.ellipse([x + x2 - 3, y + y2 - 3, x + x2 + 3, y + y2 + 3],
                     fill=(255, 140, 30))
    # two tiny drone silhouettes
    for (dx, dy) in [(96, 26), (216, 20)]:
        draw.ellipse([x + dx - 7, y + dy - 3, x + dx + 7, y + dy + 3],
                     fill=(8, 8, 8))
        draw.line([x + dx - 11, y + dy - 5, x + dx + 11, y + dy - 5],
                  fill=(120, 120, 120), width=1)
    # dense skyline with many lit windows
    base = y + h
    heights = [34, 52, 44, 62, 38, 56, 48, 66, 40, 58, 46, 60, 36]
    bx = x
    for hi in heights:
        bw = w // len(heights)
        draw.rectangle([bx, base - hi, bx + bw - 2, base], fill=(26, 36, 54))
        for wy in range(base - hi + 6, base - 6, 9):
            for wx in (bx + 4, bx + bw // 2):
                if rng.random() < 0.55:
                    draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 210, 90))
        bx += bw
    # big layered fire, centre bottom
    flame(draw, x + 150, base - 2, 86, 62, (240, 110, 20), (255, 200, 60))
    flame(draw, x + 196, base - 2, 56, 44, (240, 110, 20), (255, 200, 60))
    flame(draw, x + 104, base - 2, 44, 34, (240, 110, 20), (255, 200, 60))


def art_hero_bahrain(draw, x, y, w, h):
    """B2: Bahrain strike. Orange-to-dark gradient sky, white missile
    trails, layered flames of varied shapes on white tanks, a big
    red-hulled tanker burning with black smoke, dark water at the base."""
    bands = 26
    top = (232, 145, 47)
    bot = (46, 26, 18)
    for i in range(bands):
        t = i / (bands - 1)
        col = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        draw.rectangle([x, y + i * h // bands, x + w,
                        y + (i + 1) * h // bands + 1], fill=col)
    # missile trails from top left, white with orange tips
    for (x1, y1, x2, y2) in [(14, 4, 78, 44), (52, 2, 116, 40),
                             (96, 6, 150, 42), (150, 2, 196, 34)]:
        draw.line([x + x1, y + y1, x + x2, y + y2], fill=(245, 245, 245), width=2)
        draw.ellipse([x + x2 - 3, y + y2 - 3, x + x2 + 3, y + y2 + 3],
                     fill=(255, 140, 30))
    # three white storage tanks with varied layered flames
    tank_xs = [x + 18, x + 108, x + 198]
    tank_ws = [72, 78, 66]
    flame_ws = [46, 58, 38]
    flame_hs = [34, 44, 28]
    for tx, tw, fw, fh in zip(tank_xs, tank_ws, flame_ws, flame_hs):
        draw.rounded_rectangle([tx, y + 62, tx + tw, y + 104], radius=6,
                               fill=(232, 232, 232))
        draw.rectangle([tx, y + 62, tx + tw, y + 70], fill=(200, 200, 200))
        flame(draw, tx + tw // 2, y + 64, fw, fh, (240, 110, 20),
              (255, 205, 70))
    # dark water strip
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(18, 32, 48))
    # big red tanker, burning, with black smoke
    hx0, hy0 = x + 168, y + 92
    draw.polygon([(hx0, hy0), (hx0 + 138, hy0), (hx0 + 128, hy0 + 20),
                  (hx0 + 8, hy0 + 20)], fill=(168, 31, 31))
    draw.rectangle([hx0 + 6, hy0 - 12, hx0 + 34, hy0], fill=(220, 220, 220))
    draw.rectangle([hx0 + 6, hy0 - 12, hx0 + 34, hy0 - 8], fill=(120, 120, 120))
    flame(draw, hx0 + 70, hy0 + 2, 54, 40, (240, 110, 20), (255, 200, 60))
    flame(draw, hx0 + 112, hy0 + 2, 34, 26, (240, 110, 20), (255, 200, 60))
    for (sx, sy, sr) in [(hx0 + 52, hy0 - 26, 10), (hx0 + 66, hy0 - 40, 12),
                         (hx0 + 84, hy0 - 54, 13), (hx0 + 104, hy0 - 66, 11),
                         (hx0 + 122, hy0 - 76, 9)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(42, 42, 42))
        draw.ellipse([sx - sr + 4, sy - sr + 3, sx + sr - 3, sy + sr - 4],
                     fill=(58, 58, 58))


# ---------------------------------------------------------------- art: cards

def art_card(draw, n, x, y, w, h):
    """B4: richer small illustrations, one per card, with a dusk sky or a
    specific setting instead of a flat backdrop."""
    if n == 4:  # Gulf of Finland: ship ablaze on a dark sea
        draw.rectangle([x, y, x + w, y + h], fill=(150, 190, 220))
        draw.rectangle([x, y + h * 0.45, x + w, y + h], fill=(24, 62, 110))
        draw.polygon([(x + 30, y + h * 0.52), (x + w - 24, y + h * 0.52),
                      (x + w - 40, y + h * 0.78), (x + 44, y + h * 0.78)],
                     fill=(150, 28, 28))
        draw.rectangle([x + 108, y + h * 0.34, x + w - 52, y + h * 0.52],
                       fill=(235, 235, 235))
        flame(draw, x + 78, y + h * 0.54, 40, 30, (240, 110, 20),
              (255, 200, 60))
        for (sx, sy, sr) in [(x + 66, y + 8, 7), (x + 80, y + 2, 9)]:
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(110, 110, 110))
        for wy in (y + h * 0.82, y + h * 0.9):
            draw.line([x + 8, wy, x + w - 8, wy - 3], fill=(220, 235, 245), width=2)
    elif n == 5:  # Kryvyi Rih: dusk skyline, lit windows, small fire glow
        for i in range(8):
            t = i / 7
            col = tuple(int(106 + (210 - 106) * t) for _ in range(1)) * 3
            col = (int(106 + 104 * t), int(90 + 70 * t), int(122 + 10 * t))
            draw.rectangle([x, y + i * h // 8, x + w, y + (i + 1) * h // 8 + 1],
                           fill=col)
        rng = random.Random(55)
        bx = x + 4
        for bw, bh in [(52, 34), (44, 46), (48, 30), (40, 40)]:
            draw.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(32, 30, 44))
            for wy in range(y + h - bh + 6, y + h - 5, 9):
                for wx in (bx + 6, bx + bw // 2 + 2):
                    if rng.random() < 0.6:
                        draw.rectangle([wx, wy, wx + 3, wy + 4],
                                       fill=(255, 210, 90))
            bx += bw + 4
        flame(draw, x + w - 34, y + h - 2, 30, 20, (240, 110, 20),
              (255, 200, 60))
        draw.rectangle([x + w - 46, y + h - 22, x + w - 12, y + h - 8],
                       fill=WHITE)
        draw.rectangle([x + w - 44, y + h - 20, x + w - 14, y + h - 16],
                       fill=(200, 40, 40))
        draw.rectangle([x + w - 32, y + h - 20, x + w - 28, y + h - 10],
                       fill=(200, 40, 40))
    elif n == 6:  # Bayelsa: boat with mourners on a blue sea
        draw.rectangle([x, y, x + w, y + h], fill=(168, 200, 230))
        draw.rectangle([x, y + h * 0.42, x + w, y + h], fill=(31, 90, 154))
        draw.polygon([(x + 36, y + h * 0.5), (x + w - 30, y + h * 0.5),
                      (x + w - 48, y + h * 0.74), (x + 52, y + h * 0.74)],
                     fill=(122, 74, 42))
        draw.rectangle([x + 82, y + h * 0.38, x + w - 86, y + h * 0.5],
                       fill=(96, 58, 32))
        for px in (x + 66, x + 84, x + 102, x + 120):
            draw.ellipse([px, y + h * 0.44, px + 6, y + h * 0.5], fill=(40, 30, 20))
        for wy in (y + h * 0.8, y + h * 0.88):
            draw.line([x + 6, wy, x + w - 6, wy - 2], fill=(225, 240, 250), width=2)
    elif n == 7:  # Jerusalem: columned building, two flags
        draw.rectangle([x, y, x + w, y + h], fill=(232, 216, 184))
        draw.polygon([(x + 20, y + h * 0.3), (x + w // 2, y + h * 0.12),
                      (x + w - 20, y + h * 0.3)], fill=(200, 180, 140))
        draw.rectangle([x + 18, y + h * 0.3, x + w - 18, y + h * 0.82],
                       fill=(214, 196, 160))
        for cx in (x + 34, x + 74, x + 114, x + 150):
            draw.rectangle([cx, y + h * 0.36, cx + 10, y + h * 0.82],
                           fill=(190, 170, 130))
        draw.line([x + 12, y + h * 0.2, x + 12, y + h * 0.55], fill=(60, 60, 60),
                  width=2)
        draw.rectangle([x + 12, y + h * 0.2, x + 28, y + h * 0.28], fill=(40, 80, 180))
        draw.line([x + w - 12, y + h * 0.2, x + w - 12, y + h * 0.55],
                  fill=(60, 60, 60), width=2)
        draw.rectangle([x + w - 28, y + h * 0.2, x + w - 12, y + h * 0.28],
                       fill=(200, 40, 40))
    elif n == 8:  # Gaza: white aid truck, smoke above
        draw.rectangle([x, y, x + w, y + h], fill=(224, 216, 200))
        for (sx, sy, sr, col) in [(x + 40, y + 10, 12, (120, 120, 120)),
                                  (x + 62, y + 4, 14, (140, 140, 140)),
                                  (x + 128, y + 8, 11, (150, 150, 150))]:
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=col)
        flame(draw, x + 150, y + 22, 26, 16, (240, 110, 20), (255, 200, 60))
        draw.rectangle([x + 22, y + h * 0.42, x + w - 60, y + h * 0.68],
                       fill=WHITE, outline=(180, 180, 180))
        draw.rectangle([x + w - 58, y + h * 0.5, x + w - 22, y + h * 0.68],
                       fill=(230, 230, 230), outline=(180, 180, 180))
        draw.rectangle([x + 44, y + h * 0.48, x + 66, y + h * 0.62],
                       fill=(200, 40, 40))
        draw.rectangle([x + 52, y + h * 0.48, x + 58, y + h * 0.62],
                       fill=WHITE)
        for wx in (x + 44, x + 140):
            draw.ellipse([wx - 7, y + h * 0.66, wx + 7, y + h * 0.8], fill=(30, 30, 30))
    elif n == 9:  # Sinaloa: desert hills, cactus, drone in the sky
        draw.rectangle([x, y, x + w, y + h], fill=(232, 200, 138))
        draw.polygon([(x, y + h * 0.62), (x + 70, y + h * 0.28),
                      (x + 150, y + h * 0.62)], fill=(168, 122, 74))
        draw.polygon([(x + 90, y + h * 0.62), (x + 150, y + h * 0.34),
                      (x + w, y + h * 0.62)], fill=(150, 106, 62))
        draw.rectangle([x, y + h * 0.62, x + w, y + h], fill=(196, 150, 96))
        draw.rectangle([x + 22, y + h * 0.5, x + 30, y + h * 0.78],
                       fill=(42, 122, 62))
        draw.rectangle([x + 12, y + h * 0.58, x + 22, y + h * 0.64],
                       fill=(42, 122, 62))
        draw.rectangle([x + 30, y + h * 0.62, x + 40, y + h * 0.68],
                       fill=(42, 122, 62))
        draw.ellipse([x + w - 62, y + 10, x + w - 44, y + 18], fill=(25, 25, 25))
        draw.line([x + w - 68, y + 8, x + w - 38, y + 8], fill=(90, 90, 90), width=1)
    elif n == 10:  # Tehran: night, pylon, moon, lit windows
        draw.rectangle([x, y, x + w, y + h], fill=(20, 20, 42))
        draw.ellipse([x + w - 44, y + 6, x + w - 20, y + 30], fill=(240, 230, 190))
        rng = random.Random(1010)
        bx = x + 6
        for bw, bh in [(36, 26), (30, 38), (34, 24), (30, 32)]:
            draw.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(12, 12, 24))
            for wy in range(y + h - bh + 5, y + h - 4, 9):
                if rng.random() < 0.5:
                    draw.rectangle([bx + 6, wy, bx + 10, wy + 4],
                                   fill=(255, 210, 90))
            bx += bw + 6
        # transmission pylon
        px = x + w // 2
        draw.line([px, y + 8, px - 16, y + h], fill=(200, 200, 200), width=2)
        draw.line([px, y + 8, px + 16, y + h], fill=(200, 200, 200), width=2)
        draw.line([px - 20, y + 22, px + 20, y + 22], fill=(200, 200, 200), width=2)
        draw.line([px - 12, y + 40, px + 12, y + 40], fill=(200, 200, 200), width=2)
    elif n == 11:  # Washington: green chip, magnifier, falling red chart
        draw.rectangle([x, y, x + w, y + h], fill=(232, 240, 232))
        draw.rectangle([x + 16, y + 14, x + 58, y + 50], fill=(16, 90, 60))
        draw.rectangle([x + 26, y + 24, x + 48, y + 40], fill=(8, 60, 40))
        for py in (y + 20, y + 28, y + 36, y + 44):
            draw.line([x + 8, py, x + 16, py], fill=(200, 170, 60), width=2)
            draw.line([x + 58, py, x + 66, py], fill=(200, 170, 60), width=2)
        pts = [(x + 74, y + 18), (x + 104, y + 30), (x + 128, y + 22),
               (x + 156, y + 40), (x + w - 12, y + 48)]
        draw.line(pts, fill=(200, 40, 40), width=3)
        cx, cy, cr = x + 108, y + 30, 15
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=None,
                     outline=(30, 30, 30), width=3)
        draw.line([cx + 10, cy + 10, cx + 22, cy + 22], fill=(30, 30, 30), width=3)
    elif n == 12:  # Brasilia: hospital bed + monitor with ECG trace
        draw.rectangle([x, y, x + w, y + h], fill=(240, 232, 224))
        draw.rectangle([x + 14, y + h * 0.5, x + 110, y + h * 0.62],
                       fill=WHITE, outline=(150, 150, 150))
        draw.rectangle([x + 14, y + h * 0.5, x + 62, y + h * 0.62],
                       fill=(140, 190, 230))
        draw.ellipse([x + 16, y + h * 0.44, x + 34, y + h * 0.54],
                     fill=(232, 190, 150))
        draw.line([x + 20, y + h * 0.62, x + 20, y + h * 0.86], fill=(90, 90, 90),
                  width=2)
        draw.line([x + 104, y + h * 0.62, x + 104, y + h * 0.86], fill=(90, 90, 90),
                  width=2)
        draw.rectangle([x + 126, y + 8, x + w - 12, y + 34], fill=(20, 30, 40))
        pts = [(x + 130, y + 24), (x + 142, y + 24), (x + 148, y + 14),
               (x + 154, y + 30), (x + 160, y + 20), (x + 172, y + 24)]
        draw.line(pts, fill=(60, 220, 100), width=2)
        draw.line([x + 150, y + 34, x + 150, y + h * 0.5], fill=(90, 90, 90),
                  width=2)
    elif n == 13:  # Tallinn: pine forest, fence, red-white barrier
        draw.rectangle([x, y, x + w, y + h], fill=(168, 200, 230))
        draw.rectangle([x, y + h * 0.66, x + w, y + h], fill=(110, 160, 90))
        for tx in (x + 14, x + 58, x + 104, x + 148):
            draw.polygon([(tx, y + h * 0.66), (tx + 16, y + h * 0.2),
                          (tx + 32, y + h * 0.66)], fill=(30, 90, 50))
            draw.rectangle([tx + 13, y + h * 0.64, tx + 19, y + h * 0.72],
                           fill=(90, 60, 30))
        draw.rectangle([x + 6, y + h * 0.6, x + w - 6, y + h * 0.66],
                       fill=(120, 84, 50))
        for fx in (x + 20, x + 70, x + 120, x + 170):
            draw.rectangle([fx, y + h * 0.52, fx + 5, y + h * 0.72],
                           fill=(90, 60, 30))
        draw.rectangle([x + 66, y + h * 0.74, x + 126, y + h * 0.8],
                       fill=(220, 220, 220))
        draw.rectangle([x + 66, y + h * 0.74, x + 86, y + h * 0.8],
                       fill=(200, 40, 40))
        draw.rectangle([x + 106, y + h * 0.74, x + 126, y + h * 0.8],
                       fill=(200, 40, 40))


# ---------------------------------------------------------------- map

LAND_BLOBS = [  # (cx, cy, rx, ry) in fractions of the map area
    (0.16, 0.28, 0.13, 0.15), (0.27, 0.46, 0.04, 0.06),
    (0.30, 0.68, 0.07, 0.15), (0.50, 0.22, 0.05, 0.08),
    (0.53, 0.50, 0.07, 0.13), (0.68, 0.25, 0.20, 0.13),
    (0.80, 0.48, 0.05, 0.06), (0.86, 0.70, 0.07, 0.06),
]

# (lon, lat) of stories 1-13, plus a fan-out offset (dx, dy) in px
PIN_POS = [
    (30.7, 36.9, 0, 0), (30.5, 50.5, -14, -8), (50.6, 26.2, 8, 8),
    (24.0, 60.0, -16, 6), (33.4, 47.9, 10, -10), (6.3, 4.8, 0, 0),
    (35.2, 31.8, 14, 4), (34.5, 31.5, 16, 12), (-107.0, 25.0, 0, 0),
    (51.4, 35.7, 18, -6), (-77.0, 38.9, 0, 0), (-47.9, -15.8, 0, 0),
    (24.7, 59.4, -8, -12),
]


def draw_map(draw, x, y, w, h):
    """A2: dotted continents on a pale-blue sea, red numbered pins."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    step = 5
    for gy in range(y + 3, y + h - 2, step):
        for gx in range(x + 3, x + w - 2, step):
            fx = (gx - x) / w
            fy = (gy - y) / h
            inside = False
            for (cx, cy, rx, ry) in LAND_BLOBS:
                if ((fx - cx) / rx) ** 2 + ((fy - cy) / ry) ** 2 <= 1:
                    inside = True
                    break
            if inside:
                draw.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=LAND)
    fnt = font(SANS_B, 8)
    for i, (lon, lat, dx, dy) in enumerate(PIN_POS, start=1):
        px = x + (lon + 170) / 360 * w + dx
        py = y + (75 - lat) / 130 * h + dy
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                     outline=WHITE, width=1)
        label = str(i)
        tw = text_w(draw, label, fnt)
        draw.text((px - tw / 2, py - 6), label, font=fnt, fill=WHITE)


# ---------------------------------------------------------------- page

def render(data):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # masthead
    f_mast = font(SANS_B, 13)
    d.text((MARGIN, 10), data["masthead_left"], font=f_mast, fill=NAVY)
    f_mast_r = font(SANS_B, 12)
    right = data["masthead_right"]
    d.text((W - MARGIN - text_w(d, right, f_mast_r), 11), right, font=f_mast_r,
           fill=NAVY)

    # title
    f_title = font(SERIF_B, 60)
    d.text((MARGIN, 28), data["title"], font=f_title, fill=INK)

    # kicker
    f_kick = font(SERIF_IT, 17)
    kw = text_w(d, data["kicker"], f_kick)
    d.text(((W - kw) / 2, 106), data["kicker"], font=f_kick, fill=RED)

    # thin rule
    d.line([MARGIN, 130, W - MARGIN, 130], fill=GRAY_LT, width=1)

    # stat strip: 6 columns
    f_stat_n = font(SERIF_B, 28)
    f_stat_l = font(SANS, 10)
    col_w = CW / 6
    for i, (num, label) in enumerate(data["stats"]):
        cx = MARGIN + i * col_w
        d.text((cx + 4, 136), num, font=f_stat_n, fill=RED)
        for j, line in enumerate(wrap(d, label, f_stat_l, col_w - 10)):
            d.text((cx + 4, 168 + j * 12), line, font=f_stat_l, fill=INK)
        if i:
            d.line([cx, 138, cx, 176], fill=GRAY_LT, width=1)

    # region bar (widths proportional to counts, AFRICA floored so its
    # label fits)
    f_reg = font(SANS_B, 10)
    f_reg_s = font(SANS_B, 9)
    reg_cols = [(46, 74, 122), (168, 31, 31), (46, 122, 74),
                (184, 134, 11), (107, 74, 42), (106, 74, 138)]
    counts = [c for _, c in data["regions"]]
    total = sum(counts)
    widths = [max(int(c / total * CW), 56) for c in counts]
    widths[0] -= sum(widths) - CW
    rx = MARGIN
    for (name, cnt), wd, col in zip(data["regions"], widths, reg_cols):
        d.rectangle([rx, 186, rx + wd, 206], fill=col)
        label = "%s %d" % (name, cnt)
        fnt = f_reg_s if wd < 70 else f_reg
        tw = text_w(d, label, fnt)
        d.text((rx + (wd - tw) / 2, 191), label, font=fnt, fill=WHITE)
        rx += wd

    # heroes
    hero_w, hero_gap = 320, 12
    hero_y, tag_h, art_h = 216, 22, 98
    f_tag = font(SANS_B, 13)
    f_loc = font(SANS_B, 11)
    f_head = font(SERIF_B, 19)
    f_deck = font(SANS, 11)
    hero_art = {1: art_hero_cop31, 2: art_hero_ukraine, 3: art_hero_bahrain}
    for i, hero in enumerate(data["heroes"]):
        hx = MARGIN + i * (hero_w + hero_gap)
        d.rectangle([hx, hero_y, hx + hero_w, hero_y + tag_h], fill=RED)
        d.text((hx + 8, hero_y + 3), hero["tag"], font=f_tag, fill=WHITE)
        ay = hero_y + tag_h
        hero_art[hero["n"]](d, hx, ay, hero_w, art_h)
        # chips on the art: white top-right, black bottom-left
        f_chip = font(SANS_B, 10)
        chip(d, hx + hero_w - text_w(d, hero["chip_top"], f_chip) - 14,
             ay + 6, hero["chip_top"], f_chip, INK, WHITE)
        chip(d, hx + 6, ay + art_h - 20, hero["chip_bottom"], f_chip, WHITE,
             BLACK)
        # A1: TOP STORY label under the tag bar on hero 1
        if hero.get("top_story"):
            chip(d, hx + 6, ay + 4, "TOP STORY", f_chip, WHITE, BLACK)
        ty = ay + art_h + 6
        d.text((hx, ty), "%d %s" % (hero["n"], hero["loc"]), font=f_loc, fill=RED)
        lines = wrap(d, hero["headline"], f_head, hero_w)
        for j, line in enumerate(lines[:2]):
            d.text((hx, ty + 16 + j * 22), line, font=f_head, fill=INK)
        dlines = wrap(d, hero["deck"], f_deck, hero_w)
        for j, line in enumerate(dlines[:3]):
            d.text((hx, ty + 62 + j * 14), line, font=f_deck, fill=(74, 70, 60))

    # small cards, two rows of five
    card_w, card_gap = 192, 6
    f_ctag = font(SANS_B, 12)
    f_cloc = font(SANS_B, 10)
    f_chead = font(SERIF_B, 15)
    f_cdeck = font(SANS, 11)
    f_cap = font(SANS_B, 9)
    for row in range(2):
        tag_y = 456 + row * 172
        art_y = tag_y + 21
        art_h2 = 56
        for col in range(5):
            card = data["cards"][row * 5 + col]
            cx = MARGIN + col * (card_w + card_gap)
            d.rectangle([cx, tag_y, cx + card_w, tag_y + 21], fill=RED)
            d.text((cx + 7, tag_y + 3), card["tag"], font=f_ctag, fill=WHITE)
            art_card(d, card["n"], cx, art_y, card_w, art_h2)
            number_circle(d, cx + card_w - 13, art_y + 12, card["n"])
            # B4 caption chip, bottom-left of the art
            chip(d, cx + 4, art_y + art_h2 - 17, card["caption"], f_cap,
                 WHITE, BLACK)
            ty = art_y + art_h2 + 6
            d.text((cx, ty), card["loc"], font=f_cloc, fill=RED)
            lines = wrap(d, card["headline"], f_chead, card_w)
            for j, line in enumerate(lines[:2]):
                d.text((cx, ty + 15 + j * 18), line, font=f_chead, fill=INK)
            dlines = wrap(d, card["deck"], f_cdeck, card_w)
            for j, line in enumerate(dlines[:2]):
                d.text((cx, ty + 52 + j * 13), line, font=f_cdeck,
                       fill=(74, 70, 60))

    # map + ALSO list
    f_sect = font(SANS_B, 12)
    f_sect_s = font(SANS, 10)
    d.text((MARGIN, 800), "WHERE IT HAPPENED", font=f_sect, fill=INK)
    d.text((MARGIN + text_w(d, "WHERE IT HAPPENED", f_sect) + 8, 802),
           "pins match story numbers", font=f_sect_s, fill=GRAY)
    draw_map(d, MARGIN, 818, 330, 106)
    ax = 368
    d.text((ax, 800), "ALSO ON SUNDAY 22 NOVEMBER — 22 MORE STORIES",
           font=font(SANS_B, 13), fill=INK)
    f_also = font(SANS, 10)
    f_also_n = font(SANS_B, 10)
    for k, item in enumerate(data["also"]):
        col = 0 if k < 11 else 1
        row_i = k if k < 11 else k - 11
        ix = ax + col * 322
        iy = 818 + row_i * 9.6
        num, _, rest = item.partition(":")
        d.text((ix, iy), num, font=f_also_n, fill=RED)
        d.text((ix + text_w(d, num + " ", f_also_n), iy), ": " + rest,
               font=f_also, fill=INK)

    # DATE CHECK box (A5: adds the "Not yet happened" sentence)
    f_dc_t = font(SANS_B, 13)
    f_dc = font(SERIF, 12)
    dc_y = 928
    dc_lines = wrap(d, data["datecheck"], f_dc, CW - 132)
    dc_h = len(dc_lines) * 14 + 10
    d.rectangle([MARGIN, dc_y, W - MARGIN, dc_y + dc_h], outline=RED, width=2)
    d.text((MARGIN + 8, dc_y + 7), "DATE CHECK", font=f_dc_t, fill=RED)
    for j, line in enumerate(dc_lines):
        d.text((MARGIN + 132, dc_y + 6 + j * 14), line, font=f_dc, fill=INK)

    # sources + footer
    f_src = font(SANS, 9)
    sy = dc_y + dc_h + 6
    d.text((MARGIN, sy), data["sources_line"], font=f_src, fill=GRAY)
    f_foot = font(SANS_B, 11)
    d.text((MARGIN, sy + 12), data["footer_left"], font=f_foot, fill=INK)
    fr = data["footer_right"]
    d.text((W - MARGIN - text_w(d, fr, f_foot), sy + 12), fr, font=f_foot,
           fill=INK)

    return img


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    img = render(data)
    out = os.path.join(HERE, "entry.png")
    img.save(out)
    print("wrote %s %d bytes" % (out, os.path.getsize(out)))


if __name__ == "__main__":
    main()
