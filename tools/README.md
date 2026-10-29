# tools

## `ds_log_diff.py`

Diffs two Daily Systems backtest logs. Written 2026-10-29 to find a $192.71
gap between the same bot, same settings, run on two different machines.

cTrader has no obvious trade-list export, but the bot does not need one: it
prints its whole history at the end of a run as `H|` lines, so the log IS the
trade list. This parses them, plus the `S|` startup lines (how much daily
history each symbol had in the LOCAL cache, which is the first thing to
compare between two installations), the `G|` daily-guard events and the `P|`
daily P&L.

```
python3 ds_log_diff.py <log>          summarise one run
python3 ds_log_diff.py <a> <b>        diff two runs, trade by trade
```

The diff keys a trade on (strategy, symbol, entry date) rather than on the
trade id, because a single extra trade early on renumbers everything after it
and an id-based diff then reports hundreds of false differences.

What it reports, in the order worth reading: whether the local data caches
differ, trades present in only one run, shared trades whose fills differ, and
whether the daily guard fired in one run and not the other. That last one
matters out of proportion to its size — the guard closes every open position,
so a borderline day that trips it on one machine and not the other changes
everything after it.
