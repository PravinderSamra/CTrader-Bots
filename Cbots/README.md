# cBots

Source for the cTrader bots, one folder each. These are the files that run on
the trading machine: copy the `.cs` into cTrader's editor, or point cTrader at
the folder.

| bot | version | what it does |
|---|---|---|
| `Daily Systems/` | v1.4.2 | Six daily-bar systems (A-F) across 5 FTMO instruments, each with its own on/off switch. Daily loss guard, optional flat-over-weekend. |
| `Factory Bot/` | v1.3.2 | Runs any daily Strategy Factory strategy from its settings (8 entries, 3 filters, 5 exits) across 9 indices, with a shared risk budget. |
| `Pre-FOMC Drift/` | v1.0.1 | Buys the indices at 14:00 New York the day before an FOMC statement, sells at 13:58 the next day. Scheduled meetings only. |
| `ORB Volume Breakout v3.2 AutoLadder/` | v3.2 | London range (02:00-09:30), New York execution, volume + trend filtered breakout. Adds to winners, and sets daily risk from account balance. The one that trades NAS100 intraday. |

Added to the repo 29 Oct 2026. Before that they lived only on the trading
machines, so the git history starts here rather than at each bot's v1.0.

## They all log their own trade history

Each bot prints its full trade list on stop, as `H|` lines:

```
H|id|label|symbol|entry|exit|volume|entry px|exit px|gross|swap|commission|net
```

So comparing two runs needs no CSV export from cTrader — the log IS the trade
list. `tools/ds_log_diff.py` diffs two Daily Systems logs on exactly this.

## One design note worth knowing before you debug a run

Daily Systems and Factory Bot both queue their orders and only send one when
that market is actually trading:

```csharp
private bool Tradable(Book b) =>
    Server.Time - b.LastTick <= TimeSpan.FromMinutes(2)
        && Server.Time - b.OpenSince >= TimeSpan.FromMinutes(15);
```

An order that fails the test stays in the queue and retries every minute. This
means **the order in which symbols get filled is set by when each market ticks,
not by the order of the Symbols list** — so two machines with slightly
different tick data will place the same evening's orders in a different
sequence. That is the feature working, not a bug, and sorting the symbol list
would not change it (see the 29 Oct 2026 Air-vs-Pro investigation: identical
P&L through 2024 and 2025, diverging only where the two caches held different
2026 data).

Pre-FOMC Drift has no such gate: it trades two liquid US indices at a fixed
New York time when both are certainly open.

## ORB Volume Breakout v3.2 — the live settings are in the folder

`US100 LADDER Add to Winner 4.5R 0.1step.cbotset` is the parameter set that ran
in October 2026, so the code and the settings it actually ran under stay
together. Importing it into cTrader restores that configuration exactly.

The numbers that matter, with `FixedStopPoints = 60`:

| setting | value | in points |
|---|---|---|
| stop | 60 points | **60** |
| early risk reduction + add-to-winner trigger | 0.7R | **42** |
| stop after early risk reduction | 70% of 60 | **42** |
| break-even trigger | 2.5R | **150** |
| take profit | 4.5R | **270** |
| add size | 5.0x the risk taken off, capped at 2.5x original | — |

Read that against H25 in the NAS100 skill's `journal/HYPOTHESES.md`, which
measured NAS100's median favourable run at **about 55 points**, with 100 points
reached 31-44% of the time. The take-profit sits at 270.

This bot is a later generation of `ORB Projects/ORB Volume Breakout Bot/`
(v2.0), which holds the earlier research; v3.0 added Add To Winner and v3.2
added the balance-driven risk ladder, both on an unchanged v2.0 core.
