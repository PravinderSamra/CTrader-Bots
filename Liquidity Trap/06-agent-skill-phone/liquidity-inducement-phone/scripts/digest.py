#!/usr/bin/env python3
"""
digest.py — condense an analyzer JSON read into a short, tail-safe block.

The full JSON is the source of truth, but it cannot be *read back* reliably
from a CI job log on a phone: the GitHub logs API only returns the TAIL of a
job, and `pools_above` + `pools_below` alone run to hundreds of lines. That
pushed price, session, bias and the fuel numbers off the top, and asking for
more tail just re-sent the same pool dump. The header — the part every gate
depends on — was effectively unreachable.

So the workflow prints the full JSON first and then pipes it through here. The
digest lands at the very END of the log, which is exactly the part a tail fetch
is guaranteed to return.

Usage:  python3 analyze.py XAUUSD --exec M_5 --json | tee read.json
        python3 digest.py < read.json
"""

import json
import sys


def band(z):
    return f"{z[0]:.2f}-{z[1]:.2f}" if z else "n/a"


def pool_line(p):
    flags = []
    if not p.get("confirmed"):
        flags.append("UNCONFIRMED")
    if p.get("swept"):
        flags.append("SWEPT")
    if p.get("too_close"):
        flags.append("too_close")
    tail = ("  [" + ", ".join(flags) + "]") if flags else ""
    return (f"    {band(p['zone']):<21} {p['name']:<13} "
            f"touches={p.get('touches', 0):<3} dist={p.get('dist', 0):>7.2f}"
            f"{tail}")


def tradable(p):
    """A pool that can serve as a target: confirmed, unswept, not noise-close."""
    return p.get("confirmed") and not p.get("swept") and not p.get("too_close")


def main():
    d = json.load(sys.stdin)
    if "error" in d:
        print(f"ERROR: {d['error']}  detail={d.get('detail')}")
        return 1

    s = d.get("session") or {}
    b = d.get("daily_bias") or {}
    r = d.get("range") or {}
    v = d.get("volume") or {}
    sw = d.get("recent_sweep")

    print(f"{d['instrument']}  price {d['price']}  as_of {d['as_of']}  "
          f"exec {d.get('exec_period')}")
    print(f"SESSION   {s.get('label')}  ny_local={s.get('ny_local')}  "
          f"mins_from_ny_open={s.get('minutes_from_ny_open')}  "
          f"in_trade_window={s.get('in_trade_window')}")
    print(f"BIAS      {b.get('label')} (score {b.get('score')})  "
          f"trend_day_potential={b.get('trend_day_potential')}")
    for reason in (b.get("reasons") or []):
        print(f"            - {reason}")
    print(f"FUEL      adr14={r.get('adr14')}  today_range={r.get('today_range')}"
          f"  used={r.get('adr_used_pct')}%  remaining={r.get('remaining_budget')}"
          f"  state={r.get('expansion_state')}  "
          f"min_target_dist={r.get('min_target_dist')}")
    print(f"VOLUME    state={v.get('state')}  exec_relative={v.get('exec_relative')}")
    print(f"NO_MANS_LAND {d.get('no_mans_land')}")

    print("\nSWEEP")
    if not sw:
        print("    none detected in the recent window")
    else:
        pt = sw.get("pool_taken")
        print(f"    side={sw['side']}  level={sw['level']}  "
              f"bars_ago={sw['bars_ago']}  bar_time={sw.get('bar_time')}")
        print(f"    lb_zone={band(sw.get('lb_zone'))}  "
              f"entry_zone={band(sw.get('entry_zone'))}  "
              f"stop_beyond={sw.get('stop_beyond')}")
        print(f"    still_valid={sw.get('still_valid')}  "
              f"thin_lb={sw.get('thin_lb')}  lb_width={sw.get('lb_width')}  "
              f"pools_cleared={sw.get('pools_cleared')}")
        print(f"    pool_taken={'none' if not pt else band(pt.get('zone'))}")
        print(f"    note: {sw.get('note')}")

    # The ladder comes before the single draw, because the draw is now just
    # T1 by another name and reading it first invites all-or-nothing exits.
    for name, key in (("TARGETS UP (T1 bank / T2 trail / T3 runner)", "targets_up"),
                      ("TARGETS DOWN (T1 bank / T2 trail / T3 runner)", "targets_down")):
        print(f"\n{name}")
        tiers = d.get(key) or []
        if not tiers:
            print("    none usable (no confirmed, unswept, in-reach pool)")
        for t in tiers:
            pct = ("n/a" if t["pct_of_remaining_budget"] is None
                   else f"{t['pct_of_remaining_budget']:.0f}% of budget")
            print(f"    {t['tier']}  {band(t['zone']):<21} {t['name']:<13} "
                  f"touches={t['touches']:<3} dist={t['dist']:>8.2f}  "
                  f"{t['quality']:<5}  {pct}")

    for name, key in (("DRAW UP", "draw_up"), ("DRAW DOWN", "draw_down")):
        p = d.get(key)
        print(f"\n{name}")
        print("    none in reach" if not p else pool_line(p).strip())

    for name, key in (("PATH UP (checkpoints to trail/partial at)", "path_up"),
                      ("PATH DOWN (checkpoints to trail/partial at)", "path_down")):
        print(f"\n{name}")
        items = d.get(key) or []
        if not items:
            print("    none")
        for p in items:
            print(f"    {band(p['zone']):<21} {p['name']:<13} "
                  f"touches={p.get('touches', 0):<3} dist={p.get('dist', 0):>7.2f}")

    # Only the near side of each book matters for a day trade, and the
    # unusable pools still get printed (flagged) so a "why not that level?"
    # question is answerable straight from the digest.
    for name, key in (("POOLS ABOVE (nearest 6)", "pools_above"),
                      ("POOLS BELOW (nearest 6)", "pools_below")):
        pools = d.get(key) or []
        usable = sum(1 for p in pools if tradable(p))
        print(f"\n{name}   [{usable} of {len(pools)} usable as targets]")
        for p in pools[:6]:
            print(pool_line(p))

    for w in (d.get("warnings") or []):
        print(f"\nWARNING: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
