"""
Dollar-terms executive report. $100,000 account, FLAT $100 risk per trade => 1R = $100,
so trade $ = R * 100 (stop-size independent). Best config per instrument, RR = 2/2.5/3/3.5.

Produces GROSS and NET-of-cost figures. Spread-bet indices have no separate commission;
the dealing cost is the bid/ask spread, modelled as ONE spread paid round-trip per trade:
    cost_R   = spread_pts / stop_pts        (constant per fixed-stop config)
    net_R    = gross_R - cost_R
Wins/losses/streaks are recomputed on net R so the after-cost view is internally honest.

Outputs per instrument x RR: yearly / monthly / weekly tables (gross+net) to analysis/dollar/.
"""
import os, sys, json
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions, backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analysis", "dollar")
os.makedirs(OUT, exist_ok=True)

RISK = 100.0          # $ per trade = 1R
ACCOUNT = 100_000.0
VOL = dict(vol_method="trailing", vol_mult=1.2)
RRS = [2.0, 2.5, 3.0, 3.5]

BEST = {
    "US30":   dict(range_ref="ny", lon_start=8.0, lon_end=9.5, bo_start=10.0, bo_end=13.0,
                   stop_method="fixed", stop_pts=75, **VOL),
    "NAS100": dict(range_ref="ny", lon_start=2.0, lon_end=9.5, bo_start=10.0, bo_end=11.0,
                   stop_method="fixed", stop_pts=40, **VOL),
}
# assumed round-trip dealing spread in index points (Pepperstone-style spread bet)
SPREAD_PTS = {"US30": 2.0, "NAS100": 1.5}


def streaks(signs):
    best_w = best_l = cur_w = cur_l = 0
    for s in signs:
        if s > 0:
            cur_w += 1; cur_l = 0
        elif s < 0:
            cur_l += 1; cur_w = 0
        else:
            cur_w = cur_l = 0
        best_w = max(best_w, cur_w); best_l = max(best_l, cur_l)
    return best_w, best_l


def enrich(tdf, inst, stop_pts):
    tdf = tdf.copy()
    tdf["dt"] = pd.to_datetime(tdf["date"])
    tdf = tdf.sort_values("dt").reset_index(drop=True)
    cost_R = SPREAD_PTS[inst] / stop_pts
    tdf["R_net"] = tdf["R"] - cost_R
    tdf["usd_gross"] = (tdf["R"] * RISK).round(2)
    tdf["usd_net"] = (tdf["R_net"] * RISK).round(2)
    tdf["year"] = tdf["dt"].dt.year
    tdf["month"] = tdf["dt"].dt.to_period("M").astype(str)
    iso = tdf["dt"].dt.isocalendar()
    tdf["week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    tdf["week_start"] = (tdf["dt"] - pd.to_timedelta(tdf["dt"].dt.weekday, unit="D")).dt.date
    return tdf, cost_R


def yearly_table(tdf, rcol, ucol):
    rows = []
    for yr, g in tdf.groupby("year"):
        w, l = streaks(np.sign(g[rcol]).tolist())
        wins = int((g[rcol] > 0).sum()); losses = int((g[rcol] < 0).sum())
        rows.append({"year": yr, "trades": len(g), "wins": wins, "losses": losses,
                     "win_pct": round(wins / len(g) * 100, 1),
                     "longest_win_streak": w, "longest_loss_streak": l,
                     "usd": round(g[ucol].sum(), 2), "total_R": round(g[rcol].sum(), 2)})
    df = pd.DataFrame(rows).sort_values("year")
    df["cum_usd"] = df["usd"].cumsum().round(2)
    df["account_end"] = (ACCOUNT + df["cum_usd"]).round(2)
    return df


def monthly_table(tdf, rcol, ucol):
    rows = []
    for m, g in tdf.groupby("month"):
        rows.append({"month": m, "trades": len(g), "wins": int((g[rcol] > 0).sum()),
                     "losses": int((g[rcol] < 0).sum()), "usd": round(g[ucol].sum(), 2)})
    return pd.DataFrame(rows).sort_values("month")


def weekly_table(tdf, rcol, ucol):
    rows = []
    for (wk, ws), g in tdf.groupby(["week", "week_start"]):
        rows.append({"week": wk, "week_start": str(ws), "trades": len(g),
                     "wins": int((g[rcol] > 0).sum()), "losses": int((g[rcol] < 0).sum()),
                     "usd": round(g[ucol].sum(), 2)})
    return pd.DataFrame(rows).sort_values("week")


def block(tdf, rcol, ucol):
    return {"yearly": yearly_table(tdf, rcol, ucol).to_dict(orient="records"),
            "monthly": monthly_table(tdf, rcol, ucol).to_dict(orient="records"),
            "weekly": weekly_table(tdf, rcol, ucol).to_dict(orient="records"),
            "total_usd": round(tdf[ucol].sum(), 2), "trades": len(tdf)}


def main():
    consol = {"risk_per_trade": RISK, "account": ACCOUNT, "rrs": RRS,
              "spread_pts": SPREAD_PTS,
              "config": {i: dict(BEST[i]) for i in BEST}, "data": {}}
    for inst, base in BEST.items():
        df = sessions.load_m5(os.path.join(ROOT, "data", inst, f"{inst.lower()}_m5.csv"))
        consol["data"][inst] = {}
        print(f"\n########## {inst}  (stop {base['stop_pts']}pt, spread {SPREAD_PTS[inst]}pt) ##########")
        for rr in RRS:
            cfg = bt.Config(instrument=inst, rr=rr, **base)
            tdf, s = bt.run(df, cfg)
            tdf, cost_R = enrich(tdf, inst, base["stop_pts"])
            gross = block(tdf, "R", "usd_gross")
            net = block(tdf, "R_net", "usd_net")
            consol["data"][inst][f"{rr:.1f}"] = {
                "cost_per_trade_usd": round(cost_R * RISK, 2), "gross": gross, "net": net}
            tag = f"{inst}_{str(rr).replace('.', 'p')}R"
            pd.DataFrame(net["yearly"]).to_csv(os.path.join(OUT, f"{tag}_yearly_net.csv"), index=False)
            pd.DataFrame(gross["yearly"]).to_csv(os.path.join(OUT, f"{tag}_yearly.csv"), index=False)
            pd.DataFrame(net["monthly"]).to_csv(os.path.join(OUT, f"{tag}_monthly_net.csv"), index=False)
            pd.DataFrame(net["weekly"]).to_csv(os.path.join(OUT, f"{tag}_weekly_net.csv"), index=False)
            print(f"  RR {rr}: gross ${gross['total_usd']:>8,.0f}  |  net ${net['total_usd']:>8,.0f}  "
                  f"(cost ${cost_R*RISK:.2f}/trade x {len(tdf)} = ${cost_R*RISK*len(tdf):,.0f})")
    json.dump(consol, open(os.path.join(OUT, "consolidated.json"), "w"), indent=1, default=str)
    print("\nconsolidated.json (gross+net) written")
    # compact gross-vs-net matrix
    for inst in BEST:
        print(f"\n{inst}: 3-yr $ gross -> net by RR")
        for rr in RRS:
            d = consol["data"][inst][f"{rr:.1f}"]
            print(f"  {rr}R: ${d['gross']['total_usd']:>8,.0f}  ->  ${d['net']['total_usd']:>8,.0f}")
    return consol


if __name__ == "__main__":
    main()
