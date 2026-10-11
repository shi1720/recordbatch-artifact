import sys,time,json
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve_envelope,solve
rng=np.random.default_rng(20406)
rows=[]
for n in [16,32,64,128,256,512,1024,2048]:
    for rep in range(5):
        p=rng.uniform(.05,.95,n).tolist();c=rng.integers(1,101,n).tolist()
        t=time.perf_counter();s=solve_envelope(p,c,10);dt=time.perf_counter()-t
        rows.append(dict(n=n,rep=rep,seconds=dt,value=s.value,screens=len(s.batches)-1))
pd.DataFrame(rows).to_csv(ROOT/'results/envelope_scaling.csv',index=False)
errors=[]
for row in pd.read_csv(ROOT/'results/synthetic.csv').itertuples():
    p=json.loads(row.p);c=json.loads(row.c);b=row.setup_ratio*np.mean(c)
    errors.append(abs(solve_envelope(p,c,b).value-row.robust))
assert max(errors)<1e-8
(ROOT/'results/envelope_validation.json').write_text(json.dumps(dict(instances=len(errors),max_abs_error=max(errors)),indent=2))
print('envelope scaling and',len(errors),'synthetic comparisons complete')
