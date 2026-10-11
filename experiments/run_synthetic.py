"""Frozen seed and complete grid; no significance-based instance selection."""
import sys, time, json, platform
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve,refine_zero_setup, subset_dp, evaluate
from capacity_cp import solve_capacity


def main():
    rng=np.random.default_rng(1720406)
    rows=[]
    for n in [8,12]:
        for regime,lo,hi in [('low',.05,.5),('mixed',.05,.95),('high',.8,.999)]:
            for rep in range(20):
                p=rng.uniform(lo,hi,n).tolist()
                c=rng.integers(1,101,n).tolist()
                for ratio in [0,.1,1,5]:
                    beta=ratio*np.mean(c)
                    t=time.perf_counter();raw=solve(p,c,beta)
                    r=refine_zero_setup(p,c,raw) if beta==0 else raw
                    rt=time.perf_counter()-t
                    t=time.perf_counter();ind=subset_dp(p,c,beta,law='independent');it=time.perf_counter()-t
                    ri=evaluate(p,c,beta,ind.batches)
                    seq=tuple((i,) for i in sorted(range(n),key=lambda i:(beta+c[i])/(1-p[i])))
                    rows.append(dict(n=n,regime=regime,rep=rep,setup_ratio=ratio,
                        robust=r.value,ind_robust=ri,ind_nominal=ind.value,
                        robust_nominal=evaluate(p,c,beta,r.batches,law='independent'),
                        raw_robust_nominal=evaluate(p,c,beta,raw.batches,law='independent'),
                        raw_robust_policy=json.dumps(raw.batches),
                        all_batch=beta+sum(c),serial_robust=evaluate(p,c,beta,seq),
                        screens=len(raw.batches)-1,robust_seconds=rt,ind_seconds=it,
                        p=json.dumps(p),c=json.dumps(c),robust_policy=json.dumps(r.batches),
                        independent_policy=json.dumps(ind.batches)))
    pd.DataFrame(rows).to_csv(ROOT/'results/synthetic.csv',index=False)
    scaling=[]
    for n in [16,32,64,128,256,512]:
        for rep in range(5):
            p=rng.uniform(.05,.95,n).tolist();c=rng.integers(1,101,n).tolist()
            t=time.perf_counter();s=solve(p,c,10);dt=time.perf_counter()-t
            scaling.append(dict(n=n,rep=rep,seconds=dt,value=s.value,screens=len(s.batches)-1))
    pd.DataFrame(scaling).to_csv(ROOT/'results/scaling.csv',index=False)
    cp=[]
    for n in [8,12,16]:
        for rep in range(10):
            pu=rng.integers(50,951,n).tolist();c=rng.integers(1,31,n).tolist()
            loads=rng.integers(1,7,n).tolist();beta=10
            out=solve_capacity(pu,c,beta,loads,10,seconds=10)
            lower=solve([p/1000 for p in pu],c,beta).value
            cp.append(dict(n=n,rep=rep,unrestricted_lower=lower,p=json.dumps(pu),
                           c=json.dumps(c),loads=json.dumps(loads),**out))
    pd.DataFrame(cp).to_csv(ROOT/'results/capacity.csv',index=False)
    (ROOT/'results/environment.json').write_text(json.dumps(dict(
        python=sys.version,platform=platform.platform(),machine=platform.machine(),
        seed=1720406,processor='Apple M4 Pro',threads=1),indent=2))
    print('completed',len(rows),'synthetic,',len(scaling),'scaling,',len(cp),'CP instances')

if __name__=='__main__':main()
