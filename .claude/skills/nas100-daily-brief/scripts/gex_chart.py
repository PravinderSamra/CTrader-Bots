#!/usr/bin/env python3
"""
gex_chart.py — the per-strike gamma profile, drawn as an SVG.

Renders what the commercial GEX dashboards render: one horizontal bar per
strike, positive gamma one way, negative the other, with the walls, the gamma
flip and spot marked across it.

SVG rather than a plotting library on purpose. This container is ephemeral and
matplotlib is not installed in a fresh one, so a chart that depends on it is a
chart that silently stops working on some future morning. SVG is also vector,
which is the honest answer to "make sure every level and label is legible" —
it stays sharp at any zoom on a phone.

    python3 gex_chart.py                    # writes /tmp/nas100-gex.svg
    python3 gex_chart.py out.svg --span 700
"""
import os, sys
from datetime import datetime, timezone

import gex_levels as gl

# ---- palette (fixed, not theme-derived: this is a standalone image) --------
BG       = "#0d1117"
PANEL    = "#161b22"
GRID     = "#2a3038"
TEXT     = "#e6edf3"
DIM      = "#8b949e"
POS      = "#26a641"      # positive gamma — dealers damp
POS_HI   = "#3fb950"
NEG      = "#c9401f"      # negative gamma — dealers amplify
NEG_HI   = "#f85149"
SPOT     = "#d0d7de"
CALLW    = "#f85149"
PUTW     = "#3fb950"
FLIP     = "#d29922"


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# The brief's level board reads the `this_week` bucket, which gex_levels
# defines as dte <= 7. The chart was built on dte <= 45 and so summed five
# more weeks of open interest into every bar. Same strikes, bigger numbers,
# and the C1-C3 ordering could differ from the board's ranking because the
# longer book weights far strikes more heavily. Two files delivered as one
# scan disagreed with each other.
#
# Default is now `week`, matching the brief. `full` stays available, labelled.
BOOKS = {"week": 7, "full": 45}


def collect(d=None, cfd_price=None, span=650, bin_pts=50, book="week"):
    dte_max = BOOKS.get(book, 7)
    """Per-strike net GEX in NAS100 price space, plus the marker levels."""
    if d is not None:
        gx = d["gex"]
        cfd_price = d["levels"]["price"]
        off = gx["cfd_offset"]
        S_ndx = gx["ndx_spot"]
        flip = (gx.get("gamma_flip") or {}).get("nas100")
    else:
        gx = gl.build(cfd_price)
        off = gx["cfd_offset"]
        S_ndx = gx["ndx_spot"]
        flip = (gx.get("gamma_flip") or {}).get("nas100")

    rows, _S, _Sq, _r, _a = gl.load_combined(max_dte=dte_max)
    buck = gl.bucket(rows, S_ndx, dte_max=dte_max, bin_pts=bin_pts, reprice=True)

    bars = []
    for x in buck:
        px = x["strike"] + off
        if abs(px - cfd_price) > span:
            continue
        bars.append({
            "price": round(px, 0),
            "net": x["net_gex"],
            "call_gex": x["call_gex"], "put_gex": x["put_gex"],
            "call_oi": x["call_oi"], "put_oi": x["put_oi"],
        })
    bars.sort(key=lambda b: -b["price"])

    above = [b for b in bars if b["price"] > cfd_price]
    below = [b for b in bars if b["price"] < cfd_price]
    # Call resistance: heaviest POSITIVE gamma above spot — dealers sell into it.
    # Match the BRIEF's definitions exactly, or the same word means two things
    # across two files. The brief's call wall is max CALL gamma above spot and
    # its put wall is max PUT gamma below — not max/min NET, which is what this
    # used and which put "put support" 295pts away from the brief's put wall on
    # 2026-08-27 (and 700pts away in a same-minute test).
    # Dominance, not just magnitude — see the note in gex_levels.build().
    call_res = max((b for b in above if b["call_gex"] > b["put_gex"]),
                   key=lambda b: b["call_gex"], default=None)
    # Put support: heaviest NEGATIVE gamma below spot.
    #
    # On NDX this is frequently absent. The index carries far less protective
    # put open interest than SPX, so the book below spot can be net-positive
    # all the way down. When that happens the honest answer is "there is no put
    # support on this chain today", not to promote the least-positive strike
    # and dress it up as one.
    put_sup = max((b for b in below if b["put_gex"] > b["call_gex"]),
                  key=lambda b: b["put_gex"], default=None)
    # Kept separately: the most negative NET strike below spot. It is a real
    # and different object (where dealers are most short gamma) and it used to
    # masquerade as the put wall.
    most_neg = min(below, key=lambda b: b["net"], default=None)
    most_neg = most_neg if most_neg and most_neg["net"] < 0 else None

    # Rank WITHIN SIGN, not by absolute size.
    #
    # C1-C3 are the heaviest POSITIVE strikes (dealers damp — these are the
    # brakes price stalls at). P1-P3 are the heaviest NEGATIVE strikes (dealers
    # amplify). An earlier version ranked by |net| on each side of spot, which
    # on a call-dominated chain like NDX stamped "P1" on a strongly POSITIVE
    # bar — the label said accelerant while the bar said brake.
    pos = sorted([b for b in bars if b["net"] > 0], key=lambda b: -b["net"])[:3]
    neg = sorted([b for b in bars if b["net"] < 0], key=lambda b: b["net"])[:3]
    return {
        "bars": bars, "spot": cfd_price, "flip": flip,
        "call_res": call_res, "put_sup": put_sup, "most_neg": most_neg,
        "book": book,
        "ranked_up": pos, "ranked_dn": neg,
        "net_total": sum(b["net"] for b in bars),
        "generated": datetime.now(timezone.utc),
        "bin_pts": bin_pts, "dte_max": dte_max,
    }


