import csv, os
from ctrader_client import fetch_ohlcv_window
DATA=os.path.join(os.path.dirname(__file__),"..","data")
print("[GER40 M5] fetching 365d ...", flush=True)
bars=fetch_ohlcv_window(200,"M_5",365,1e5,chunk_hours=8,pause=0.15)
p=os.path.join(DATA,"GER40_M5_12m.csv")
with open(p,"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["timestamp","time","open","high","low","close","volume"]); w.writeheader(); w.writerows(bars)
print(f"[GER40 M5] saved {len(bars)} -> GER40_M5_12m.csv ({bars[0]['time'][:10]}..{bars[-1]['time'][:10]})", flush=True)
print("DONE",flush=True)
