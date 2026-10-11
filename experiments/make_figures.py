import sys,json
from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from recordbatch import solve
OUT=ROOT/'paper/figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'axes.labelsize':10.5,
    'axes.titlesize':11,'legend.fontsize':10,'pdf.fonttype':42,'ps.fonttype':42,
    'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
blue='#245B80';red='#B65A3C';grey='#68757E'

fig,ax=plt.subplots(1,2,figsize=(6.1,2.4),gridspec_kw={'width_ratios':[1,1.35]})
for y,p in enumerate([.8,.6,.3]):
    ax[0].plot([0,p],[y,y],lw=8,color=blue,solid_capstyle='butt')
    ax[0].plot([p,1],[y,y],lw=8,color='#DFE4E8',solid_capstyle='butt')
ax[0].axvline(.4,color=red,ls='--',lw=1)
ax[0].set(yticks=[0,1,2],yticklabels=['check A','check B','check C'],xlim=(0,1),xlabel='Shared uniform outcome U',title='Shared-uniform adversary')
ax[1].set_xlim(0,10);ax[1].set_ylim(0,3.4);ax[1].axis('off')
ax[1].set_title('Only all-pass continues')
for y,t in [(2.6,'Screen A: p = 0.8'),(1.4,'Screen C: p = 0.3'),(.2,'Final batch: all other checks')]:
    ax[1].add_patch(FancyBboxPatch((.3,y),9.4,.6,boxstyle='round,pad=0.08',lw=.9,edgecolor=blue,facecolor='#EDF3F6'))
    ax[1].text(5,y+.3,t,ha='center',va='center',fontsize=10.5)
for y in [2.5,1.3]:ax[1].annotate('',xy=(5,y-.42),xytext=(5,y),arrowprops={'arrowstyle':'->','color':grey})
fig.tight_layout(w_pad=1.5);fig.savefig(OUT/'structure.pdf');plt.close(fig)

s=pd.read_csv(ROOT/'results/synthetic.csv')
fig,axes=plt.subplots(1,2,figsize=(6.1,2.35))
groups=[0,.1,1,5]
for ax,col,title in [(axes[0],'risk','Worst-case cost ratio'),(axes[1],'nominal','Independent-law cost ratio')]:
    v=s.assign(risk=s.robust/s.ind_robust,nominal=s.robust_nominal/s.ind_nominal)
    ax.boxplot([v[v.setup_ratio==b][col] for b in groups],tick_labels=['0','0.1','1','5'],
        showfliers=False,patch_artist=True,boxprops={'facecolor':'#DDEAF2'},medianprops={'color':blue,'linewidth':1.5})
    ax.axhline(1,color=grey,lw=.7,ls='--');ax.set(title=title,xlabel='Setup / mean test cost',ylabel='RecordBatch / IndependentDP')
axes[1].set_yscale('log')
fig.tight_layout();fig.savefig(OUT/'synthetic.pdf');plt.close(fig)

b=pd.read_csv(ROOT/'results/benchmark.csv')
fig,ax=plt.subplots(figsize=(4.3,2.4))
for name,color,marker,label in [('cubic',grey,'s','Cubic DAG'),('envelope',blue,'o','Lower envelope')]:
    z=b[b.method==name].groupby('n').seconds.agg(['median','min','max'])
    ax.plot(z.index,z['median'],marker=marker,color=color,label=label,ms=4)
    ax.fill_between(z.index,z['min'],z['max'],color=color,alpha=.13)
ax.set(xscale='log',yscale='log',xlabel='Number of mandatory tests n',ylabel='Wall time (seconds)')
ax.legend(frameon=False);fig.tight_layout();fig.savefig(OUT/'scaling.pdf');plt.close(fig)

w=pd.read_csv(ROOT/'results/westermo.csv')
p=w.pivot(index=['system','setup_ratio'],columns='policy',values='replay_mean')
premium=(100*(p.RecordBatch/p.IndependentDP-1)).unstack('setup_ratio')
fig,ax=plt.subplots(figsize=(4.8,3.0))
im=ax.imshow(premium.values,cmap='RdBu_r',vmin=-350,vmax=350,aspect='auto')
for i in range(len(premium)):
    for j in range(4):
        val=premium.iloc[i,j];ax.text(j,i,f'{val:.1f}',ha='center',va='center',fontsize=9.5,color='white' if abs(val)>210 else '#172D3A')
ax.set(xticks=range(4),xticklabels=['0','0.1','1','5'],yticks=range(len(premium)),yticklabels=premium.index,
       xlabel='Setup / median training duration',title='Held-out cost premium over IndependentDP (%)')
fig.colorbar(im,ax=ax,shrink=.8,label='Positive = higher replay cost')
fig.tight_layout();fig.savefig(OUT/'replay.pdf');plt.close(fig)

summary={}
for ratio,g in s.groupby('setup_ratio'):
    summary[str(ratio)]={
        'median_wc_saving_pct':float(np.median(100*(g.ind_robust-g.robust)/g.ind_robust)),
        'median_nominal_premium_pct':float(np.median(100*(g.robust_nominal-g.ind_nominal)/g.ind_nominal)),
        'median_screens':float(g.screens.median())}
(ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2))
print('four vector figures and summary generated')
