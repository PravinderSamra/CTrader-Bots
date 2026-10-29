# cBots

Source for the cTrader bots, one folder each. These are the files that run on
the trading machine: copy the `.cs` into cTrader's editor, or point cTrader at
the folder.

| bot | version | what it does |
|---|---|---|
| `Daily Systems/` | v1.4.2 | Six daily-bar systems (A-F) across 5 FTMO instruments, each with its own on/off switch. Daily loss guard, optional flat-over-weekend. |
| `Factory Bot/` | v1.3.2 | Runs any daily Strategy Factory strategy from its settings (8 entries, 3 filters, 5 exits) across 9 indices, with a shared risk budget. |
| `Pre-FOMC Drift/` | v1.0.1 | Buys the indices at 14:00 New York the day before an FOMC statement, sells at 13:58 the next day. Scheduled meetings only. |

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
