"""Tiny static SVG line-chart helper for the strategy PDFs."""
INK2 = "#52514e"; MUTED = "#7a7974"; GRID = "#e6e5e1"; SURF = "#fcfcfb"
BLUE = "#2a78d6"; ORANGE = "#eb6834"; AQUA = "#1baf7a"; GREY = "#a3a29c"


def nice_ticks(lo, hi, n=5):
    import math
    span = hi - lo or 1
    raw = span / n; mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw))
    t = math.floor(lo / step) * step; out = []
    while t <= hi + step * 0.001:
        if t >= lo - step * 0.001: out.append(round(t, 10))
        t += step
    return out, step


def chart(series, w=720, h=280, ylo=None, yhi=None, yfmt=lambda v: f"{v:,.0f}", xticks=(),
          markers=(), hlines=(), bands=(), title="", pad=(64, 16, 24, 34), zero=False):
    """series: list of dict(xs, ys, color, width, dash, label). xticks: [(x, text)].
    markers: [(x, y, 'buy'|'sell'|'dot', label)]. hlines: [(y, text)]. bands: [(x0, x1, text)]."""
    L, R, T, B = pad
    xs = [x for s in series for x in s["xs"]]; ys = [y for s in series for y in s["ys"] if y is not None]
    x0, x1 = min(xs), max(xs)
    lo = min(ys) if ylo is None else ylo; hi = max(ys) if yhi is None else yhi
    if zero: lo = min(lo, 0); hi = max(hi, 0)
    ticks, step = nice_ticks(lo, hi)
    lo = min(lo, ticks[0]); hi = max(hi, ticks[-1])
    hi += (hi - lo) * 0.04
    X = lambda x: L + (x - x0) / ((x1 - x0) or 1) * (w - L - R)
    Y = lambda y: T + (hi - y) / ((hi - lo) or 1) * (h - T - B)
    o = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}" '
         f'style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;background:{SURF};border-radius:8px">']
    for a, b, txt in bands:
        o.append(f'<rect x="{X(a):.1f}" y="{T}" width="{X(b)-X(a):.1f}" height="{h-T-B}" fill="#f0efec"/>')
        if txt: o.append(f'<text x="{(X(a)+X(b))/2:.1f}" y="{T+12}" font-size="10" fill="{MUTED}" text-anchor="middle">{txt}</text>')
    for t in ticks:
        o.append(f'<line x1="{L}" x2="{w-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L-6}" y="{Y(t)+4:.1f}" font-size="11" fill="{INK2}" text-anchor="end">{yfmt(t)}</text>')
    for yv, txt in hlines:
        o.append(f'<line x1="{L}" x2="{w-R}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 3"/>')
        if txt: o.append(f'<text x="{w-R-2}" y="{Y(yv)-4:.1f}" font-size="10" fill="{MUTED}" text-anchor="end">{txt}</text>')
    for x, txt in xticks:
        o.append(f'<line x1="{X(x):.1f}" x2="{X(x):.1f}" y1="{h-B}" y2="{h-B+4}" stroke="{MUTED}"/>')
        anc = "start" if X(x) - L < 30 else "end" if w - R - X(x) < 30 else "middle"
        o.append(f'<text x="{X(x):.1f}" y="{h-B+17}" font-size="11" fill="{INK2}" text-anchor="{anc}">{txt}</text>')
    o.append(f'<line x1="{L}" x2="{w-R}" y1="{h-B}" y2="{h-B}" stroke="{MUTED}" stroke-width="1"/>')
    for s in series:
        pts = []; segs = []
        for x, y in zip(s["xs"], s["ys"]):
            if y is None:
                if pts: segs.append(pts); pts = []
                continue
            pts.append(f"{X(x):.1f},{Y(y):.1f}")
        if pts: segs.append(pts)
        for p in segs:
            dash = f' stroke-dasharray="{s["dash"]}"' if s.get("dash") else ""
            o.append(f'<polyline points="{" ".join(p)}" fill="none" stroke="{s["color"]}" '
                     f'stroke-width="{s.get("width",2)}" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
    for x, y, kind, txt in markers:
        cx, cy = X(x), Y(y)
        if kind == "buy":
            o.append(f'<path d="M{cx:.1f},{cy+6:.1f} l7,12 h-14 z" fill="{AQUA}" stroke="{SURF}" stroke-width="2"/>')
            o.append(f'<text x="{cx:.1f}" y="{cy+32:.1f}" font-size="11" font-weight="600" fill="#0b0b0b" text-anchor="middle">{txt}</text>')
        elif kind == "sell":
            o.append(f'<path d="M{cx:.1f},{cy-6:.1f} l7,-12 h-14 z" fill="{ORANGE}" stroke="{SURF}" stroke-width="2"/>')
            o.append(f'<text x="{cx:.1f}" y="{cy-22:.1f}" font-size="11" font-weight="600" fill="#0b0b0b" text-anchor="middle">{txt}</text>')
        else:
            o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="{s["color"] if False else BLUE}" stroke="{SURF}" stroke-width="2"/>')
            if txt: o.append(f'<text x="{cx+8:.1f}" y="{cy-8:.1f}" font-size="11" fill="#0b0b0b">{txt}</text>')
    o.append("</svg>")
    return "\n".join(o)


def legend(items):
    return '<div style="display:flex;gap:16px;flex-wrap:wrap;font-size:9.5pt;color:#52514e;margin:4px 0">' + "".join(
        f'<span><span style="display:inline-block;width:14px;height:0;border-top:2px {"dashed" if d else "solid"} {c};'
        f'vertical-align:middle;margin-right:5px"></span>{t}</span>' for t, c, d in items) + "</div>"


def figure(title, svg, caption, leg=""):
    return (f'<figure style="margin:12px 0;break-inside:avoid"><div style="font-weight:600;font-size:10.5pt;margin-bottom:2px">{title}</div>'
            f'{leg}{svg}<figcaption style="color:#5b6475;font-size:9pt;margin-top:4px">{caption}</figcaption></figure>')
