[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/stevencau55551/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/stevencau55551/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# news-image-20261120 — The World Today: Friday, 20 November 2026

A newspaper front page drawn entirely by `main.py` (Python 3.13, standard
library only, no network) summing up the world news of Friday 20 November
2026 in six panels:

1. **Trump delays Iran war decision to 2027** — "no rush", "see what
   happens" after Jan 1 (Reuters)
2. **Cyclone Akvan bears down on Odisha** — 300,000 evacuated, 423 rescue
   teams (The Hindu)
3. **Europe ready for talks with Russia** on ending the Ukraine war (BBC)
4. **Hayabusa2 drops its asteroid landing** after engine trouble (Space.com)
5. **GTA 6 sales pass $1.8 billion**, overtaking The Odyssey (Mezha)
6. **Fiji declares a national disaster** over severe drought (20 Nov headlines)

Also noted: World Children's Day, 20 November.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

The program draws the 1024x1024 PNG itself (zlib PNG encoder + a hand-made
5x7 pixel font) and is fully deterministic: two runs write byte-identical
files. Verified: sha256 `c507f398103737c266c8e2ef880cdeb8b84132eee4491b87fa389df5238a532d`,
41,077 bytes.

Entry for [make.fun competition `news-image-20261120`](https://make.fun/bounty/news-image-20261120), account @hulukahandap.
