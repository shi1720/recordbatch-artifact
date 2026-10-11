"""Paired timing run after the experiment jobs have finished."""
import sys,time
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve,solve_envelope
rng=np.random.default_rng(407)
rows=[]
for n in [16,32,64,128,256,512,1024,2048]:
    for rep in range(5):
        p=rng.uniform(.05,.95,n).tolist();c=rng.integers(1,101,n).tolist()
        methods=[('envelope',solve_envelope)]
        if n<=512:methods+=[('cubic',solve)]
        values=[]
        for name,fn in methods:
            t=time.perf_counter();out=fn(p,c,10);elapsed=time.perf_counter()-t
            rows.append(dict(n=n,rep=rep,method=name,seconds=elapsed,value=out.value))
            values.append(out.value)
        assert max(values)-min(values)<1e-7
pd.DataFrame(rows).to_csv(ROOT/'results/benchmark.csv',index=False)
print(pd.DataFrame(rows).groupby(['method','n']).seconds.median().to_string())
