#!/usr/bin/env python3
"""
DOM RECORDER — the actual Bookmap equivalent.

Bookmap's heatmap is not magic. It is one thing done well: subscribe to the
Level 2 order book, and every time it changes, remember the size resting at
every price. Then draw price on the y-axis, time on the x-axis, and shade each
cell by how much size was sitting there. Big resting offers above the market
show up as a bright band. When price runs into that band and stalls, you are
watching absorption. When the band vanishes before price arrives, it was spoof.

cTrader gives you the same input for free. The Open API exposes
ProtoOASubscribeDepthQuotesReq / ProtoOADepthEvent — real depth from your
broker's aggregated liquidity providers. The cTrader *MCP* server does not
expose it (it only has spot/trendbars/orders), which is why this connects to the
Open API directly.

This script maintains the book and writes one JSONL line per snapshot:

    {"t": 1785510000123, "bid": [[10869.5, 12.0], ...], "ask": [[10870.5, 8.0], ...]}

Feed that to heatmap_render.py to get the picture.

SETUP (one-off, free)
---------------------
1. Go to https://openapi.ctrader.com/ and sign in with your cTID.
2. Create an application. You get a Client ID and Client Secret.
3. Under the app, add your Pepperstone trading account and complete the OAuth
   flow to get an Access Token (scope: trading).
4. Find your ctidTraderAccountId — the numeric account id the token is bound to
   (this script will list them for you if you omit --account).
5. Export:
     export CTRADER_OA_CLIENT_ID=...
     export CTRADER_OA_CLIENT_SECRET=...
     export CTRADER_OA_ACCESS_TOKEN=...
     export CTRADER_OA_ACCOUNT_ID=...       # optional, discovered if omitted

    pip install ctrader-open-api

USAGE
-----
    # discover which symbols actually carry depth on your account
    python3 dom_recorder.py --probe

    # record UK100 depth for 2 hours
    python3 dom_recorder.py --symbol-id 113 --minutes 120 --out ../data/uk100-dom.jsonl

WHAT TO EXPECT — read this before you trust the output
------------------------------------------------------
Pepperstone is a CFD/spread-bet broker, not an exchange. The depth you receive
is its aggregated LP book, so:
  * FX pairs generally carry genuine multi-level depth.
  * Index and commodity CFDs (UK100, US30, XAUUSD) are frequently quoted by a
    much smaller set of LPs and may return very few levels, or none at all.
  * The sizes are that broker's available liquidity, NOT total market volume.
    They tell you what you can actually get filled against, which is arguably
    the more relevant number for your stop — but it is not exchange depth.

Run --probe FIRST. If your instruments come back with one level per side, the
heatmap will be thin and you should lean on level_stats.py plus a futures proxy
instead. Do not assume depth exists because the API has a message for it.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict

try:
    from twisted.internet import reactor, defer
    from ctrader_open_api import Client, Protobuf, TcpProtocol, EndPoints
    from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *  # noqa: F401,F403
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAApplicationAuthReq, ProtoOAAccountAuthReq, ProtoOAGetAccountListByAccessTokenReq,
        ProtoOASymbolsListReq, ProtoOASubscribeDepthQuotesReq, ProtoOADepthEvent,
    )
except ImportError:  # pragma: no cover
    print("Missing dependency. Run:  pip install ctrader-open-api twisted", file=sys.stderr)
    raise

PRICE_SCALE = 100_000.0   # depth quote prices are in pipettes
SIZE_SCALE = 100.0        # depth quote sizes are in cents of base → units


def _env(name: str, required: bool = True) -> str:
    v = (os.environ.get(name) or "").strip()
    if required and not v:
        print(f"FAILED: {name} is not set. See the SETUP block at the top of this file.",
              file=sys.stderr)
        sys.exit(1)
    return v


class DepthRecorder:
    """Maintains the live book from incremental depth events and snapshots it."""

    def __init__(self, symbol_id: int, out_path: str | None, snapshot_ms: int = 250,
                 max_levels: int = 40):
        self.symbol_id = symbol_id
        self.snapshot_ms = snapshot_ms
        self.max_levels = max_levels
        # quote id -> (side, price, size). The API sends deltas, not full books.
        self.book: dict[int, tuple[str, float, float]] = {}
        self.out = open(out_path, "a") if out_path else None
        self.last_snap = 0.0
        self.events = 0
        self.snaps = 0

    def apply(self, ev) -> None:
        self.events += 1
        for qid in getattr(ev, "deletedQuotes", []):
            self.book.pop(qid, None)
        for q in getattr(ev, "newQuotes", []):
            # Exactly one of bid/ask is populated per quote.
            if q.HasField("bid"):
                side, px = "bid", q.bid / PRICE_SCALE
            elif q.HasField("ask"):
                side, px = "ask", q.ask / PRICE_SCALE
            else:
                continue
            self.book[q.id] = (side, px, q.size / SIZE_SCALE)

    def maybe_snapshot(self) -> None:
        now = time.time() * 1000
        if now - self.last_snap < self.snapshot_ms:
            return
        self.last_snap = now

        # Several LP quotes can rest at the same price — aggregate them, which is
        # what actually matters for "how much is sitting there".
        bids: dict[float, float] = defaultdict(float)
        asks: dict[float, float] = defaultdict(float)
        for side, px, sz in self.book.values():
            (bids if side == "bid" else asks)[px] += sz

        snap = {
            "t": int(now),
            "bid": sorted(([p, round(s, 2)] for p, s in bids.items()), reverse=True)[:self.max_levels],
            "ask": sorted(([p, round(s, 2)] for p, s in asks.items()))[:self.max_levels],
        }
        line = json.dumps(snap)
        if self.out:
            self.out.write(line + "\n")
            self.out.flush()
        self.snaps += 1
        if self.snaps % 40 == 0:
            nb, na = len(snap["bid"]), len(snap["ask"])
            top_b = snap["bid"][0] if snap["bid"] else ["-", "-"]
            top_a = snap["ask"][0] if snap["ask"] else ["-", "-"]
            print(f"  {self.snaps:>6} snaps · {self.events:>7} events · "
                  f"{nb} bid / {na} ask levels · top {top_b[0]} x{top_b[1]} | "
                  f"{top_a[0]} x{top_a[1]}", file=sys.stderr)

    def close(self) -> None:
        if self.out:
            self.out.close()


def run(args) -> None:
    client_id = _env("CTRADER_OA_CLIENT_ID")
    client_secret = _env("CTRADER_OA_CLIENT_SECRET")
    token = _env("CTRADER_OA_ACCESS_TOKEN")
    account_id = args.account or os.environ.get("CTRADER_OA_ACCOUNT_ID")

    host = EndPoints.PROTOBUF_LIVE_HOST if args.live else EndPoints.PROTOBUF_DEMO_HOST
    client = Client(host, EndPoints.PROTOBUF_PORT, TcpProtocol)
    rec = DepthRecorder(args.symbol_id, args.out, args.snapshot_ms) if args.symbol_id else None
    state = {"deadline": None}

    def on_error(failure):
        print(f"FAILED: {failure}", file=sys.stderr)
        if reactor.running:
            reactor.stop()

    def connected(_):
        print(f"Connected to {host}", file=sys.stderr)
        req = ProtoOAApplicationAuthReq()
        req.clientId = client_id
        req.clientSecret = client_secret
        client.send(req).addCallbacks(app_authed, on_error)

    def app_authed(_):
        print("Application authenticated", file=sys.stderr)
        if account_id:
            return auth_account(int(account_id))
        req = ProtoOAGetAccountListByAccessTokenReq()
        req.accessToken = token
        client.send(req).addCallbacks(got_accounts, on_error)

    def got_accounts(msg):
        res = Protobuf.extract(msg)
        accts = list(res.ctidTraderAccount)
        if not accts:
            return on_error("access token is not linked to any trading account")
        print("Accounts on this token:", file=sys.stderr)
        for a in accts:
            print(f"  ctidTraderAccountId={a.ctidTraderAccountId} "
                  f"live={getattr(a, 'isLive', False)}", file=sys.stderr)
        return auth_account(accts[0].ctidTraderAccountId)

    def auth_account(acc_id: int):
        state["account"] = acc_id
        req = ProtoOAAccountAuthReq()
        req.ctidTraderAccountId = acc_id
        req.accessToken = token
        client.send(req).addCallbacks(account_authed, on_error)

    def account_authed(_):
        print(f"Account {state['account']} authenticated", file=sys.stderr)
        if args.probe:
            req = ProtoOASymbolsListReq()
            req.ctidTraderAccountId = state["account"]
            return client.send(req).addCallbacks(probe_symbols, on_error)
        subscribe(args.symbol_id)

    def probe_symbols(msg):
        res = Protobuf.extract(msg)
        syms = [(s.symbolId, s.symbolName) for s in res.symbol]
        print(f"\n{len(syms)} symbols on this account. Subscribing to each of your "
              f"instruments and watching for depth…\n", file=sys.stderr)
        wanted = [w.strip().upper() for w in args.probe_symbols.split(",")]
        targets = [(sid, nm) for sid, nm in syms
                   if any(w in nm.upper().replace("_SB", "") for w in wanted)]
        if not targets:
            print("None of the requested probe symbols matched. Available sample:",
                  file=sys.stderr)
            for sid, nm in syms[:40]:
                print(f"  {sid:>6}  {nm}", file=sys.stderr)
            return reactor.stop()
        state["probe_seen"] = defaultdict(lambda: {"events": 0, "bid": 0, "ask": 0})
        state["probe_names"] = dict(targets)
        for sid, nm in targets:
            print(f"  subscribing {nm} (id {sid})", file=sys.stderr)
            req = ProtoOASubscribeDepthQuotesReq()
            req.ctidTraderAccountId = state["account"]
            req.symbolId.append(sid)
            client.send(req)
        reactor.callLater(args.probe_seconds, probe_report)

    def probe_report():
        print(f"\n{'='*64}\nDEPTH PROBE — {args.probe_seconds}s\n{'='*64}", file=sys.stderr)
        seen = state.get("probe_seen", {})
        names = state.get("probe_names", {})
        for sid, nm in sorted(names.items(), key=lambda x: x[1]):
            d = seen.get(sid)
            if not d or d["events"] == 0:
                print(f"  {nm:<16} NO DEPTH — 0 events. Heatmap not possible here.",
                      file=sys.stderr)
            else:
                print(f"  {nm:<16} {d['events']:>5} events · "
                      f"peak {d['bid']} bid / {d['ask']} ask levels", file=sys.stderr)
        print(f"{'='*64}", file=sys.stderr)
        reactor.stop()

    def subscribe(symbol_id: int):
        req = ProtoOASubscribeDepthQuotesReq()
        req.ctidTraderAccountId = state["account"]
        req.symbolId.append(symbol_id)
        client.send(req).addCallbacks(subscribed, on_error)

    def subscribed(_):
        print(f"Subscribed to depth for symbolId {args.symbol_id}. "
              f"Recording for {args.minutes} minutes → {args.out}", file=sys.stderr)
        state["deadline"] = time.time() + args.minutes * 60
        reactor.callLater(args.minutes * 60, finish)

    def finish():
        if rec:
            rec.close()
            print(f"\nDone. {rec.events} depth events → {rec.snaps} snapshots in {args.out}",
                  file=sys.stderr)
        reactor.stop()

    def on_message(_, message):
        if message.payloadType != ProtoOADepthEvent().payloadType:
            return
        ev = Protobuf.extract(message)
        if args.probe:
            d = state["probe_seen"][ev.symbolId]
            d["events"] += 1
            nb = sum(1 for q in ev.newQuotes if q.HasField("bid"))
            na = sum(1 for q in ev.newQuotes if q.HasField("ask"))
            d["bid"] = max(d["bid"], nb)
            d["ask"] = max(d["ask"], na)
            return
        if rec and ev.symbolId == args.symbol_id:
            rec.apply(ev)
            rec.maybe_snapshot()

    def disconnected(_, reason):
        print(f"Disconnected: {reason}", file=sys.stderr)
        if rec:
            rec.close()

    client.setConnectedCallback(connected)
    client.setDisconnectedCallback(disconnected)
    client.setMessageReceivedCallback(on_message)
    client.startService()
    reactor.run()


def main() -> int:
    p = argparse.ArgumentParser(description="Record cTrader Level 2 depth to JSONL")
    p.add_argument("--symbol-id", type=int, default=0, help="cTrader symbolId to record")
    p.add_argument("--minutes", type=float, default=60.0)
    p.add_argument("--out", default="dom.jsonl")
    p.add_argument("--snapshot-ms", type=int, default=250,
                   help="how often to write a book snapshot")
    p.add_argument("--account", type=int, default=None, help="ctidTraderAccountId")
    p.add_argument("--live", action="store_true", help="use live host instead of demo")
    p.add_argument("--probe", action="store_true",
                   help="check which of your instruments actually deliver depth")
    p.add_argument("--probe-symbols", default="UK100,US30,XAUUSD,EURUSD,GBPUSD,US500,NAS100")
    p.add_argument("--probe-seconds", type=int, default=60)
    args = p.parse_args()

    if not args.probe and not args.symbol_id:
        p.error("give --symbol-id, or use --probe to find out what carries depth")
    run(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
