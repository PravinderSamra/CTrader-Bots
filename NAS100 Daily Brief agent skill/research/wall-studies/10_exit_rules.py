"""Hard target, breakeven stop, or trail — which exit suits which stop size?

09 asked what target is REACHABLE. This asks what you should actually DO about
it, including the half of the question 09 cannot answer: moving the stop.
Reaching a target needs only the furthest point price closed, which 09 had.
Moving a stop needs the ORDER events happened in, so this re-derives every
setup from the M5 bars and walks it forward bar by bar.

FILL MODEL, and it differs from 09 deliberately:
    a resting take-profit fills on the WICK, so targets fill on the bar extreme
    a stop fills on the WICK too
    within one bar the STOP is checked FIRST
That last line is the conservative choice and it matters: when a bar both
reaches the target and takes the stop, this books the loss. Intra-bar order is
unknowable at M5, so the pessimistic read is the honest one. 09 measured
targets on CLOSES instead, which is pessimistic in the other direction, so the
two sets of numbers are not meant to match — 09 bounds what price did, this
bounds what an order would have got.

Still absent everywhere: spread, slippage, commission, partial fills.

RULES, each run against every setup:
    hard kR          target at k x risk, stop never moves
    BE at +xR        stop to entry once price trades x x risk in favour,
                     then run to the target
    trail xR         once +1R is reached, stop trails x x risk behind the
                     best favourable EXTREME, ratcheting only
A rule that books a scratch at breakeven scores 0.0R, which is the point of
testing it: it converts some losses into nothing and some winners into nothing
too, and the question is which it does more of at each stop size.
"""
import json, importlib.util, pathlib, statistics as st, collections

HERE = pathlib.Path(__file__).parent
BUCKETS = [(0, 25, "<=25pts"), (25, 40, "26-40"), (40, 55, "41-55"),
           (55, 75, "56-75"), (75, 100, "76-100"), (100, 1e9, ">100")]


