#!/usr/bin/env python3
"""Render the 22 November 2026 front page (1024x1024) from stories.json.

Build-time only: uses PIL. The graded entrypoint (main.py) is stdlib-only
and just copies the rendered entry.png. If hero.jpg sits beside this
script it is used as the hero photo (top-biased crop so faces are kept);
otherwise a procedural plenary illustration is drawn instead.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
MUTED = (90, 86, 76)
RULE = (120, 114, 100)
CARD_BG = (255, 253, 246)
RED = (178, 34, 34)
NAVY = (18, 38, 66)
SKY = (146, 190, 220)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
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


def draw_flag(d, x, y, w, h, top, bottom):
    d.rectangle([x, y, x + w, y + h // 2], fill=top)
    d.rectangle([x, y + h // 2, x + w, y + h], fill=bottom)
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def art(d, key, x, y, s):
    """Draw a small flat illustration of size s at (x, y)."""
    if key == "quake":
        d.polygon([(x, y + s), (x + s * 0.28, y + s * 0.30), (x + s * 0.55, y + s)],
                  fill=(96, 110, 96))
        d.polygon([(x + s * 0.45, y + s), (x + s * 0.72, y + s * 0.18),
                   (x + s, y + s)], fill=(70, 84, 78))
        d.polygon([(x, y + s * 0.82), (x + s * 0.3, y + s * 0.62),
                   (x + s * 0.5, y + s * 0.86), (x + s * 0.7, y + s * 0.66),
                   (x + s, y + s * 0.84), (x + s, y + s), (x, y + s)],
                  fill=(120, 96, 66))
        d.rectangle([x + s * 0.12, y + s * 0.55, x + s * 0.30, y + s * 0.72],
                    fill=(178, 120, 70))
        d.polygon([(x + s * 0.10, y + s * 0.55), (x + s * 0.21, y + s * 0.44),
                   (x + s * 0.32, y + s * 0.55)], fill=(140, 60, 50))
    elif key == "capture":
        d.rectangle([x, y, x + s, y + s], fill=(30, 42, 58))
        d.ellipse([x + s * 0.22, y + s * 0.42, x + s * 0.62, y + s * 0.62],
                  fill=(200, 200, 200))
        d.rectangle([x + s * 0.60, y + s * 0.48, x + s * 0.86, y + s * 0.54],
                    fill=(200, 200, 200))
        d.rectangle([x + s * 0.12, y + s * 0.34, x + s * 0.82, y + s * 0.38],
                    fill=(230, 230, 230))
        d.rectangle([x + s * 0.40, y + s * 0.38, x + s * 0.44, y + s * 0.44],
                    fill=(180, 180, 180))
        d.polygon([(x + s * 0.30, y + s * 0.62), (x + s * 0.36, y + s * 0.86),
                   (x + s * 0.44, y + s * 0.62)], fill=(255, 220, 120))
        d.polygon([(x + s * 0.55, y + s * 0.62), (x + s * 0.62, y + s * 0.86),
                   (x + s * 0.70, y + s * 0.62)], fill=(255, 220, 120))
    elif key == "barrage":
        d.rectangle([x, y, x + s, y + s], fill=(16, 22, 40))
        for bx in (0.08, 0.30, 0.55, 0.78):
            bh = s * (0.28 + 0.18 * ((bx * 7) % 1))
            d.rectangle([x + s * bx, y + s - bh, x + s * (bx + 0.16), y + s],
                        fill=(52, 60, 84))
            for wy in (0.25, 0.5, 0.75):
                d.rectangle([x + s * (bx + 0.05), y + s - bh + bh * wy,
                             x + s * (bx + 0.11), y + s - bh + bh * wy + 3],
                            fill=(255, 210, 90))
        for dx, dy in ((0.2, 0.2), (0.45, 0.12), (0.7, 0.25), (0.85, 0.12)):
            d.ellipse([x + s * dx - 2, y + s * dy - 2, x + s * dx + 2,
                       y + s * dy + 2], fill=(255, 220, 120))
            d.line([x + s * dx, y + s * dy, x + s * (dx + 0.12),
                    y + s * (dy + 0.10)], fill=(255, 180, 80), width=2)
        d.ellipse([x + s * 0.62, y + s * 0.55, x + s * 0.78, y + s * 0.71],
                  fill=(255, 140, 40))
        d.ellipse([x + s * 0.66, y + s * 0.59, x + s * 0.74, y + s * 0.67],
                  fill=(255, 220, 90))
    elif key == "carrier":
        d.rectangle([x, y, x + s, y + s * 0.62], fill=(140, 185, 215))
        d.rectangle([x, y + s * 0.62, x + s, y + s], fill=(28, 68, 110))
        d.rectangle([x + s * 0.08, y + s * 0.66, x + s * 0.92, y + s * 0.74],
                    fill=(70, 74, 80))
        d.rectangle([x + s * 0.62, y + s * 0.52, x + s * 0.74, y + s * 0.66],
                    fill=(90, 94, 100))
        d.polygon([(x + s * 0.20, y + s * 0.60), (x + s * 0.34, y + s * 0.52),
                   (x + s * 0.44, y + s * 0.60)], fill=(200, 205, 210))
        d.polygon([(x + s * 0.44, y + s * 0.58), (x + s * 0.52, y + s * 0.50),
                   (x + s * 0.58, y + s * 0.58)], fill=(180, 185, 190))
        for wx in range(6):
            d.arc([x + s * (0.06 + wx * 0.15), y + s * 0.10,
                   x + s * (0.16 + wx * 0.15), y + s * 0.22],
                  180, 360, fill=(255, 255, 255), width=2)
    elif key == "scales":
        d.rectangle([x, y, x + s, y + s], fill=(235, 228, 210))
        d.ellipse([x + s * 0.38, y + s * 0.78, x + s * 0.62, y + s * 0.86],
                  fill=(150, 120, 60))
        d.rectangle([x + s * 0.48, y + s * 0.22, x + s * 0.52, y + s * 0.80],
                    fill=(150, 120, 60))
        d.rectangle([x + s * 0.16, y + s * 0.24, x + s * 0.84, y + s * 0.28],
                    fill=(150, 120, 60))
        for cx in (0.22, 0.78):
            d.line([x + s * cx, y + s * 0.26, x + s * (cx - 0.10),
                    y + s * 0.52], fill=(120, 95, 45), width=2)
            d.line([x + s * cx, y + s * 0.26, x + s * (cx + 0.10),
                    y + s * 0.52], fill=(120, 95, 45), width=2)
            d.pieslice([x + s * (cx - 0.11), y + s * 0.50,
                        x + s * (cx + 0.11), y + s * 0.68], 0, 180,
                       fill=(190, 160, 90))
        d.ellipse([x + s * 0.44, y + s * 0.14, x + s * 0.56, y + s * 0.26],
                  fill=(190, 160, 90))
    elif key == "ipo":
        d.rectangle([x, y, x + s, y + s], fill=(232, 240, 235))
        bars = [(0.12, 0.30), (0.30, 0.45), (0.48, 0.38), (0.66, 0.62),
                (0.84, 0.80)]
        for bx, bh in bars:
            d.rectangle([x + s * bx, y + s * (0.92 - bh),
                         x + s * (bx + 0.12), y + s * 0.92],
                        fill=(30, 110, 70))
        d.line([x + s * 0.10, y + s * 0.68, x + s * 0.32, y + s * 0.50,
                x + s * 0.52, y + s * 0.56, x + s * 0.72, y + s * 0.32,
                x + s * 0.90, y + s * 0.14], fill=(178, 34, 34), width=3)
        d.polygon([(x + s * 0.90, y + s * 0.14), (x + s * 0.80, y + s * 0.14),
                   (x + s * 0.90, y + s * 0.24)], fill=(178, 34, 34))
        d.line([x + s * 0.06, y + s * 0.92, x + s, y + s * 0.92],
               fill=INK, width=2)
    elif key == "trade":
        d.rectangle([x, y, x + s, y + s], fill=(238, 236, 228))
        d.rectangle([x + s * 0.08, y + s * 0.18, x + s * 0.44, y + s * 0.60],
                    fill=(20, 50, 130))
        for k in range(12):
            import math
            a = math.pi * 2 * k / 12
            cx = x + s * 0.26 + 0.09 * s * math.cos(a)
            cy = y + s * 0.39 + 0.09 * s * math.sin(a)
            d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 210, 60))
        d.rectangle([x + s * 0.56, y + s * 0.18, x + s * 0.92, y + s * 0.39],
                    fill=(205, 40, 40))
        d.rectangle([x + s * 0.56, y + s * 0.39, x + s * 0.92, y + s * 0.60],
                    fill=(245, 245, 245))
        d.line([x + s * 0.10, y + s * 0.78, x + s * 0.90, y + s * 0.78],
               fill=INK, width=2)
        d.line([x + s * 0.30, y + s * 0.78, x + s * 0.50, y + s * 0.66],
               fill=INK, width=2)
        d.line([x + s * 0.70, y + s * 0.78, x + s * 0.50, y + s * 0.66],
               fill=INK, width=2)
    elif key == "sudan":
        d.rectangle([x, y, x + s, y + s], fill=(232, 206, 150))
        d.polygon([(x, y + s * 0.55), (x + s * 0.35, y + s * 0.40),
                   (x + s * 0.7, y + s * 0.62), (x + s, y + s * 0.50),
                   (x + s, y + s), (x, y + s)], fill=(210, 175, 110))
        d.line([x + s * 0.10, y + s * 0.85, x + s * 0.90, y + s * 0.30],
               fill=(140, 100, 60), width=3)
        d.ellipse([x + s * 0.68, y + s * 0.10, x + s * 0.88, y + s * 0.30],
                  fill=(255, 200, 90))
        d.ellipse([x + s * 0.38, y + s * 0.30, x + s * 0.62, y + s * 0.54],
                  fill=(178, 34, 34))
        d.ellipse([x + s * 0.46, y + s * 0.38, x + s * 0.54, y + s * 0.46],
                  fill=(255, 255, 255))
    elif key == "boat":
        d.rectangle([x, y, x + s, y + s * 0.60], fill=(150, 195, 225))
        d.rectangle([x, y + s * 0.60, x + s, y + s], fill=(30, 90, 140))
        for wx in range(4):
            d.arc([x + s * (wx * 0.25), y + s * 0.62,
                   x + s * (wx * 0.25 + 0.28), y + s * 0.82], 0, 180,
                  fill=(255, 255, 255), width=3)
        d.polygon([(x + s * 0.18, y + s * 0.58), (x + s * 0.82, y + s * 0.58),
                   (x + s * 0.70, y + s * 0.74), (x + s * 0.30, y + s * 0.74)],
                  fill=(120, 70, 40))
        d.rectangle([x + s * 0.30, y + s * 0.42, x + s * 0.70, y + s * 0.58],
                    fill=(240, 230, 200))
        for px in (0.36, 0.48, 0.60):
            d.ellipse([x + s * px, y + s * 0.34, x + s * (px + 0.06),
                       y + s * 0.42], fill=(40, 40, 40))
    elif key == "football":
        d.rectangle([x, y, x + s, y + s], fill=(46, 130, 70))
        d.rectangle([x + s * 0.08, y + s * 0.08, x + s * 0.92, y + s * 0.92],
                    outline=(255, 255, 255), width=2)
        d.line([x + s * 0.50, y + s * 0.08, x + s * 0.50, y + s * 0.92],
               fill=(255, 255, 255), width=2)
        d.ellipse([x + s * 0.38, y + s * 0.38, x + s * 0.62, y + s * 0.62],
                  outline=(255, 255, 255), width=2)
        d.ellipse([x + s * 0.66, y + s * 0.60, x + s * 0.86, y + s * 0.80],
                  fill=(255, 255, 255))
        d.polygon([(x + s * 0.76, y + s * 0.64), (x + s * 0.82, y + s * 0.68),
                   (x + s * 0.78, y + s * 0.74), (x + s * 0.72, y + s * 0.72),
                   (x + s * 0.71, y + s * 0.66)], fill=INK)
    elif key == "f1":
        d.rectangle([x, y, x + s, y + s], fill=(24, 28, 38))
        d.polygon([(x + s * 0.10, y + s * 0.55), (x + s * 0.30, y + s * 0.42),
                   (x + s * 0.62, y + s * 0.40), (x + s * 0.86, y + s * 0.52),
                   (x + s * 0.88, y + s * 0.60), (x + s * 0.10, y + s * 0.62)],
                  fill=(200, 30, 30))
        d.rectangle([x + s * 0.55, y + s * 0.30, x + s * 0.68, y + s * 0.42],
                    fill=(200, 30, 30))
        for wx in (0.24, 0.72):
            d.ellipse([x + s * (wx - 0.09), y + s * 0.56,
                       x + s * (wx + 0.09), y + s * 0.74], fill=(15, 15, 15))
            d.ellipse([x + s * (wx - 0.04), y + s * 0.61,
                       x + s * (wx + 0.04), y + s * 0.69], fill=(180, 180, 180))
        for i in range(4):
            for j in range(2):
                c = (255, 255, 255) if (i + j) % 2 == 0 else INK
                d.rectangle([x + s * (0.08 + i * 0.09), y + s * (0.10 + j * 0.09),
                             x + s * (0.17 + i * 0.09), y + s * (0.19 + j * 0.09)],
                            fill=c)
        d.line([x + s * 0.44, y + s * 0.10, x + s * 0.44, y + s * 0.28],
               fill=(200, 200, 200), width=2)
    elif key == "un":
        d.rectangle([x, y, x + s, y + s], fill=(120, 170, 210))
        d.rectangle([x + s * 0.30, y + s * 0.22, x + s * 0.70, y + s * 0.88],
                    fill=(235, 235, 235))
        for r in range(6):
            for c in range(4):
                d.rectangle([x + s * (0.34 + c * 0.09), y + s * (0.28 + r * 0.09),
                             x + s * (0.40 + c * 0.09), y + s * (0.33 + r * 0.09)],
                            fill=(90, 130, 170))
        d.rectangle([x + s * 0.08, y + s * 0.70, x + s * 0.26, y + s * 0.88],
                    fill=(200, 200, 200))
        d.ellipse([x + s * 0.44, y + s * 0.08, x + s * 0.56, y + s * 0.20],
                  fill=(20, 60, 140))
    elif key == "greenland":
        d.rectangle([x, y, x + s, y + s * 0.55], fill=(160, 200, 225))
        d.rectangle([x, y + s * 0.55, x + s, y + s], fill=(40, 90, 140))
        d.polygon([(x + s * 0.05, y + s * 0.80), (x + s * 0.30, y + s * 0.30),
                   (x + s * 0.55, y + s * 0.80)], fill=(235, 245, 250))
        d.polygon([(x + s * 0.45, y + s * 0.80), (x + s * 0.68, y + s * 0.42),
                   (x + s * 0.95, y + s * 0.80)], fill=(215, 230, 240))
        d.rectangle([x + s * 0.62, y + s * 0.12, x + s * 0.90, y + s * 0.34],
                    fill=(255, 255, 255))
        d.rectangle([x + s * 0.62, y + s * 0.12, x + s * 0.90, y + s * 0.23],
                    fill=(205, 40, 40))
        d.ellipse([x + s * 0.70, y + s * 0.16, x + s * 0.82, y + s * 0.30],
                  fill=(205, 40, 40))
        d.ellipse([x + s * 0.70, y + s * 0.16, x + s * 0.82, y + s * 0.23],
                  fill=(255, 255, 255))
def draw_plenary_hero(d, x, y, w, h):
    """Wide dawn-plenary illustration for the hero band (no photo yet)."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 44, 78))
    # dawn windows with mullions
    for i in range(6):
        wx0 = x + w * (0.03 + i * 0.165)
        d.rectangle([wx0, y + h * 0.08, wx0 + w * 0.13, y + h * 0.40],
                    fill=(255, 205, 120))
        d.line([wx0 + w * 0.065, y + h * 0.08, wx0 + w * 0.065,
                y + h * 0.40], fill=(24, 44, 78), width=3)
        d.line([wx0, y + h * 0.24, wx0 + w * 0.13, y + h * 0.24],
               fill=(24, 44, 78), width=3)
    # big screen with a proper globe
    d.rectangle([x + w * 0.38, y + h * 0.12, x + w * 0.62, y + h * 0.42],
                fill=(240, 240, 235))
    cx, cy = x + w * 0.50, y + h * 0.27
    r = h * 0.13
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 130, 90))
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
              outline=(240, 240, 235), width=2)
    d.line([cx - r, cy, cx + r, cy], fill=(240, 240, 235), width=2)
    d.line([cx, cy - r, cx, cy + r], fill=(240, 240, 235), width=2)
    # rows of desks with delegates (heads above continuous desks)
    for r_i in range(3):
        dy = y + h * (0.56 + r_i * 0.15)
        d.rectangle([x + w * 0.03, dy, x + w * 0.97, dy + h * 0.075],
                    fill=(198, 176, 132))
        for c in range(12):
            hx = x + w * (0.05 + c * 0.08)
            d.ellipse([hx, dy - h * 0.085, hx + w * 0.028,
                       dy - h * 0.015], fill=(232, 202, 162))
            d.rectangle([hx - w * 0.004, dy - h * 0.02,
                         hx + w * 0.032, dy], fill=(120, 90, 60))


