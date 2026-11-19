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
| 2 | Context and zone selection | 4 | transcripts needed |
| 3 | The order-flow trigger | 4 | transcripts needed |
| 4 | The complete method, and risk | 4 | transcripts needed |

### Carried forward

Topics he teaches that module 1's four videos do not cover, to be picked up
once the relevant transcripts are in:

- **Volume-profile shapes (P and b).** Module 1 section 7b reads absorption and
  exhaustion from footprint and delta only, because that is all these four
  transcripts use. He does teach profile shapes elsewhere. Best fit: module 3,
  the order-flow trigger.

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
