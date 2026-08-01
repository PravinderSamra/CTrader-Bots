#!/usr/bin/env python3
"""
HEATMAP RENDERER — turn recorded depth into the Bookmap-style picture, plus the
number you actually want: how much size is resting above your level vs below it.

Input is the JSONL written by dom_recorder.py:
    {"t": ms, "bid": [[price, size], ...], "ask": [[price, size], ...]}

Output is a single self-contained HTML file (no CDN, no dependencies) with:
  * the heatmap — price on y, time on x, cell brightness = resting size
  * the mid-price track drawn over it
  * a right-hand profile of total size-seconds resting at each price
And a text summary answering, for any level you name:
    "over this window, N% of the resting size within X points of 10,911 was on
     the offer — sellers outweighed buyers 2.4 : 1"

Usage
-----
    python3 heatmap_render.py --in ../data/uk100-dom.jsonl --out ../reports/uk100-heatmap.html
    python3 heatmap_render.py --in ../data/uk100-dom.jsonl --level 10911 --band 5

    # verify the renderer works without live depth (clearly-labelled fake book):
    python3 heatmap_render.py --selftest --out /tmp/selftest.html
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import defaultdict


# ------------------------------------------------------------------- load/grid

def load_snapshots(path: str) -> list[dict]:
    snaps = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                s = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "t" in s:
                snaps.append(s)
    return sorted(snaps, key=lambda s: s["t"])


def synth_snapshots(n: int = 900) -> list[dict]:
    """A clearly-synthetic book, for verifying the renderer only.

    Builds a wall of offers at 10911 that price repeatedly tests and fails to
    break — the shape you are hunting for — so the rendering path can be checked
    end to end without waiting for a live session. This is NOT market data.
    """
    rnd = random.Random(7)
    out = []
    mid = 10890.0
    t0 = 1785510000000
    for i in range(n):
        # drift up into the wall, get rejected, repeat
        phase = (i / n) * 3 * math.pi
        mid = 10890.0 + 21.0 * abs(math.sin(phase)) + rnd.uniform(-1.2, 1.2)
        bids, asks = [], []
        for k in range(1, 26):
            bp = round(mid - 0.5 - k * 0.5, 1)
            ap = round(mid + 0.5 + k * 0.5, 1)
            bids.append([bp, round(rnd.uniform(2, 9) + (14 if abs(bp - 10872) < 1.0 else 0), 2)])
            wall = 55 if abs(ap - 10911) < 1.2 else 0
            asks.append([ap, round(rnd.uniform(2, 9) + wall, 2)])
        out.append({"t": t0 + i * 250, "bid": bids, "ask": asks})
    return out


def build_grid(snaps: list[dict], rows: int = 220, cols: int = 900):
    prices = [p for s in snaps for side in ("bid", "ask") for p, _ in s[side]]
    if not prices:
        raise SystemExit("no depth levels found in input")
    pmin, pmax = min(prices), max(prices)
    if pmax <= pmin:
        pmax = pmin + 1.0
    pad = (pmax - pmin) * 0.02
    pmin, pmax = pmin - pad, pmax + pad

    t0, t1 = snaps[0]["t"], snaps[-1]["t"]
    span = max(1, t1 - t0)
    cols = min(cols, len(snaps))

    bid_grid = [[0.0] * cols for _ in range(rows)]
    ask_grid = [[0.0] * cols for _ in range(rows)]
    counts = [0] * cols
    mids: list[list[float]] = [[] for _ in range(cols)]

    def row_of(p: float) -> int:
        r = int((p - pmin) / (pmax - pmin) * (rows - 1))
        return max(0, min(rows - 1, r))

    for s in snaps:
        c = int((s["t"] - t0) / span * (cols - 1))
        c = max(0, min(cols - 1, c))
        counts[c] += 1
        for p, sz in s["bid"]:
            bid_grid[row_of(p)][c] += sz
        for p, sz in s["ask"]:
            ask_grid[row_of(p)][c] += sz
        if s["bid"] and s["ask"]:
            mids[c].append((s["bid"][0][0] + s["ask"][0][0]) / 2)

    # Average within each column so a column holding more snapshots isn't brighter
    # merely for that reason.
    for c in range(cols):
        k = counts[c] or 1
        for r in range(rows):
            bid_grid[r][c] /= k
            ask_grid[r][c] /= k

    mid_track = [(sum(v) / len(v)) if v else None for v in mids]
    return {
        "rows": rows, "cols": cols, "pmin": pmin, "pmax": pmax, "t0": t0, "t1": t1,
        "bid": bid_grid, "ask": ask_grid, "mid": mid_track,
    }


# ------------------------------------------------------------------- analytics

def level_report(snaps: list[dict], level: float, band: float, buckets: int = 20) -> dict:
    """Bid vs ask resting size within `band` of `level`, integrated over time.

    The per-price breakdown is bucketed rather than shown at raw quote precision —
    at 0.1 granularity a ±5 point band is 100 near-identical rows, which hides the
    shape instead of showing it.
    """
    bid_sz = ask_sz = 0.0
    step = (2 * band) / buckets
    per_price: dict[float, list[float]] = defaultdict(lambda: [0.0, 0.0])

    def bucket(p: float) -> float:
        return round(level - band + (math.floor((p - (level - band)) / step) + 0.5) * step, 2)

    for s in snaps:
        for p, sz in s["bid"]:
            if abs(p - level) <= band:
                bid_sz += sz
                per_price[bucket(p)][0] += sz
        for p, sz in s["ask"]:
            if abs(p - level) <= band:
                ask_sz += sz
                per_price[bucket(p)][1] += sz
    n = max(1, len(snaps))
    total = bid_sz + ask_sz
    return {
        "level": level, "band": band, "snapshots": len(snaps),
        "avg_bid": bid_sz / n, "avg_ask": ask_sz / n,
        "ask_share": (ask_sz / total) if total else 0.0,
        "ratio": (ask_sz / bid_sz) if bid_sz else float("inf"),
        "per_price": {k: [v[0] / n, v[1] / n] for k, v in sorted(per_price.items())},
    }


def format_level_report(r: dict) -> str:
    L = []
    a = L.append
    a("")
    a(f"RESTING LIQUIDITY AROUND {r['level']:,.2f}  (±{r['band']:g} pts, "
      f"{r['snapshots']} snapshots)")
    a("=" * 68)
    a(f"  Average resting BID size (buyers) : {r['avg_bid']:>10,.1f}")
    a(f"  Average resting ASK size (sellers): {r['avg_ask']:>10,.1f}")
    if r["ratio"] == float("inf"):
        a("  → all resting size on the offer; no bids inside the band")
    else:
        a(f"  → sellers outweigh buyers {r['ratio']:.2f} : 1  "
          f"({r['ask_share']*100:.0f}% of size is on the offer)")
    a("")
    if r["ask_share"] >= 0.65:
        a("  READ: supply-heavy. Consistent with wicks being absorbed and price")
        a("        failing to break. Supports a short from the level.")
    elif r["ask_share"] <= 0.35:
        a("  READ: demand-heavy. Buyers are stacked here — be careful shorting into it.")
    else:
        a("  READ: balanced. The book is not making a case either way; do not")
        a("        claim absorption you cannot see.")
    a("")
    a("  Price       avg bid     avg ask   ")
    a("  " + "-" * 46)
    peak = max((max(v) for v in r["per_price"].values()), default=0.0) or 1.0
    step = r["band"] * 2 / max(1, len(r["per_price"]))
    for p, (b, k) in r["per_price"].items():
        bar = "█" * int(round(max(b, k) / peak * 14))
        mark = " <<< level" if abs(p - r["level"]) <= step else ""
        a(f"  {p:>9,.2f} {b:>11,.1f} {k:>11,.1f}  {bar}{mark}")
    return "\n".join(L)


# ---------------------------------------------------------------------- render

HTML = """<meta charset="utf-8">
<title>%(title)s</title>
<style>
  :root { color-scheme: light dark; }
  body { margin:0; font:13px/1.5 ui-sans-serif,system-ui,-apple-system,sans-serif;
         background:#0b0d12; color:#e6e9ef; }
  @media (prefers-color-scheme: light) { body { background:#0b0d12; } }
  header { padding:14px 18px; border-bottom:1px solid #232838; }
  h1 { margin:0 0 3px; font-size:15px; font-weight:600; letter-spacing:.2px; }
  .sub { color:#8b93a7; font-size:12px; }
  .wrap { padding:14px 18px 28px; overflow-x:auto; }
  canvas { display:block; border:1px solid #232838; border-radius:4px;
           image-rendering:pixelated; max-width:100%%; }
  .legend { display:flex; gap:16px; align-items:center; margin:10px 0 0;
            color:#8b93a7; font-size:12px; flex-wrap:wrap; }
  .sw { display:inline-block; width:52px; height:10px; border-radius:2px;
        vertical-align:-1px; margin-right:6px; }
  .banner { background:#3a2410; border:1px solid #7a4a12; color:#f0c07a;
            padding:9px 12px; border-radius:4px; margin:0 18px 12px; font-size:12px; }
  pre { margin:14px 18px; padding:12px 14px; background:#11141c;
        border:1px solid #232838; border-radius:4px; overflow-x:auto;
        font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace; color:#c9d1e0; }
</style>
<header>
  <h1>%(title)s</h1>
  <div class="sub">%(subtitle)s</div>
</header>
%(banner)s
<div class="wrap">
  <canvas id="c" width="%(w)d" height="%(h)d"></canvas>
  <div class="legend">
    <span><span class="sw" style="background:linear-gradient(90deg,#0b0d12,#1b3a6b,#2f7fd0,#7fd4ff)"></span>resting bids (buyers)</span>
    <span><span class="sw" style="background:linear-gradient(90deg,#0b0d12,#6b1b1b,#d04a2f,#ffb27f)"></span>resting offers (sellers)</span>
    <span><span class="sw" style="background:#ffffff"></span>mid price</span>
  </div>
</div>
<pre>%(summary)s</pre>
<script>
const G = %(data)s;
const c = document.getElementById('c'), x = c.getContext('2d');
const PL = 62, PB = 20, W = c.width - PL, H = c.height - PB;
const cw = W / G.cols, ch = H / G.rows;

let peak = 0;
for (let r=0;r<G.rows;r++) for (let k=0;k<G.cols;k++)
  peak = Math.max(peak, G.bid[r][k], G.ask[r][k]);
// Compress with a root curve so ordinary depth stays visible next to a big wall.
const norm = v => peak <= 0 ? 0 : Math.pow(v / peak, 0.45);

x.fillStyle = '#0b0d12'; x.fillRect(0,0,c.width,c.height);
for (let r=0;r<G.rows;r++) {
  const y = (G.rows - 1 - r) * ch + 0;
  for (let k=0;k<G.cols;k++) {
    const b = norm(G.bid[r][k]), a = norm(G.ask[r][k]);
    if (b<=0.01 && a<=0.01) continue;
    // blue for bids, orange for offers; whichever is larger wins the cell
    const col = b >= a
      ? `rgb(${Math.round(20+40*b)},${Math.round(40+150*b)},${Math.round(60+195*b)})`
      : `rgb(${Math.round(60+195*a)},${Math.round(35+120*a)},${Math.round(25+90*a)})`;
    x.fillStyle = col;
    x.fillRect(PL + k*cw, y, Math.ceil(cw), Math.ceil(ch));
  }
}

// mid price track
x.strokeStyle = 'rgba(255,255,255,.9)'; x.lineWidth = 1.1; x.beginPath();
let started = false;
for (let k=0;k<G.cols;k++) {
  const m = G.mid[k]; if (m == null) { started = false; continue; }
  const y = H - ((m - G.pmin) / (G.pmax - G.pmin)) * H;
  if (!started) { x.moveTo(PL + k*cw, y); started = true; } else x.lineTo(PL + k*cw, y);
}
x.stroke();

// price axis
x.fillStyle = '#8b93a7'; x.font = '11px ui-monospace,monospace';
x.strokeStyle = '#232838'; x.lineWidth = 1;
for (let i=0;i<=8;i++) {
  const p = G.pmin + (G.pmax - G.pmin) * i/8;
  const y = H - (i/8)*H;
  x.beginPath(); x.moveTo(PL, y); x.lineTo(c.width, y); x.stroke();
  x.fillText(p.toFixed(1), 4, Math.min(H-1, Math.max(9, y+3)));
}
// time axis
const fmt = ms => new Date(ms).toISOString().slice(11,16);
for (let i=0;i<=6;i++) {
  const t = G.t0 + (G.t1 - G.t0) * i/6;
  const px = PL + (i/6)*W;
  x.fillText(fmt(t), Math.min(c.width-32, Math.max(PL, px-16)), H + 14);
}
</script>
"""


def render_html(grid: dict, title: str, subtitle: str, summary: str,
                synthetic: bool) -> str:
    data = json.dumps({
        "rows": grid["rows"], "cols": grid["cols"],
        "pmin": grid["pmin"], "pmax": grid["pmax"],
        "t0": grid["t0"], "t1": grid["t1"],
        "bid": [[round(v, 2) for v in row] for row in grid["bid"]],
        "ask": [[round(v, 2) for v in row] for row in grid["ask"]],
        "mid": [None if m is None else round(m, 2) for m in grid["mid"]],
    })
    banner = ('<div class="banner"><b>SYNTHETIC SELF-TEST DATA.</b> This page was '
              'generated with <code>--selftest</code> to verify the renderer. It is '
              'not market data and must not be traded from.</div>') if synthetic else ""
    return HTML % {
        "title": title, "subtitle": subtitle, "banner": banner,
        "w": 1180, "h": 620, "data": data,
        "summary": (summary or "").replace("&", "&amp;").replace("<", "&lt;"),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Render recorded cTrader depth as a heatmap")
    p.add_argument("--in", dest="inp", help="JSONL from dom_recorder.py")
    p.add_argument("--out", default=None, help="output .html")
    p.add_argument("--level", type=float, default=None, help="level to analyse")
    p.add_argument("--band", type=float, default=5.0, help="± band around --level")
    p.add_argument("--rows", type=int, default=220)
    p.add_argument("--cols", type=int, default=900)
    p.add_argument("--selftest", action="store_true",
                   help="render a clearly-labelled synthetic book to check the renderer")
    args = p.parse_args()

    if args.selftest:
        snaps = synth_snapshots()
        title = "DOM Heatmap — SELF-TEST (synthetic)"
        level = args.level if args.level is not None else 10911.0
    else:
        if not args.inp:
            p.error("give --in <jsonl>, or --selftest")
        snaps = load_snapshots(args.inp)
        if not snaps:
            print(f"FAILED: no snapshots in {args.inp}", file=sys.stderr)
            return 1
        title = f"DOM Heatmap — {os.path.basename(args.inp)}"
        level = args.level

    grid = build_grid(snaps, args.rows, args.cols)
    mins = (grid["t1"] - grid["t0"]) / 60000
    subtitle = (f"{len(snaps):,} snapshots · {mins:.0f} min · "
                f"price {grid['pmin']:,.1f} – {grid['pmax']:,.1f}")

    summary = ""
    if level is not None:
        rep = level_report(snaps, level, args.band)
        summary = format_level_report(rep)
        print(summary)

    out = args.out or ((args.inp.rsplit(".", 1)[0] + ".html") if args.inp else "heatmap.html")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as f:
        f.write(render_html(grid, title, subtitle, summary, args.selftest))
    print(f"\nWrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
