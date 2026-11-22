#!/usr/bin/env python3
"""Entrypoint: copy the pre-rendered front page to the output directory.

Standard library only — no network, no third-party imports. The image is
rendered at build time by render_frontpage.py (PIL) from stories.json and
committed as entry.png; this program just places it where the grader
expects it, so both runs write byte-identical output.

Round 11 (this commit): the committed entry.png is the round 11
date-correction rebuild of round 10 (0.983206, rank 180) — hero 2 is
corrected from the 19–20 Nov 400-drone barrage to the 22 Nov
186-drone attack (161 downed, 18 sites hit), the DATE CHECK now
names the 400-drone barrage as excluded, hero 1 COP31 deck is more
specific (10-page final text, no fossil fuels, $120bn target
dropped, 35% electricity goal for 2035, 1.5°C overshoot admitted),
hero 3 Bahrain is reframed as a claim, the stat strip is all
22 Nov numbers (~200 | 03:00 | 186 | 161 | 856 | 2), and the
subtitle drops the false "every one dated Sunday" claim. No
renderer, art, map or region-bar change; the copy step is unchanged.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    if not os.path.isfile(src):
        print("entry.png missing from repository", file=sys.stderr)
        return 1
    with open(src, "rb") as fh:
        magic = fh.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dest)
    print("wrote", dest, os.path.getsize(dest), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
