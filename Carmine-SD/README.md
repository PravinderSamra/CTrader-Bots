# Carmine Rosato - supply &amp; demand

A syllabus reconstructed from his YouTube channel, built to teach the method
properly rather than to endorse it. Nothing here has been backtested.

## Layout

```
Carmine-SD/
|- 01-transcripts/      cleaned transcripts, one per video (timestamps stripped)
|- 02-documentation/    the syllabus PDFs
|- 03-diagrams/         generated schematics (do not edit by hand)
|- make_diagrams.py     regenerates 03-diagrams
|- make_module1_pdf.py  regenerates the Module 1 PDF
```

Both scripts need `python3.13` on this machine - matplotlib and reportlab are
installed there, not under the default `python3` (3.11).

## Modules

| # | Topic | Videos | Status |
|---|---|---|---|
| 1 | The zone: what it is, how to draw it, when it is tradable | 4 | **done** |
| 2 | Context: reading the day before you trade it | 4 | **done** |
| 3 | The trigger: order flow | 4 | **done** |
| 4 | The complete method, and risk | 4 | transcripts in, not yet built |

### Carried forward

- **Volume-profile shapes (P and b).** Module 1 section 7b reads absorption and
  exhaustion from footprint and delta only, because that is all those four
  transcripts use. He does teach profile shapes elsewhere. Still not covered by
  modules 2 or 3 - carry to module 4 or a later batch.
- **Resolved in module 3:** delta outliers as a fourth source of key levels (now
  added to module 2 section 5), and the confirmation layer that supersedes
  module 1 section 6.


## Source dating - read this before trusting a module

The corpus spans four years, and his tooling changes across it. Each video is
dated from the trading dates and index levels he quotes on screen; every
weekday he names matches the calendar for the year given.

| Video | Era | Evidence |
|---|---|---|
| 02 complete-sd-guide | Oct 2022 | "Friday October 7th", S&P 3675/3750 |
| 04 sd-zones-right-way | Jun 2022 | "June 28th", S&P 3828-3950, NDX 12160 |
| 07 why-i-love-sd-zones | Feb 2022 | "February 22nd", S&P 4295/4316 |
| 08 what-i-look-for | Apr 2022 | "April 21st/22nd" Thu/Fri, S&P 4503, NDX 14277 |
| 06 trading-sd-in-a-trend | Apr 2023 | "Thursday April 27th", S&P 4107-4115 |
| 01, 03, 05 | undated | no dates or index levels quoted |
| 11 orderflow-confirmation | ~2024 | ES 5046-5048 |
| 10 better-entries | ~2025 | ES 6595 |
| 16 january-reset | ~Jan 2025 | "2025" stated, ES 5823 |
| 09 orderflow-playbook | ~2026 | ES 6837/6838 |
| 12 orderflow-levels-up | ~2026 | ES 6934/6936 |
| 15 the-30k-mistake | ~2026 | ES 6967-7027 |
| 13 masterclass | ~2026 | ES 7360-7593 |
| 14 day-trading-strategy | ~2022 | ES 3758-3896 |

**Modules 1 and 2 are built entirely on 2022-23 material. Modules 3 and 4 are
mostly 2024-26.** Tooling tracks the same split: Bookmap is mentioned zero times
across every 2022 video, once in the April 2023 one, and four times in the
module-4 batch; footprint charts go from 6 mentions to 27.

So where a later module conflicts with an earlier one, the default reading is
**the method moved on**, not that he contradicted himself. For live trading,
prefer the newer statement and say so explicitly in the text.

## Module 1 sources

| Video | Length | ID |
|---|---|---|
| How To DRAW Supply &amp; Demand Zones | 14:00 | `OtDSG7iafjk` |
| Complete Supply &amp; Demand Trading Guide (DRAW - FIND - TRADE Zones) | 26:48 | `_ffbix1afZs` |
| How To Use Support and Resistance the RIGHT Way | 29:14 | `5qBo04SMUFc` |
| How To Trade Supply &amp; Demand Zones The RIGHT WAY | 19:15 | `NVSBpUiBVDM` |

Transcripts were supplied by hand from YouTube's own transcript panel. Automated
caption download is blocked by YouTube's bot check and was not worked around.

## Sourcing discipline

Every claim in the PDFs is tagged:

- **HIS RULE** - stated outright in a transcript
- **HIS WORDS** - direct quote
- **NOT STATED** - the method needs it and he does not specify it in this module's
  four videos
- **NOT IN THESE VIDEOS** - he does teach it, but outside this module's source set

Both labels describe the limits of the source set, not the limits of his method -
never write "he never teaches X" on the strength of four transcripts.
Gaps are flagged, never filled with generic textbook theory. Where videos
disagree, both readings are shown rather than one being picked.
