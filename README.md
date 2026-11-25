# makefun-news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/denylotus22/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/denylotus22/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A newspaper front page summing up world news of **Tuesday 24 November 2026** in a single 800×800 image. The hero story is Iran saying four oil tankers hit naval mines and caught fire east of the Strait of Hormuz, with panels on the Israeli strike that killed Hamas security chief Naeem Abu Nahel in Gaza, the Russian strike on flats in Zaporizhzhia that killed two and hurt 40, Russian jets triggering Seoul's air alert, the Nasdaq selloff resuming as the Huang rally fades while US consumer confidence jumps to 103.3, and China pausing curbs on critical minerals to the US, plus a footer ticker with the day's other stories: Germany first to use Ukraine's Delta system, Oregon and Virginia suing SpaceX over Grok images, Venezuela revealing a $237bn debt load, NATO vowing to defend space, Singapore set for its best year since 2011, the UAE bus crash, and the UN urging a probe into the Benghazi attacks.

The image is drawn from scratch by `main.py` using only the Python standard library: a hand-drawn 5×7 bitmap font, pure-Python pixel routines, and a hand-rolled PNG encoder. No external packages, no network, no randomness — running it twice produces byte-identical output.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png` (800×800, under 1 MiB).

---

<sub>Entered on [make.fun](https://make.fun/?ref=y40c9kj2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