def consistency_check(c):
    """No strike may carry two labels that contradict each other.

    This is the test that would have caught the 29,291 bug: it was marked
    PUT WALL and ranked C3 (top-3 POSITIVE) on the same row, and nothing
    looked. D2's lesson was written down after the secondary-walls put labels
    were found backwards — "a new panel needs one test that it does not
    contradict the rest of the brief" — and then not implemented. Here it is.

    Returns a list of problems; empty means clean.
    """
    bad = []
    pos = {b["price"] for b in c["ranked_up"]}
    neg = {b["price"] for b in c["ranked_dn"]}
    pw = (c.get("put_sup") or {}).get("price")
    cw = (c.get("call_res") or {}).get("price")
    if pw is not None and pw in pos:
        bad.append(f"{pw:,.0f} is labelled PUT WALL and also ranked among the "
                   f"heaviest POSITIVE strikes")
    if cw is not None and cw in neg:
        bad.append(f"{cw:,.0f} is labelled CALL WALL and also ranked among the "
                   f"heaviest NEGATIVE strikes")
    by_price = {b["price"]: b for b in c["bars"]}
    if pw is not None and by_price.get(pw, {}).get("net", 0) > 0:
        bad.append(f"{pw:,.0f} is labelled PUT WALL but its NET gamma is "
                   f"{by_price[pw]['net']/1e9:+.2f}bn (positive)")
    if cw is not None and by_price.get(cw, {}).get("net", 0) < 0:
        bad.append(f"{cw:,.0f} is labelled CALL WALL but its NET gamma is "
                   f"{by_price[cw]['net']/1e9:+.2f}bn (negative)")
    for b in c["ranked_up"]:
        if b["net"] <= 0:
            bad.append(f"{b['price']:,.0f} carries a C rank with net "
                       f"{b['net']/1e9:+.2f}bn")
    for b in c["ranked_dn"]:
        if b["net"] >= 0:
            bad.append(f"{b['price']:,.0f} carries a P rank with net "
                       f"{b['net']/1e9:+.2f}bn")
    return bad


