"""Reproduce zero-setup ablations; optional seeded timing benchmark.

Uses the frozen p/c instances and released panels. It does not alter the
canonical synthetic or replay tables. Original arbitrary robust ties are
reconstructed from the cubic reference, then refined pointwise.
"""
from pathlib import Path
import sys,json,time,argparse
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve,solve_zero_setup,refine_zero_setup,evaluate,empirical_costs

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark',action='store_true')
    args=parser.parse_args();rows=[];replay=[]
    s=pd.read_csv(ROOT/'results/synthetic.csv')
    for _,r in s[s.setup_ratio==0].iterrows():
        p=json.loads(r.p);c=json.loads(r.c)
        raw=solve(p,c,0);ref=refine_zero_setup(p,c,raw);fast=solve_zero_setup(p,c)
        assert abs(ref.value-r.robust)<1e-8 and abs(fast.value-r.robust)<1e-8
        nominal=evaluate(p,c,0,ref.batches,'independent')
        assert abs(nominal-r.robust_nominal)<1e-8
        rows.append(dict(n=r.n,regime=r.regime,rep=r.rep,
            raw_nominal=evaluate(p,c,0,raw.batches,'independent'),refined_nominal=nominal,
            fast_nominal=evaluate(p,c,0,fast.batches,'independent'),robust=fast.value,
            fast_policy=json.dumps(fast.batches)))
    pd.DataFrame(rows).to_csv(ROOT/'results/zero_setup_ablation_rerun.csv',index=False)
    for path in sorted((ROOT/'data').glob('*_panel.npz')):
        a=np.load(path);p=a['p'].tolist();c=a['c'].tolist();x=a['test']
        raw=solve(p,c,0);ref=refine_zero_setup(p,c,raw)
        before=empirical_costs(c,0,raw.batches,x);after=empirical_costs(c,0,ref.batches,x)
        assert np.all(after<=before+1e-9)
        replay.append(dict(system=path.stem[:-6],raw_mean=before.mean(),refined_mean=after.mean(),
            raw_policy=json.dumps(raw.batches),refined_policy=json.dumps(ref.batches)))
    pd.DataFrame(replay).to_csv(ROOT/'results/zero_setup_replay_ablation_rerun.csv',index=False)
    if args.benchmark:
        rng=np.random.default_rng(120727);timings=[]
        for n in [128,512,2048,8192,32768]:
            for rep in range(5):
                p=rng.uniform(.05,.95,n).tolist();c=rng.integers(1,101,n).tolist()
                t=time.perf_counter();a=solve_zero_setup(p,c);dt=time.perf_counter()-t
                timings.append(dict(n=n,rep=rep,seconds=dt,value=a.value))
        pd.DataFrame(timings).to_csv(ROOT/'results/zero_setup_scaling_rerun.csv',index=False)
    print('120 synthetic and nine replay zero-setup ablations verified')

if __name__=='__main__':main()
