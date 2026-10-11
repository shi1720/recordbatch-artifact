"""Chronological replay on CC BY 4.0 Westermo outcomes. No deployment claim.

Select 12 most frequent tests from training sessions only, deterministic ties.
Retain complete panels only. Duration proxy is training median, not elapsed
batch time. Setup is a sensitivity parameter, not a measured overhead.
"""
import sys, json, zipfile, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve,refine_zero_setup,subset_dp,evaluate,empirical_costs


def main(path):
    with zipfile.ZipFile(path) as z:
        d=pd.read_csv(z.open('test-results.csv'),sep='\t')
    source_rows=len(d)
    d=d[(d.sessiontype=='N')&(d.rel=='M')&d.result.isin([0,1])]
    rows=[];panels=[]
    for system,g in d.groupby('system'):
        keys=g[['jid','sstarted']].drop_duplicates().sort_values(['sstarted','jid'])
        k=int(.6*len(keys));trainids=set(keys.iloc[:k].jid);testids=set(keys.iloc[k:].jid)
        tr=g[g.jid.isin(trainids)]
        counts=tr.groupby('tid').jid.nunique().reset_index(name='count')
        tids=counts.sort_values(['count','tid'],ascending=[False,True]).head(12).tid.tolist()
        A=tr.pivot_table(index='jid',columns='tid',values='result',aggfunc='max').reindex(columns=tids).dropna()
        B=g[g.jid.isin(testids)].pivot_table(index='jid',columns='tid',values='result',aggfunc='max').reindex(columns=tids).dropna()
        if len(A)<30 or len(B)<20:continue
        p=(A==0).mean().to_numpy()
        c=np.maximum(1,tr.groupby('tid').oduration.median().reindex(tids).to_numpy()).tolist()
        x=(B.to_numpy()==0)
        np.savez_compressed(ROOT/f'data/{system}_panel.npz',p=p,c=c,train=(A.to_numpy()==0),
            test=x,tids=tids,train_jid=A.index.to_numpy(),test_jid=B.index.to_numpy())
        panels.append(dict(system=system,total_sessions=len(keys),train_complete=len(A),test_complete=len(B),
                           train_failures=int((A!=0).sum().sum()),test_failures=int((B!=0).sum().sum()),tids=tids))
        for ratio in [0,.1,1,5]:
            beta=ratio*np.median(c)
            r=solve(p.tolist(),c,beta)
            if beta==0:r=refine_zero_setup(p.tolist(),c,r)
            ind=subset_dp(p.tolist(),c,beta,law='independent')
            emp=subset_dp(p.tolist(),c,beta,law='empirical',outcomes=A.to_numpy()==0)
            policies={'RecordBatch':r.batches,'IndependentDP':ind.batches,
                'EmpiricalDP':emp.batches,
                'AllBatch':(tuple(range(12)),),
                'RatioSerial':tuple((i,) for i in sorted(range(12),key=lambda i:(beta+c[i])/max(1-p[i],1e-15)))}
            for name,bs in policies.items():
                costs=empirical_costs(c,beta,bs,x)
                rows.append(dict(system=system,setup_ratio=ratio,policy=name,train_n=len(A),test_n=len(B),
                    replay_mean=costs.mean(),replay_std=costs.std(ddof=1),
                    train_robust=evaluate(p.tolist(),c,beta,bs),
                    train_nominal=evaluate(p.tolist(),c,beta,bs,law='independent'),
                    batches=json.dumps(bs),episode_costs=json.dumps(costs.tolist())))
    pd.DataFrame(rows).to_csv(ROOT/'results/westermo.csv',index=False)
    (ROOT/'data/provenance.json').write_text(json.dumps(dict(
        repository='https://github.com/westermo/test-results-dataset',
        commit='31ca0ab802fd2eecf3455c6622c2c18f5b3fe775',license='CC BY 4.0',
        attribution='Per Erik Strandberg / Westermo Network Communications AB',
        zip_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        raw_rows=source_rows,filtered_rows=len(d),selection='N sessiontype, M release, results 0 or 1; first 60% of sessions for training; top 12 training-frequency tids with ascending tid ties; complete panels only',
        duplicate_rule='maximum result within session/test',panels=panels),indent=2))
    print('completed',len(panels),'systems;',sum(p['test_complete'] for p in panels),'held-out sessions')

if __name__=='__main__':main(sys.argv[1])
