"""Larger capacity benchmark; replay stored inputs to avoid seed ambiguity."""
import json,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve
from capacity_cp import solve_capacity

# Released CSV is canonical; time-limited incumbents and timings may vary.
rows=[]
for r in pd.read_csv(ROOT/'results/capacity_large.csv').itertuples():
    pu=json.loads(r.p);c=json.loads(r.c);loads=json.loads(r.loads)
    result=solve_capacity(pu,c,10,loads,10,seconds=10)
    rows.append(dict(n=r.n,rep=r.rep,p=r.p,c=r.c,loads=r.loads,
        unrestricted_lower=solve([p/1000 for p in pu],c,10).value,**result))
pd.DataFrame(rows).to_csv(ROOT/'results/capacity_large_rerun.csv',index=False)
print('wrote capacity_large_rerun.csv; preserved original measurements')
