# YouTube research

Source material for the Gex-Bot strategy work: transcripts of videos where
practitioners explain how they trade gamma/options-flow levels, plus written
analysis of each.

## Layout

```
youtube-research/
├── README.md
├── vtt_to_text.py                  # VTT -> clean de-duplicated text
├── transcripts/                    # raw .vtt + cleaned .txt
└── analysis/                       # written analysis per video
```

## Videos

| # | Video | Channel | Date | Length | Transcript | Analysis |
|---|---|---|---|---|---|---|
| 1 | [Master Gexbot Classic - Trade Like a Pro with This Simple Yet Powerful Tool!](https://youtu.be/6r2329ybeb8) | GexFuture Trading | 2025-03-16 | 49:48 | [`.txt`](transcripts/gexfuture-master-classic-6r2329ybeb8.txt) | [analysis](analysis/gexfuture-master-gexbot-classic.md) |
| 2 | [STEAL This INSANE 1-Minute Market Maker Trading Strategy (75% Win Rate)](https://youtu.be/35cyqDz-ej8) | Chart Fanatics | 2026-08-23 | 2:29:41 | [`.txt`](transcripts/chart-fanatics-35cyqDz-ej8.txt) | [analysis](analysis/chart-fanatics-freddy-siento.md) |
| 3 | [Understanding Our Visualizations](https://youtu.be/pz5oIhQEJOs) | **gexbot (official)** | 2023-10-14 | 44:01 | [`.txt`](transcripts/gexbot-official-understanding-visualizations-pz5oIhQEJOs.txt) | [analysis](analysis/gexbot-official-understanding-visualizations.md) |

**[Strategy synthesis](analysis/strategy-synthesis.md)** merges videos 1 and 2
into one specification — read that first.

**Video 3 is the primary source and outranks the other two on anything
factual about what the product computes.** It is the founders explaining
their own model, and it settles the volume-vs-open-interest question the
other two disagreed on. It also carries the one caveat neither trader
mentions: the naive sign assumption is claimed to hold **for SPX**, not
universally — which matters, because we trade NDX.

Videos 1 and 2 are **Freddy Siento**, a ~20-year institutional market maker who
trades NQ futures off SPX gamma levels using GexBot's Classic package.
Video 1 is his own channel and is the *operational* one — the actual screen
and rules. Video 2 is a long-form interview and is the *explanatory* one —
why the levels work. Video 1 is more useful for implementation despite being
17 months older.

## Fetching a transcript

```bash
cd transcripts
yt-dlp --skip-download --write-auto-subs --write-subs \
       --sub-langs "en.*" --sub-format "vtt/srv3/best" \
       -o "%(channel)s-%(id)s.%(ext)s" "<url>"

cd .. && python3 vtt_to_text.py \
    transcripts/<file>.en-GB.vtt transcripts/<file>.txt
```

Two notes learned the hard way:

- **Always clean the VTT.** YouTube auto-captions use a rolling two-line
  window, so a naive extraction repeats nearly every word and roughly
  doubles the length. `vtt_to_text.py` keeps only newly-appearing tokens and
  re-flows into 30-second timestamped paragraphs.
- **Request only English.** `--sub-langs "en.*"` still enumerates ~26
  translated variants and YouTube starts returning HTTP 429 after the first
  one. The first file (`en-GB`) is the one that matters; the 429s on the
  rest are harmless.

## Searching the transcripts

Auto-captions mangle proper nouns badly. In the Chart Fanatics transcript
"GexBot" never appears literally — it shows up as **"guestbot"**, **"guess
what"** and **"Gexot"**. Search for concepts (`gamma`, `wall`, `convexity`,
`level`) rather than product names, and expect to read around the hits.