def _load_05():
    spec = importlib.util.spec_from_file_location("s05", HERE / "05_sweep_reversal.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def setups(s05):
    """Re-derive the confirmed sweep -> LH/HL setups, keeping the bar index so
    the forward path is available."""
    B = s05.load_bars()
    out = []
    for day in sorted(B):
        lv = s05.levels_for(day)
        bars = B[day]
        if not lv or len(bars) < 100:
            continue
        for P, name in lv.items():
            for side in ("up", "down"):
                for s in s05.find_sweeps(bars, P, side):
                    c = s05.confirm_lh(bars, s["i_entry"], side, s["ext"])
                    if not c:
                        continue
                    k2, _ = c
                    entry = bars[k2]["c"]
                    stop = s["ext"] + s05.STOP_BUF if side == "up" \
                        else s["ext"] - s05.STOP_BUF
                    risk = abs(entry - stop)
                    if risk < 3:
                        continue
                    out.append({"day": day, "level": P, "name": name, "side": side,
                                "entry": entry, "stop": stop, "risk": risk,
                                "bars": bars[k2 + 1:]})
    return out


def favourable(s, px):
    return (s["entry"] - px) if s["side"] == "up" else (px - s["entry"])


def simulate(s, target_R, be_at=None, trail_R=None):
    """-> R booked. Stop checked before target within each bar."""
    risk, short = s["risk"], s["side"] == "up"
    stop = s["stop"]
    tgt = s["entry"] - target_R * risk if short else s["entry"] + target_R * risk
    best = 0.0
    armed = False
    for b in s["bars"]:
        adverse = b["h"] if short else b["l"]
        fav_px = b["l"] if short else b["h"]
        # 1. stop, on the wick, checked first
        if (adverse >= stop) if short else (adverse <= stop):
            return round(favourable(s, stop) / risk, 4)
        # 2. target, on the wick
        if (fav_px <= tgt) if short else (fav_px >= tgt):
            return float(target_R)
        # 3. then move the stop for the NEXT bar, never against the trade
        best = max(best, favourable(s, fav_px))
        if be_at is not None and best >= be_at * risk:
            stop = min(stop, s["entry"]) if short else max(stop, s["entry"])
        if trail_R is not None and best >= 1.0 * risk:
            cand = (s["entry"] - best) + trail_R * risk if short \
                else (s["entry"] + best) - trail_R * risk
            stop = min(stop, cand) if short else max(stop, cand)
    # day ended with the position open: mark out at the last close
    return round(favourable(s, s["bars"][-1]["c"]) / risk, 4) if s["bars"] else 0.0


RULES = [("hard 0.5R",  dict(target_R=0.5)),
         ("hard 1R",    dict(target_R=1.0)),
         ("hard 1.5R",  dict(target_R=1.5)),
         ("hard 2R",    dict(target_R=2.0)),
         ("hard 3R",    dict(target_R=3.0)),
         ("1R, BE@0.5R", dict(target_R=1.0, be_at=0.5)),
         ("2R, BE@1R",  dict(target_R=2.0, be_at=1.0)),
         ("3R, BE@1R",  dict(target_R=3.0, be_at=1.0)),
         ("trail 0.5R", dict(target_R=99.0, trail_R=0.5)),
         ("trail 1R",   dict(target_R=99.0, trail_R=1.0))]


if __name__ == "__main__":
    s05 = _load_05()
    S = setups(s05)
    print(f"{len(S)} setups re-derived from bars, "
          f"{len({s['day'] for s in S})} trading days")

    by = collections.defaultdict(list)
    for s in S:
        for lo, hi, nm in BUCKETS:
            if lo < s["risk"] <= hi:
                by[nm].append(s)
                break

    print("\nEXPECTANCY IN R PER TRADE, by stop size "
          "(stop checked before target within a bar)")
    print(f"{'rule':<13}" + "".join(f"{nm:>10}" for _, _, nm in BUCKETS) + f"{'ALL':>8}")
    scores = {}
    for label, kw in RULES:
        row = ""
        for _, _, nm in BUCKETS:
            v = by.get(nm)
            if not v:
                row += f"{'—':>10}"
                continue
            e = st.fmean(simulate(s, **kw) for s in v)
            scores[(label, nm)] = e
            row += f"{e:>+10.2f}"
        allv = st.fmean(simulate(s, **kw) for s in S)
        print(f"{label:<13}{row}{allv:>+8.2f}")

    print("\nBEST RULE PER STOP SIZE")
    print(f"{'stop size':<11}{'n':>5}{'med stop':>10}  {'best rule':<14}{'E(R)':>7}"
          f"   {'runner-up':<14}{'E(R)':>7}")
    for _, _, nm in BUCKETS:
        v = by.get(nm)
        if not v:
            continue
        rank = sorted(((scores[(l, nm)], l) for l, _ in RULES), reverse=True)
        print(f"{nm:<11}{len(v):>5}{st.median(s['risk'] for s in v):>9.0f}p  "
              f"{rank[0][1]:<14}{rank[0][0]:>+7.2f}   {rank[1][1]:<14}{rank[1][0]:>+7.2f}")

    print("\nWHAT THE BREAKEVEN STOP ACTUALLY TRADES AWAY  (target 2R, BE at 1R)")
    print(f"{'stop size':<11}{'n':>5}{'2R hit':>9}{'2R hit':>9}{'scratch':>9}"
          f"{'full loss':>11}{'full loss':>11}")
    print(f"{'':<11}{'':>5}{'hard':>9}{'with BE':>9}{'from BE':>9}"
          f"{'hard':>11}{'with BE':>11}")
    for _, _, nm in BUCKETS:
        v = by.get(nm)
        if not v:
            continue
        h = [simulate(s, target_R=2.0) for s in v]
        b = [simulate(s, target_R=2.0, be_at=1.0) for s in v]
        print(f"{nm:<11}{len(v):>5}"
              f"{sum(1 for x in h if x >= 1.99) / len(v):>8.0%}"
              f"{sum(1 for x in b if x >= 1.99) / len(v):>9.0%}"
              f"{sum(1 for x in b if -0.02 < x < 0.02) / len(v):>9.0%}"
              f"{sum(1 for x in h if x <= -0.98) / len(v):>10.0%}"
              f"{sum(1 for x in b if x <= -0.98) / len(v):>11.0%}")
