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
| 1 | *(link not yet supplied)* | — | — | — | — | — |
| 2 | [STEAL This INSANE 1-Minute Market Maker Trading Strategy (75% Win Rate)](https://youtu.be/35cyqDz-ej8) | Chart Fanatics | 2026-08-23 | 2:29:41 | [`.txt`](transcripts/chart-fanatics-35cyqDz-ej8.txt) | [analysis](analysis/chart-fanatics-freddy-siento.md) |

Video 1 was requested but no URL came through in the message — the sentence
"access the transcript for this YouTube video" arrived without a link. Add
the link and it can be processed the same way.

Both requested videos feature **Freddy Siento**, a ~20-year institutional
market maker who trades NQ futures off SPX/NDX options levels using GexBot's
Classic package.

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
