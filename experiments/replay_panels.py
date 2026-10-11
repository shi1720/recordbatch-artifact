"""Rebuild all replay policies from distributed derived panels."""
import json,sys
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve,refine_zero_setup,subset_dp,evaluate,empirical_costs
rows=[]
for path in sorted((ROOT/'data').glob('*_panel.npz')):
    a=np.load(path);p=a['p'].tolist();c=a['c'].tolist()
    train=a['train'];x=a['test'];n=len(p)
    for ratio in [0,.1,1,5]:
        beta=ratio*np.median(c)
        raw=solve(p,c,beta)
        rec=refine_zero_setup(p,c,raw) if beta==0 else raw
        policies={
            'RecordBatch':rec.batches,
            'IndependentDP':subset_dp(p,c,beta,law='independent').batches,
            'EmpiricalDP':subset_dp(p,c,beta,law='empirical',outcomes=train).batches,
            'AllBatch':(tuple(range(n)),),
            'RatioSerial':tuple((i,) for i in sorted(range(n),
                key=lambda i:(beta+c[i])/max(1-p[i],1e-15)))}
        for name,bs in policies.items():
            costs=empirical_costs(c,beta,bs,x)
            rows.append(dict(system=path.stem.removesuffix('_panel') if sys.version_info>=(3,9) else path.stem[:-6],
                setup_ratio=ratio,policy=name,train_n=len(train),test_n=len(x),
                replay_mean=costs.mean(),replay_std=costs.std(ddof=1),
                train_robust=evaluate(p,c,beta,bs),
                train_nominal=evaluate(p,c,beta,bs,law='independent'),
                batches=json.dumps(bs),episode_costs=json.dumps(costs.tolist())))
out=pd.DataFrame(rows)
out.to_csv(ROOT/'results/westermo_rerun.csv',index=False)
keys=['system','setup_ratio','policy']
old=pd.read_csv(ROOT/'results/westermo.csv').set_index(keys).sort_index()
new=out.set_index(keys).sort_index()
for col in ['replay_mean','replay_std','train_robust','train_nominal']:
    assert np.allclose(old[col],new[col],rtol=1e-12,atol=1e-9),col
print('all',len(out),'policy/configuration rows reproduced from distributed panels')
