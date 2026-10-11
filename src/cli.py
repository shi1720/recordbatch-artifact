"""JSON command-line interface; see examples/validation.json."""
import argparse,json
from fractions import Fraction
from pathlib import Path
from recordbatch import solve_policy,solve_zero_setup,evaluate

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('instance',type=Path)
    parser.add_argument('--exact',action='store_true',help='rational arithmetic')
    parser.add_argument('--zero-setup-fast',action='store_true',help='O(n log n) alternative; requires beta=0')
    args=parser.parse_args()
    d=json.loads(args.instance.read_text())
    p,c,b=d['p'],d['c'],d.get('beta',0)
    if args.exact:
        p=[Fraction(str(v)) for v in p]
        c=[Fraction(str(v)) for v in c];b=Fraction(str(b))
    if args.zero_setup_fast and b!=0:
        parser.error('--zero-setup-fast requires beta=0')
    out=solve_zero_setup(p,c) if args.zero_setup_fast else solve_policy(p,c,b)
    result=dict(robust_expected_cost=float(out.value),batches=out.batches,
        independent_law_cost=float(evaluate(p,c,b,out.batches,law='independent')),
        cost_model='additive committed work plus setup; not parallel elapsed time')
    if args.exact:result['exact_robust_cost']=str(out.value)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
