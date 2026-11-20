# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/tamadung/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/tamadung/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image summing up the world news of Thursday 19 November 2026: a newspaper-style front page on the winning template — masthead naming the day, region bar (7 regions) and numbers strip, 14 core stories each with its own flat-illustration panel and a verification tag (REPORTED / CLAIM / FORECAST), a large PIL-drawn world map with 14 numbered pins tied to the core stories plus gold dots for the rest, a 28-item "Also on Thursday 19 November" list, and a date-check box naming the stories deliberately left out because they were first reported on 18 November or belong to 20 November. 42 stories in all, across every region and field.

Core stories: Trump–Xi–Putin trilateral summit in Shenzhen, GTA VI global launch, ICJ genocide verdict on Myanmar, Anthropic's record $81.3bn IPO, Crimea Bridge hit a third time, COP31 draft, Cyclone Akvan, Houthi missiles over Riyadh, Israeli armour in Gaza, Korea's Suneung exam, Colombia's national strike, Australia's 4.9% jobless rate, Denmark's Arctic pact, Somalia expelling the UAE ambassador.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024×1024, PNG, 549,662 bytes). Two runs write identical bytes.

`compose.py` is the build script that drew the page (PIL + 14 flat illustrations in the work dir — 10 generated fresh for this round, 4 reused from the 18 Nov v3 build); `main.py` only carries the finished image to the output directory.

---

<sub>Entered on [make.fun](https://make.fun/?ref=tidy-ibis-74&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
