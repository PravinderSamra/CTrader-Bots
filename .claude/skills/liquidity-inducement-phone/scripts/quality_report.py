#!/usr/bin/env python3
"""Retrospective: how good were the calls, the pools and the targets?

journal_review.py answers "what happened to each idea". This answers the
harder questions about the *recommendations themselves*:
  1. When the skill said NO_TRADE, what did the setup go on to do?
  2. Did the trigger zones and target zones actually get reached?
  3. Do target_touches and the fuel budget predict whether a target is hit?
  4. Did the close-confirmation gate change anything?

READ THE CONFOUNDS BEFORE QUOTING ANY OF THIS:

* Section 1 scores NO_TRADE ideas using conditional levels written at the
  time. They were never real orders. "The declined ideas made +3.45R" means
  "the levels I wrote down for setups I advised against would have made that",
  not "you left money on the table" - you could not have taken them as
  written, because several had no entry until the level was invented for the
  journal.
* Section 4 is NOT a controlled comparison. The gate was added part-way
  through, so "with gate" and "no gate" are two different date ranges and
  therefore two different market regimes. It cannot separate the gate from
  the week.
* Every bucket here is single-digit or low-double-digit n. These are
  descriptions, not findings. The point of running it is to notice which way
  things are leaning early, and to keep re-running as n grows.

Usage:  CTRADER_MCP_TOKEN=... python3 quality_report.py
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import journal_review as jr

JD = jr.DEFAULT_JOURNAL
entries = []
for f in sorted(glob.glob(os.path.join(JD, "*.jsonl"))):
    entries += [json.loads(l) for l in open(f) if l.strip()]

# Was hardcoded at 14 days, which silently shrinks the sample as the journal
# ages: the oldest entries sat exactly on the edge, so this and journal_review
# agreed by luck and would have diverged the next day with no warning.
DAYS = int(os.environ.get("QUALITY_DAYS", "21"))
bars = {i: jr.bars_for(i, DAYS) for i in {e["instrument"] for e in entries}}
rows, skipped = [], []
for e in entries:
    r = jr.score(e, bars[e["instrument"]])
    (rows.append((e, r)) if r else skipped.append(e))

directional = [(e, r) for e, r in rows if e.get("direction")]
print(f"{len(entries)} entries on disk over {DAYS} days of bars; "
      f"{len(rows)} scored; {len(directional)} directional "
      f"({len(rows)-len(directional)} london_alt with no direction)")
if skipped:
    # Dropping these silently let a truncated sample read as a complete one.
    print(f"SKIPPED {len(skipped)} too recent to judge: "
          + ", ".join(e["id"] for e in skipped))
print()

# ── 1. NO_TRADE calls that would have paid ──────────────────────────────────
print("=" * 78)
print("1. WHAT HAPPENED TO THE CALLS THE SKILL DECLINED")
print("=" * 78)
for label, pred in (("DECLINED  (NO_TRADE)", lambda e: e["state"] == "NO_TRADE"),
                    ("ACTIONABLE (WATCHING/ARMED)",
                     lambda e: e["state"] != "NO_TRADE")):
    grp = [(e, r) for e, r in directional if pred(e)]
    fil = [r for _, r in grp if r["filled"]]
    wins = [r for r in fil if r["outcome"] == "target"]
    tot = sum(r["r"] for r in fil)
    print(f"\n{label}: {len(grp)} ideas, {len(fil)} filled, "
          f"{len(wins)} hit target, totalR={tot:+.2f}")
    if fil:
        print(f"    win rate {len(wins)}/{len(fil)} = {100*len(wins)/len(fil):.0f}%"
              f"   expectancy {tot/len(fil):+.2f}R per fill")

print("\nDeclined ideas that WON (the ones a 'no trade' cost):")
for e, r in directional:
    if e["state"] == "NO_TRADE" and r["outcome"] == "target":
        print(f"  {e['as_of'][:16]} {e['instrument']:<7} {e['kind']:<10} "
              f"{e['direction']:<5} +{r['r']:.2f}R (peak {r['mfe_r']:.2f}R)")
        print(f"      reason given: {e['reason'][:95]}")

# ── 2. Did the zones get reached? ───────────────────────────────────────────
print("\n" + "=" * 78)
print("2. DID THE ZONES ACTUALLY GET REACHED?")
print("=" * 78)
with_trig = [(e, r) for e, r in directional if e.get("trigger_zone")]
trig_hit = [x for x in with_trig if x[1]["triggered"]]
plans = [(e, r) for e, r in directional
         if e.get("entry_zone") and e.get("stop") and e.get("target_zone")]
filled = [x for x in plans if x[1]["filled"]]
tgt_hit = [x for x in filled if x[1]["outcome"] == "target"]
triggered_plans = [x for x in plans if x[1]["triggered"]]
print(f"  trigger zone reached : {len(trig_hit)}/{len(with_trig)} "
      f"({100*len(trig_hit)/len(with_trig):.0f}%)")
print(f"  entry filled | plan   : {len(filled)}/{len(plans)} "
      f"({100*len(filled)/len(plans):.0f}%)   <- of ideas carrying a full plan")
if triggered_plans:
    print(f"  entry filled | triggered: {len(filled)}/{len(triggered_plans)} "
          f"({100*len(filled)/len(triggered_plans):.0f}%)   <- the real "
          f"conditional; the line above is not a funnel step")
print(f"  target reached       : {len(tgt_hit)}/{len(filled)} of fills "
      f"({100*len(tgt_hit)/len(filled):.0f}%)")

# ── 3. Does pool quality / distance predict a hit? ──────────────────────────
print("\n" + "=" * 78)
print("3. DO TARGET TOUCHES AND FUEL PREDICT A HIT?")
print("=" * 78)
print(f"{'touches':>8} {'n':>4} {'hit':>4} {'hit%':>6}   verdict")
buckets = {}
for e, r in filled:
    t = (e.get("context") or {}).get("target_touches")
    if t is None:
        continue
    key = ("0 (none)" if t == 0 else "1 (unconfirmed)" if t == 1
           else "2-4" if t <= 4 else "5+")
    buckets.setdefault(key, []).append(r)
for k in ("0 (none)", "1 (unconfirmed)", "2-4", "5+"):
    rs = buckets.get(k, [])
    if not rs:
        continue
    h = sum(1 for r in rs if r["outcome"] == "target")
    print(f"{k:>15} {len(rs):>4} {h:>4} {100*h/len(rs):>5.0f}%   "
          f"avgR={sum(r['r'] for r in rs)/len(rs):+.2f}")

print(f"\n{'target dist as % of remaining ADR budget':<46}{'n':>4}{'hit':>5}{'avgR':>8}")
fb = {}
for e, r in filled:
    c = e.get("context") or {}
    rem, tz, px = c.get("remaining_budget"), e.get("target_zone"), e.get("price_at_idea")
    if not rem or not tz or not px:
        continue
    dist = abs((tz[0] if e["direction"] == "long" else tz[1]) - px)
    pct = 100 * dist / rem
    key = "<50% (comfortable)" if pct < 50 else \
          "50-100% (tight)" if pct < 100 else "100%+ (beyond budget)"
    fb.setdefault(key, []).append(r)
for k in ("<50% (comfortable)", "50-100% (tight)", "100%+ (beyond budget)"):
    rs = fb.get(k, [])
    if not rs:
        continue
    h = sum(1 for r in rs if r["outcome"] == "target")
    print(f"{k:<46}{len(rs):>4}{h:>5}{sum(r['r'] for r in rs)/len(rs):>+8.2f}")

# ── 4. Confirmation gate effect ─────────────────────────────────────────────
print("\n" + "=" * 78)
print("4. EFFECT OF THE CLOSE-CONFIRMATION GATE")
print("=" * 78)
for lab, flag in (("with gate (requires_close_confirmation)", True),
                  ("no gate (filled on touch)", False)):
    rs = [r for e, r in filled if bool(e.get("requires_close_confirmation")) is flag]
    if not rs:
        continue
    h = sum(1 for r in rs if r["outcome"] == "target")
    tot = sum(r["r"] for r in rs)
    print(f"  {lab:<42} n={len(rs):<3} hit={h}  totalR={tot:+.2f}  "
          f"avg={tot/len(rs):+.2f}R")
print("\n  CONFOUND: state and gate are near-collinear with DATE. Cross-tab "
      "before reading either\n  section 1 or section 4 as an effect:")
cells = {}
for e, r in filled:
    cells.setdefault((("declined" if e["state"] == "NO_TRADE" else "actionable"),
                      ("GATED" if e.get("requires_close_confirmation")
                       else "no-gate")), []).append(r)
for (st, g), rs in sorted(cells.items()):
    print(f"    {st:<11}{g:<9} n={len(rs):<3} "
          f"R={sum(x['r'] for x in rs):+.2f}  "
          f"avg={sum(x['r'] for x in rs)/len(rs):+.2f}R")
