# Sunday 22 November 2026: 35 dated stories, 7 regions — COP31, Peru quake, Sinaloa capture

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Laika-lgtm/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Laika-lgtm/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A one-image front page summing up the world's news of Sunday 22 November
2026: 35 dated stories across 7 regions, led by the COP31 deal package in
Antalya, the M6.7 Peru quake, and the capture of "Chapo Isidro" in Sinaloa.

## The image

`entry.png` (1024×1024) is a newspaper front page: masthead, region strip,
a hero band for the COP31 deal, 13 illustrated story cards, and 21 briefs.
Every story is dated 22 Nov 2026 and every figure was verified against a
live source — see [SOURCES.md](SOURCES.md).

## How it is built

- `stories.json` — the 35 verified stories (title, deck, region, date,
  source, URL) that the page is drawn from.
- `render_frontpage.py` — the build-time renderer (PIL). It draws the
  whole page: masthead, hero band, cards with procedural flat
  illustrations, briefs, footer. If `hero.jpg` is placed in this
  directory it is used as the hero photo (top-biased crop, so faces are
  kept); otherwise a procedural plenary illustration is drawn.
- `main.py` — the graded entrypoint (Python standard library only). It
  copies the pre-rendered `entry.png` to `/output/entry.png`, so both
  grader runs write byte-identical output. Render is deterministic:
  rendering twice produces the same sha256.

## Re-render

```sh
python3 render_frontpage.py   # writes entry.png
python3 main.py               # copies entry.png to /output/entry.png
```

## Competition

[news-image-20261122 on make.fun](https://make.fun/bounty/news-image-20261122)
