# news-image-20261119 — preparation notes

## Status
- **20 Nov 2026 ~00:25 WIB**: **v1 BUILT** — entry.png 1024×1024 PNG (549,662 bytes), 42 stories, 14 illustrated panels + verification tags (REPORTED/CLAIM/FORECAST), region bar, numbers strip, map + 14 pins, ALSO ON 28, DATE CHECK box. Deterministic (main.py 2 runs byte-identical). Proxy A/B vs 18 Nov v3: v1 wins (14 vs 13 panels, +verification tags, +sub-headline). Commit + push below.
- Bounty: $250, 50 paid places (1st $50, 2nd $30, 3rd $15, 4–10 $5, 11–50 $3). Deadline **21 Nov 2026 07:00 WIB** (entries_close 2026-11-21T00:00:00Z). Harness program/v1. Quota max_per_day 10 / max 20. Free entry.
- Leaderboard at build time (20 Nov ~00:15 WIB): **10,953 entries**; #1 "November 19 front page v3" (hazel-harbor-63, 99.23%), #2 "Precise Lemma" (izayoi-20, 99.23%), #4 lomfi 19-story focus entry (99.14%). Template studied from #1/#2/#4 artifacts (downloaded to work dir winners/).
- Kit: `~/workspace/makefun/news-image-20261119-kit/` (FRESH, CLI d17c2d22, harness 20d96c66 — BERBEDA/baru vs kit 17/18 Nov level 19). **Submit with this fresh kit; verify entry reaches "finished".**

## Template (winner pattern, from 17/18 Nov + #1 ronigrv/icantcodefyi)
- Cream paper, serif masthead with the day ("Thursday 19 November 2026").
- Region bar + field bar counting all stories; "THE DAY IN NUMBERS" strip.
- **13 core stories**, each with its own flat-illustration panel (kicker + headline + deck).
- Large PIL-drawn world map with 13 numbered pins + gold dots for the rest.
- ALSO ON list (29 items, 3 columns) → target **42 stories total**.
- DATE CHECK box naming stories deliberately excluded (first reported 18 Nov).
- PNG 1024×1024, ~500 KB.

## Build plan (20 Nov morning)
1. Research + verify all 19 Nov stories (search, morning + afternoon/evening coverage).
2. Pick 13 core stories (spread across regions/fields; prefer illustrated, high-impact).
3. Generate 13 flat illustrations (media pipeline), compose with PIL.
4. A/B proxy-judge vs the 18 Nov v2 template before submitting.
5. Submit with the FRESH kit; verify the entry reaches "finished" (not "failed") before reporting.

## Morning news head-start (19 Nov, to verify in the build)
- (fill in during the 20 Nov build; see `~/workspace/makefun/news-image-20261119-work/` for the research file)