def hero_image(hero_path, w, h):
    """Load hero.jpg with a top-biased cover crop, or None."""
    if not hero_path or not os.path.exists(hero_path):
        return None
    im = Image.open(hero_path).convert("RGB")
    sw, sh = im.size
    scale = max(w / sw, h / sh)
    im = im.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    top = max(0, int((im.height - h) * 0.12))  # keep the top of the frame
    return im.crop((0, top, w, top + h))


def render():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    ed = data["edition"]
    stories = data["stories"]
    hero = next(s for s in stories if s["kind"] == "hero")
    cards = [s for s in stories if s["kind"] == "card"]
    briefs = [s for s in stories if s["kind"] == "brief"]

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 4], fill=INK)
    f_title = font(SERIF, 66)
    tw = d.textlength(ed["title"], font=f_title)
    d.text(((W - tw) / 2, 10), ed["title"], font=f_title, fill=INK)
    d.line([16, 92, W - 16, 92], fill=RULE, width=2)
    f_date = font(SANS_B, 17)
    dateline = "SUNDAY, 22 NOVEMBER 2026"
    dw = d.textlength(dateline, font=f_date)
    d.text(((W - dw) / 2, 98), dateline, font=f_date, fill=INK)
    f_sub = font(SANS, 14)
    sub = ed["subtitle"].upper() + "  ·  ALL STORIES DATED 22 NOV 2026"
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 120), sub, font=f_sub, fill=MUTED)
    d.line([16, 142, W - 16, 142], fill=INK, width=2)

    # ---- region strip ----
    strip_y, strip_h = 146, 26
    d.rectangle([0, strip_y, W, strip_y + strip_h], fill=INK)
    f_strip = font(SANS_B, 12)
    parts = [f"{r['name']} {r['count']}" for r in ed["regions"]]
    strip = "   ·   ".join(parts)
    sw = d.textlength(strip, font=f_strip)
    d.text(((W - sw) / 2, strip_y + 6), strip, font=f_strip, fill=(245, 242, 230))

    # ---- hero ----
    hx, hy, hw, hh = 0, 176, W, 220
    photo = hero_image(os.path.join(HERE, "hero.jpg"), hw, hh)
    if photo is not None:
        img.paste(photo, (hx, hy))
    else:
        draw_plenary_hero(d, hx, hy, hw, hh)
    # headline band over the hero's lower part
    band_h = 78
    band = Image.new("RGBA", (hw, band_h), (10, 10, 10, 215))
    img.paste(band, (hx, hy + hh - band_h), band)
    d = ImageDraw.Draw(img)
    f_h1 = font(SERIF, 34)
    d.text((18, hy + hh - band_h + 6), hero["title"], font=f_h1,
           fill=(255, 255, 255))
    f_hd = font(SANS, 13)
    deck_lines = fit_text(d, hero["deck"], f_hd, hw - 36, 1)
    d.text((18, hy + hh - 28), deck_lines[0], font=f_hd, fill=(225, 222, 210))
    f_tag2 = font(SANS_B, 12)
    tag_txt = "22 NOV 2026"
    tw_tag = d.textlength(tag_txt, font=f_tag2)
    d.rectangle([W - tw_tag - 24, hy + 8, W - 10, hy + 30], fill=(10, 10, 10))
    d.text((W - tw_tag - 17, hy + 11), tag_txt, font=f_tag2,
           fill=(255, 220, 120))

    # ---- 13 illustrated cards ----
    gx, gy = 14, 408
    cw, ch, gap = 242, 90, 6
    f_ct = font(SANS_B, 12)
    f_cd = font(SANS, 10)
    f_tag = font(SANS_B, 8)
    for i, s in enumerate(cards):
        cx = gx + (i % 4) * (cw + gap)
        cy = gy + (i // 4) * (ch + gap)
        d.rectangle([cx, cy, cx + cw, cy + ch], fill=CARD_BG,
                    outline=(150, 144, 130), width=1)
        art(d, s["art"], cx + 6, cy + 6, 58)
        tx = cx + 70
        tw2 = cw - 76
        title_lines = fit_text(d, s["title"], f_ct, tw2, 3)
        yy = cy + 6
        for ln in title_lines:
            d.text((tx, yy), ln, font=f_ct, fill=INK)
            yy += 14
        deck_lines = fit_text(d, s["deck"], f_cd, tw2, 2)
        for ln in deck_lines:
            d.text((tx, yy), ln, font=f_cd, fill=MUTED)
            yy += 12
        d.text((tx, cy + ch - 13), s["region"] + "  ·  22 NOV",
               font=f_tag, fill=RED)
    # fill the last row's empty slots with an edition index box
    ix = gx + 1 * (cw + gap)
    iy = gy + 3 * (ch + gap)
    iw = 3 * cw + 2 * gap
    d.rectangle([ix, iy, ix + iw, iy + ch], fill=(238, 232, 214),
                outline=(150, 144, 130), width=1)
    f_ix = font(SANS_B, 12)
    d.text((ix + 10, iy + 8), "INSIDE THIS EDITION", font=f_ix, fill=INK)
    f_ix2 = font(SANS, 11)
    idx = ("MIDDLE EAST 4  ·  EUROPE 8  ·  ASIA 4  ·  N. AMERICA 8  ·  "
           "LATIN AMERICA 5  ·  AFRICA 2  ·  OCEANIA 4")
    d.text((ix + 10, iy + 28), idx, font=f_ix2, fill=MUTED)
    d.text((ix + 10, iy + 48),
           "Every story below is dated 22 November 2026 — the day's news,",
           font=f_ix2, fill=MUTED)
    d.text((ix + 10, iy + 64),
           "from the COP31 deal in Antalya to the quake in Peru.",
           font=f_ix2, fill=MUTED)

    # ---- briefs ----
    by = gy + 4 * ch + 3 * gap + 12
    f_bh = font(SANS_B, 14)
    d.text((14, by), "THE DAY IN BRIEF", font=f_bh, fill=INK)
    d.line([14, by + 20, W - 14, by + 20], fill=INK, width=2)
    f_bt = font(SANS_B, 10)
    f_bd = font(SANS, 10)
    rows = 11
    rh = 16
    for i, s in enumerate(briefs):
        col = i // rows
        row = i % rows
        bx = 14 + col * 500
        bxx = bx + 496
        yy = by + 26 + row * rh
        bullet = "• "
        bw = d.textlength(bullet, font=f_bt)
        d.text((bx, yy), bullet, font=f_bt, fill=RED)
        avail = bxx - (bx + bw)
        line = s["title"] + " — " + s["deck"]
        # measure title then deck separately to keep the title bold
        tw_t = d.textlength(s["title"], font=f_bt)
        if tw_t + 8 <= avail:
            d.text((bx + bw, yy), s["title"], font=f_bt, fill=INK)
            rest = " — " + s["deck"]
            rw = d.textlength(rest, font=f_bd)
            if rw <= avail - tw_t:
                d.text((bx + bw + tw_t, yy), rest, font=f_bd, fill=MUTED)
            else:
                while rest and d.textlength(rest + "…", font=f_bd) > avail - tw_t:
                    rest = rest[:-1]
                d.text((bx + bw + tw_t, yy), rest.rstrip() + "…",
                       font=f_bd, fill=MUTED)
        else:
            title = s["title"]
            while title and d.textlength(title + "…", font=f_bt) > avail:
                title = title[:-1]
            d.text((bx + bw, yy), title.rstrip() + "…", font=f_bt, fill=INK)

    # ---- footer ----
    fy = by + 26 + rows * rh + 8
    d.line([14, fy, W - 14, fy], fill=RULE, width=1)
    f_ft = font(SANS, 9)
    foot = ("Sources: Reuters · AP · AFP · BBC · IAEA · ICJ · INDECI · European "
            "Commission · PassBlue · Flashscore · Formula 1")
    d.text((14, fy + 6), foot, font=f_ft, fill=MUTED)
    f_ft2 = font(SANS_B, 9)
    tag = "make.fun · news-image-20261122"
    tw = d.textlength(tag, font=f_ft2)
    d.text((W - 14 - tw, fy + 6), tag, font=f_ft2, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    render()
