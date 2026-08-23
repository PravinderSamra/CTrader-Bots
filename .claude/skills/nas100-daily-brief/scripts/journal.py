#!/usr/bin/env python3
"""
journal.py — write every scan to disk so it can be graded later.

Two files per scan, under `journal/<trading-day>/`:
  <HHMM>-<session>.json  the full machine record — every bias component, every
                         published level, fuel, regime, news counts
  <HHMM>-<session>.md    the human brief exactly as delivered

The JSON is the important one. Phase 4 cannot ask "which bias components
actually predicted the day" or "does price really react at the call wall"
unless the *predictions* were recorded before the outcome was known. Writing it
at scan time is the only moment that data exists uncontaminated.

Writing is best-effort: a journal failure must never break the brief.
"""
import json, os, re
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_journal_root():
    """The journal is DATA and lives with the project, not inside the skill.
    Walk up for the repo root, then into the project folder. Falls back to a
    sibling of the scripts dir so the module still works if moved."""
    env = os.environ.get("NAS100_JOURNAL_DIR", "").strip()
    if env:
        return os.path.abspath(env)
    d = _HERE
    for _ in range(6):
        d = os.path.dirname(d)
        cand = os.path.join(d, "NAS100 Daily Brief agent skill", "journal")
        if os.path.isdir(os.path.dirname(cand)):
            return os.path.abspath(cand)
    return os.path.abspath(os.path.join(_HERE, "..", "journal"))


JOURNAL_ROOT = _find_journal_root()


def _session_tag(ctx):
    return (ctx.get("session_window") or "UNKNOWN").lower()


def entry_from(d, markdown_text=None):
    """Reduce a full brief payload to the record we want to grade later."""
    lv, gx, bs = d["levels"], d["gex"], d["bias"]
    ctx = d.get("context") or {}
    mc = d.get("macro") or {}
    board = d.get("level_board") or []

    return {
        "schema": 1,
        "scan_utc": ctx.get("now_utc") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scan_et": ctx.get("now_et"),
        "trading_day": ctx.get("trading_day") or lv["trading_day"],
        "session_window": ctx.get("session_window"),
        "is_trading_day": ctx.get("is_trading_day"),

        # ---- what we PREDICTED (this is what gets graded) -----------------
        "prediction": {
            "price_at_scan": lv["price"],
            "bias_score": bs["score"],
            "bias_label": bs["label"],
            "strategy": bs["strategy_call"],
            "event_gate": bs.get("event_gate"),
            "expected_direction": (1 if bs["score"] >= 3 else
                                   -1 if bs["score"] <= -3 else 0),
            "gamma_flip": gx["gamma_flip"]["nas100"],
            "expiry_shape": (gx.get("expiry_structure") or {}).get("shape"),
            "fuel_state": lv["fuel"]["expansion_state"],
            "remaining_budget": lv["fuel"]["remaining_budget"],
            "adr14": lv["fuel"]["adr14"],
            "adr_used_pct": lv["fuel"]["adr_used_pct"],
            # every level we told the user to mark, with what we said would
            # happen there — graded against the real bars tomorrow
            "levels": [{"price": r["level"], "name": r["name"],
                        "kind": r["kind"], "dist": r["dist"],
                        "reach": r["reach"], "stretch": r.get("stretch", False),
                        "confluence": r.get("confluence", 1)}
                       for r in board],
        },

        # ---- the inputs, so a wrong call can be traced to its cause -------
        "inputs": {
            "bias_components": bs["components"],
            "fuel": lv["fuel"],
            "gamma": {k: v.get("net_gex_$bn_per_1pct")
                      for k, v in gx.get("buckets", {}).items()},
            "call_wall": (gx["buckets"].get("this_week", {}).get("call_wall") or {}).get("nas100"),
            "put_wall": (gx["buckets"].get("this_week", {}).get("put_wall") or {}).get("nas100"),
            "max_pain": gx.get("max_pain_week", {}).get("nas100"),
            "vol": {"vxn": (mc.get("volatility", {}).get("vxn_nasdaq_ivol") or {}).get("last"),
                    "vix": (mc.get("volatility", {}).get("vix") or {}).get("last"),
                    "vix9d_over_vix": mc.get("volatility", {}).get("vix9d_over_vix")},
            "rates": {"us10y": (mc.get("rates_fx", {}).get("us10y") or {}).get("last"),
                      "dxy": (mc.get("rates_fx", {}).get("dxy") or {}).get("last")},
            "news": {k: (mc.get("news_scored") or {}).get(k)
                     for k in ("raw_score", "bias_points", "label",
                               "scored_high_confidence", "needs_model_judgement")},
            "events_24h": (mc.get("calendar") or {}).get("upcoming_next_24h"),
        },

        # ---- filled in later by review_day.py ------------------------------
        "outcome": None,
    }


def write(d, markdown_text=None, root=None):
    """-> path of the JSON written, or {'_error': ...}. Never raises."""
    try:
        root = root or JOURNAL_ROOT
        e = entry_from(d, markdown_text)
        day = e["trading_day"]
        ts = datetime.fromisoformat(e["scan_utc"]).strftime("%H%M")
        tag = re.sub(r"[^a-z0-9]+", "", (e["session_window"] or "x").lower())
        folder = os.path.join(root, day)
        os.makedirs(folder, exist_ok=True)
        stem = os.path.join(folder, f"{ts}-{tag}")
        with open(stem + ".json", "w") as f:
            json.dump(e, f, indent=2, default=str)
        if markdown_text:
            with open(stem + ".md", "w") as f:
                f.write(markdown_text)
        _write_index(root)
        return stem + ".json"
    except Exception as ex:                     # never break the brief
        return {"_error": f"{type(ex).__name__}: {ex}"}


def _write_index(root):
    """A flat index so the reviewer and the skill can find the last scan fast."""
    scans = []
    for day in sorted(os.listdir(root)):
        dpath = os.path.join(root, day)
        if not os.path.isdir(dpath):
            continue
        for fn in sorted(os.listdir(dpath)):
            if fn.endswith(".json"):
                scans.append(os.path.join(day, fn))
    with open(os.path.join(root, "index.json"), "w") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "count": len(scans), "scans": scans,
                   "latest": scans[-1] if scans else None}, f, indent=2)


def last_scan_utc(root=None):
    """Timestamp of the most recent scan, for session_context. None if first run."""
    root = root or JOURNAL_ROOT
    try:
        with open(os.path.join(root, "index.json")) as f:
            idx = json.load(f)
        if not idx.get("latest"):
            return None
        with open(os.path.join(root, idx["latest"])) as f:
            return json.load(f)["scan_utc"]
    except Exception:
        return None


def load_day(day, root=None):
    """All scans for a trading day, oldest first."""
    root = root or JOURNAL_ROOT
    folder = os.path.join(root, day)
    if not os.path.isdir(folder):
        return []
    out = []
    for fn in sorted(os.listdir(folder)):
        if fn.endswith(".json"):
            with open(os.path.join(folder, fn)) as f:
                out.append(json.load(f))
    return out