def render(c, path):
    """Lay the chart out in fixed columns so nothing can collide.

    The first version let the legend, the marker labels and the bar values all
    find their own x. They overlapped in three different places. Everything now
    has a reserved lane: marker labels far left, rank badge, strike, plot,
    value. Nothing is positioned relative to anything it could run into.
    """
    bars, spot = c["bars"], c["spot"]
    if not bars:
        raise SystemExit("no strikes in range")

    ROW, GAP = 30, 13
    MARK_W = 236                     # lane: marker labels (CALL RESISTANCE ...)
    BADGE_X, BADGE_W = MARK_W + 6, 36
    STRIKE_R = BADGE_X + BADGE_W + 76   # strikes right-aligned here
    L = STRIKE_R + 20                # plot starts
    PLOT_W = 700
    R = 168                          # lane: value labels
    TOP, BOT = 168, 96
    W = L + PLOT_W + R
    H = TOP + len(bars) * (ROW + GAP) + BOT
    MID = L + PLOT_W / 2

    peak = max(abs(b["net"]) for b in bars) or 1.0
    half = PLOT_W / 2 - 20

    def y_of(i):
        return TOP + i * (ROW + GAP)

    def y_price(p):
        for i in range(len(bars) - 1):
            hi, lo = bars[i]["price"], bars[i + 1]["price"]
            if lo <= p <= hi:
                f = (hi - p) / (hi - lo) if hi != lo else 0
                return y_of(i) + ROW / 2 + f * (ROW + GAP)
        return y_of(0) + ROW / 2 if p > bars[0]["price"] else y_of(len(bars) - 1) + ROW / 2

    rank_of = {}
    for tag, pool in (("C", c["ranked_up"]), ("P", c["ranked_dn"])):
        for n, b in enumerate(pool, 1):
            rank_of[b["price"]] = f"{tag}{n}"

    o = []
    A = o.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
      f'width="{W}" height="{H}" font-family="Segoe UI,Helvetica,Arial,sans-serif">')
    A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    A(f'<rect x="{L-10}" y="{TOP-16}" width="{PLOT_W+20}" '
      f'height="{len(bars)*(ROW+GAP)+20}" fill="{PANEL}" rx="6"/>')

    ts = c["generated"].strftime("%Y-%m-%d %H:%M UTC")
    A(f'<text x="28" y="46" fill="{TEXT}" font-size="30" font-weight="700">'
      f'NAS100 — net gamma by strike</text>')
    A(f'<text x="28" y="74" fill="{DIM}" font-size="17">{ts} &#183; spot '
      f'<tspan fill="{TEXT}" font-weight="700">{spot:,.0f}</tspan> &#183; '
      f'{c["bin_pts"]}pt bins &#183; expiries to {c["dte_max"]}d &#183; '
      f'net <tspan fill="{TEXT}">{c["net_total"]/1e9:+.2f}bn</tspan></text>')

    # legend: fixed 3-column grid, two rows. No measuring, no collisions.
    legend = [(POS_HI, "Positive GEX \u2014 dealers damp (brake)"),
              (CALLW, "Call wall \u2014 max call gamma above"), (FLIP, "Book flip"),
              (NEG_HI, "Negative GEX \u2014 dealers amplify"),
              (PUTW, "Put wall \u2014 max put gamma below"), (SPOT, "Spot")]
    COLW = (W - 56) / 3
    for n, (col, lab) in enumerate(legend):
        cx = 28 + (n % 3) * COLW
        cy = 106 + (n // 3) * 24
        A(f'<rect x="{cx:.0f}" y="{cy-11}" width="14" height="14" fill="{col}" rx="3"/>')
        A(f'<text x="{cx+21:.0f}" y="{cy+1}" fill="{DIM}" font-size="15">{_esc(lab)}</text>')

    A(f'<line x1="{MID}" y1="{TOP-16}" x2="{MID}" y2="{TOP+len(bars)*(ROW+GAP)+4}" '
      f'stroke="{GRID}" stroke-width="2"/>')

    for i, b in enumerate(bars):
        y = y_of(i)
        wpx = abs(b["net"]) / peak * half
        positive = b["net"] >= 0
        x = MID if positive else MID - wpx
        big = abs(b["net"]) >= peak * 0.55
        col = (POS_HI if big else POS) if positive else (NEG_HI if big else NEG)
        A(f'<line x1="{L-10}" y1="{y+ROW/2}" x2="{L+PLOT_W+10}" y2="{y+ROW/2}" '
          f'stroke="{GRID}" stroke-width="0.5" opacity="0.45"/>')
        A(f'<rect x="{x:.1f}" y="{y}" width="{max(wpx,2):.1f}" height="{ROW}" '
          f'fill="{col}" rx="3"/>')
        A(f'<text x="{STRIKE_R}" y="{y+ROW*0.72:.0f}" fill="{TEXT}" font-size="18" '
          f'text-anchor="end" font-weight="600">{b["price"]:,.0f}</text>')
        oi = b["call_oi"] if positive else b["put_oi"]
        A(f'<text x="{L+PLOT_W+14}" y="{y+ROW*0.70:.0f}" fill="{TEXT}" font-size="16" '
          f'text-anchor="start">{b["net"]/1e9:+.2f}bn'
          f'<tspan fill="{DIM}" font-size="14"> {oi:,.0f}</tspan></text>')
        if b["price"] in rank_of:
            tag = rank_of[b["price"]]
            A(f'<rect x="{BADGE_X}" y="{y+3}" width="{BADGE_W}" height="24" rx="5" '
              f'fill="{"#1f6feb" if tag[0]=="C" else "#a371f7"}"/>')
            A(f'<text x="{BADGE_X+BADGE_W/2}" y="{y+20}" fill="#fff" font-size="15" '
              f'text-anchor="middle" font-weight="700">{tag}</text>')

    # marker lines — label lives in its own left lane, so it cannot collide
    used = []
    def marker(price, col, label, dash="8,6"):
        if price is None:
            return
        y = y_price(price)
        ly = y
        while any(abs(ly - u) < 24 for u in used):     # nudge off a neighbour
            ly += 24
        used.append(ly)
        A(f'<line x1="{L-10}" y1="{y:.1f}" x2="{L+PLOT_W+10}" y2="{y:.1f}" '
          f'stroke="{col}" stroke-width="2.6" stroke-dasharray="{dash}"/>')
        # short connector from the label lane to the plot, routed BELOW the
        # strike text rather than through it
        A(f'<line x1="{MARK_W-14}" y1="{ly:.1f}" x2="{MARK_W-2}" y2="{ly:.1f}" '
          f'stroke="{col}" stroke-width="2.6"/>')
        A(f'<rect x="8" y="{ly-14:.1f}" width="{MARK_W-20}" height="27" rx="5" fill="{col}"/>')
        A(f'<text x="{MARK_W-24}" y="{ly+5:.1f}" fill="#0d1117" font-size="15" '
          f'text-anchor="end" font-weight="700">{_esc(label)}</text>')

    if c["call_res"]:
        marker(c["call_res"]["price"], CALLW, f'CALL WALL {c["call_res"]["price"]:,.0f}')
    if c["put_sup"]:
        marker(c["put_sup"]["price"], PUTW, f'PUT WALL {c["put_sup"]["price"]:,.0f}')
    else:
        A(f'<text x="8" y="{TOP-26}" fill="{PUTW}" font-size="14" '
          f'font-weight="600">No put wall: no strike below spot is '
          f'put-dominated</text>')
    if c["flip"]:
        marker(c["flip"], FLIP, f'BOOK FLIP {c["flip"]:,.0f}')
    if c.get("most_neg"):
        marker(c["most_neg"]["price"], "#a371f7",
               f'MOST SHORT {c["most_neg"]["price"]:,.0f}')
    marker(spot, SPOT, f'SPOT {spot:,.0f}', dash="none")

    fy = H - 62
    book_note = ("this week (dte \u2264 7) \u2014 same book as the brief's level board"
                 if c.get("book", "week") == "week"
                 else "FULL 45-day book \u2014 larger numbers than the brief's board, "
                      "which reads this week only")
    for n, line in enumerate([
        f"Book: {book_note}. Bars are NET gamma per strike (calls minus puts); "
        f"contract count in grey.",
        "C1-C3 rank the heaviest POSITIVE strikes (brakes), P1-P3 the heaviest NEGATIVE (accelerants).",
        "BOOK FLIP is where the WHOLE book's net gamma changes sign as spot moves \u2014 every contract "
        "repriced across a spot grid.",
        "It is NOT where these bars change colour. Single strikes can be negative above it and positive "
        "below it, so do not read the green/red boundary as the flip.",
        "Open interest is the previous close \u2014 the OCC publishes once daily. Greeks are repriced at "
        "the current spot. Dealer positioning is assumed, not observed."]):
        A(f'<text x="28" y="{fy+n*20}" fill="{DIM}" font-size="14">{_esc(line)}</text>')
    A('</svg>')
    open(path, "w").write("\n".join(o))
    return path


def persist(c, root=None):
    """Save the per-strike ladder this chart was drawn from.

    Without this the chart cannot be retro-tested at all. CBOE serves a LIVE
    snapshot only — there is no historical chain endpoint — so a chart for a
    past day cannot be rebuilt after the fact. The journal keeps the summarised
    walls (call_wall, put_wall, max_pain) but not the ladder, so the C1-C3 and
    P1-P3 rankings that the chart is FOR were never recoverable.

    Every chart run now writes its ladder. From here the retrospective can
    rebuild any past chart exactly and grade its ranked walls against what
    price did next.
    """
    import json
    root = root or os.path.join(_repo_research(), "chart-ladders")
    os.makedirs(root, exist_ok=True)
    stamp = c["generated"].strftime("%Y-%m-%d-%H%M")
    doc = {
        "schema": 1,
        "generated_utc": c["generated"].isoformat(timespec="seconds"),
        "spot": c["spot"], "flip": c["flip"],
        "bin_pts": c["bin_pts"], "dte_max": c["dte_max"], "book": c.get("book"),
        "net_total_$bn": round(c["net_total"] / 1e9, 3),
        "call_resistance": (c["call_res"] or {}).get("price"),
        "put_support": (c["put_sup"] or {}).get("price"),
        "ranked_positive": [{"rank": f"C{n}", "price": b["price"],
                             "net_$bn": round(b["net"] / 1e9, 3),
                             "oi": int(b["call_oi"])}
                            for n, b in enumerate(c["ranked_up"], 1)],
        "ranked_negative": [{"rank": f"P{n}", "price": b["price"],
                             "net_$bn": round(b["net"] / 1e9, 3),
                             "oi": int(b["put_oi"])}
                            for n, b in enumerate(c["ranked_dn"], 1)],
        "ladder": [{"price": b["price"], "net_$bn": round(b["net"] / 1e9, 4),
                    "call_oi": int(b["call_oi"]), "put_oi": int(b["put_oi"])}
                   for b in c["bars"]],
    }
    path = os.path.join(root, stamp + ".json")
    json.dump(doc, open(path, "w"), indent=1)
    return path


def _repo_research():
    d = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "..", ".."))
    for base, _dirs, _f in os.walk(d):
        if base.endswith("NAS100 Daily Brief agent skill"):
            return os.path.join(base, "research")
    return os.path.join(d, "research")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "/tmp/nas100-gex.svg"
    span = 650
    if "--span" in sys.argv:
        span = float(sys.argv[sys.argv.index("--span") + 1])
    book = (sys.argv[sys.argv.index("--book") + 1] if "--book" in sys.argv else "week")
    import ctrader_http as ct
    bid, ask = ct.get_live_price("NAS100")
    c = collect(cfd_price=round((bid + ask) / 2, 1), span=span, book=book)
    print(render(c, out))
    if "--no-persist" not in sys.argv:
        print(persist(c))
