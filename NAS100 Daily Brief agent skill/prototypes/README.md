# prototypes/ — moved

The Phase-1 prototypes are now the **live skill scripts**, to avoid two copies
drifting apart. They live at:

    .claude/skills/nas100-daily-brief/scripts/

Run them from there:

```bash
cd .claude/skills/nas100-daily-brief/scripts
python3 brief.py                # the full brief
python3 brief.py --json         # structured payload
python3 source_health.py        # probe all data sources
python3 review_day.py           # grade the last completed day
python3 test_news_scorer.py     # 22 regression cases
```

This folder is kept only so the research docs' `prototypes/…` references
resolve to an explanation rather than a 404.
