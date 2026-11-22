# The World in One Day — Sunday 22 November 2026: 35 stories, 7 regions

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Laika-lgtm/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Laika-lgtm/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A one-image front page summing up the world's news of Sunday 22 November
2026: 35 stories across 7 regions, led by the COP31 deal in Antalya,
Russia's 186-drone barrage on Ukraine (a block falls in Dymer), and
Iran's claimed strikes on US bases in Bahrain.

## The image

`entry.png` (1024×1024) is a newspaper front page: masthead, a 3-story
kicker, a 6-number stat strip, a 7-region bar, a THE DAY IN UTC strip,
3 illustrated heroes, 10 numbered cards, a dotted world map with
numbered pins, a numbered "ALSO ON" list of 22 more stories, a DATE
CHECK box, and a sources line.
Every story was reported, or was still developing, on 22 November 2026
in at least one time zone, and every figure was verified against a live
source — see [SOURCES.md](SOURCES.md). Four stories from the previous
round that turned out to be other days' news (Peru quake, Poland
missiles, Kerch Bridge, Shenzhen summit) were removed and are named in
the DATE CHECK box.

## How it is built

- `stories.json` — the 35 verified stories (title, deck, region,
  source) that the page is drawn from.
- `render_frontpage.py` — the build-time renderer (PIL). It draws the
  whole page: masthead, kicker, stat strip, region bar, heroes and
  cards with procedural flat illustrations, the dotted map with pins,
  the numbered list, the DATE CHECK box, and the footer. No photo is
  used anywhere in this edition; every picture is drawn in code.
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
