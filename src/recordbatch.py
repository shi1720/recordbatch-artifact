"""Exact marginally robust sequential AND batch testing.

Outcomes are immutable, tests perfect, costs additive, setup paid per batch.
Every check is mandatory on the all-pass path. A failed batch stops execution.
This is NOT sequential statistical hypothesis testing.
"""
from dataclasses import dataclass
from functools import lru_cache
from math import prod, isfinite
from bisect import bisect_right
from numbers import Rational, Number


@dataclass(frozen=True)
class Solution:
    value: Number
    batches: tuple


def validate(p, c, beta):
    # Integers and Fractions are finite without conversion to binary float.
    # math.isfinite alone overflows on a valid very large rational cost.
    finite = lambda x: isinstance(x, Rational) or isfinite(x)
    if len(p) != len(c) or not p:
        raise ValueError('nonempty equally sized probability and cost arrays required')
    if any(not finite(x) or not 0 <= x <= 1 for x in p):
        raise ValueError('probabilities must be finite and in [0,1]')
    if any(not finite(x) or x < 0 for x in c) or not finite(beta) or beta < 0:
        raise ValueError('costs must be finite and nonnegative')


def evaluate(p, c, beta, batches, law='robust'):
    validate(p, c, beta)
    flat = [i for b in batches for i in b]
    if sorted(flat) != list(range(len(p))) or any(not b for b in batches):
        raise ValueError('batches must be a nonempty ordered partition')
    if law not in ('robust', 'independent'):
        raise ValueError('unknown law')
    survival, total = 1, 0
    for b in batches:
        total += survival * (beta + sum(c[i] for i in b))
        survival = (min(survival, min(p[i] for i in b)) if law == 'robust'
                    else survival * prod(p[i] for i in b))
    return total


def solve(p, c, beta):
    """O(n^3) arithmetic, O(n) auxiliary memory (excluding output).

    For each terminal survival q, solve a decreasing-probability DAG.
    Ties prefer fewer screening tests, ensuring a nonempty final batch.
    Supports Fraction inputs for exact rational verification.
    """
    validate(p, c, beta)
    n, total = len(p), sum(c)
    order = sorted(range(n), key=lambda i: (-p[i], i))
    best_value, best_path = beta + total, ()
    for q in sorted(set(p), reverse=True):
        if q == 1:
            continue
        dist, pred, length = {}, {}, {}
        for j in order:
            if p[j] < q or p[j] == 1:
                continue
            v, parent, count = beta + (1-q)*c[j], None, 1
            for i in dist:
                if p[i] > p[j]:
                    z = dist[i] + p[i]*beta + (p[i]-q)*c[j]
                    if (z, length[i]+1) < (v, count):
                        v, parent, count = z, i, length[i]+1
            dist[j], pred[j], length[j] = v, parent, count
        for j in dist:
            if p[j] == q:
                score = q*(total+beta)+dist[j]
                path, node = [], j
                while node is not None:
                    path.append(node)
                    node = pred[node]
                path = tuple(reversed(path))
                if len(path) == n:
                    # The final batch must contain at least one test.
                    # Truncating the path gives the same physical schedule,
                    # without the fictitious terminal setup charge.
                    path = path[:-1]
                    bs = tuple((i,) for i in path) + (tuple(i for i in range(n) if i not in path),)
                    score = evaluate(p, c, beta, bs)
                if (score, len(path)) < (best_value, len(best_path)):
                    best_value, best_path = score, path
    batches = tuple((i,) for i in best_path) + (tuple(i for i in range(n) if i not in best_path),)
    return Solution(best_value, batches)


def subset_dp(p, c, beta, law='robust', loads=None, capacity=None, outcomes=None):
    """Independent exponential oracle; O(3^n), optional batch capacity.

    Unnormalized probability of reaching S avoids conditional probabilities
    and remains well-defined when the survival probability is zero.
    """
    validate(p, c, beta)
    if law not in ('robust','independent','empirical'):
        raise ValueError('unknown law')
    if law=='empirical' and outcomes is None:
        raise ValueError('empirical outcomes required')
    if capacity is not None:
        if loads is None or len(loads)!=len(p) or capacity<=0 or not isfinite(capacity):
            raise ValueError('finite positive capacity and one positive load per test required')
        if any(not isfinite(a) or a<=0 for a in loads):
            raise ValueError('loads must be finite and positive')
    n, full = len(p), (1 << len(p))-1
    costs, survival, load = [0]*(full+1), [1]*(full+1), [0]*(full+1)
    for s in range(1, full+1):
        bit = s & -s
        i, t = bit.bit_length()-1, s ^ bit
        costs[s] = costs[t] + c[i]
        survival[s] = min(survival[t], p[i]) if law == 'robust' else survival[t]*p[i]
        load[s] = load[t] + (loads[i] if loads is not None else 0)
    if law=='empirical':
        import numpy as np
        x=np.asarray(outcomes)
        if x.ndim!=2 or x.shape[1]!=n or len(x)==0 or not np.isin(x,[0,1]).all():
            raise ValueError('invalid empirical panel')
        x=x.astype(bool)
        # Count full row masks; superset zeta transform gives all-pass counts.
        counts=np.bincount((x*(1 << np.arange(n))).sum(axis=1),minlength=full+1)
        for i in range(n):
            for s in range(full+1):
                if not (s >> i & 1):counts[s]+=counts[s | (1 << i)]
        survival=(counts/len(x)).tolist()
    choice = {}
    @lru_cache(None)
    def f(s):
        if s == full:
            return 0
        rem, best = full ^ s, float('inf')
        b = rem
        while b:
            if capacity is None or load[b] <= capacity:
                v = survival[s]*(beta+costs[b]) + f(s | b)
                if v < best:
                    best, choice[s] = v, b
            b = (b-1) & rem
        return best
    value, batches, s = f(0), [], 0
    if value == float('inf'):
        raise ValueError('infeasible capacity')
    while s != full:
        b = choice[s]
        batches.append(tuple(i for i in range(n) if b >> i & 1))
        s |= b
    return Solution(value, tuple(batches))


def solve_envelope(p, c, beta):
    """O(n^2 log n) record-path optimizer using a monotone-slope envelope.

    A line (p_i, d_i) represents d_i + p_i*(beta+c_j). Equal-p
    groups query before insertion, enforcing STRICT probability records.
    Rational inputs retain exact rational intersections and objectives.
    """
    validate(p,c,beta)
    n,total=len(p),sum(c)
    order=sorted(range(n),key=lambda i:(-p[i],i))
    best=Solution(beta+total,(tuple(range(n)),))
    for q in sorted(set(p),reverse=True):
        if q==1:continue
        # Lines have strictly decreasing slopes; starts strictly increase.
        hull=[(1,0,None)]
        starts=[float('-inf')]
        pred={}
        pos=0
        while pos<n and p[order[pos]]>=q:
            end=pos+1
            while end<n and p[order[end]]==p[order[pos]]:end+=1
            group=order[pos:end]
            if p[group[0]]==1:
                pos=end;continue
            candidates=[]
            for j in group:
                at=bisect_right(starts,beta+c[j])-1
                m,b,parent=hull[at]
                d=b+m*beta+(m-q)*c[j]
                pred[j]=parent
                candidates.append((d,j))
                if p[j]==q:
                    value=q*(total+beta)+d
                    path=[];node=j
                    while node is not None:
                        path.append(node);node=pred[node]
                    path=tuple(reversed(path))
                    if len(path)==n:path=path[:-1]
                    chosen=[False]*n
                    for i in path:chosen[i]=True
                    batches=tuple((i,) for i in path)+(tuple(i for i in range(n) if not chosen[i]),)
                    # Re-evaluation removes a possible empty-terminal charge.
                    value=evaluate(p,c,beta,batches)
                    if value<best.value:best=Solution(value,batches)
            intercept,j=min(candidates)
            slope=p[j]
            while hull:
                cross=(intercept-hull[-1][1])/(hull[-1][0]-slope)
                if cross>starts[-1]:break
                hull.pop();starts.pop()
            if not hull:cross=float('-inf')
            hull.append((slope,intercept,j));starts.append(cross)
            pos=end
    return best


def refine_zero_setup(p, c, solution):
    """Split the residual batch for beta=0; preserve the preceding screens.

    This weakly reduces cost on every Boolean outcome, hence under every law.
    Ratio ordering minimizes the independent-law cost of this fixed tail.
    It does not optimize nominal cost over all robust-optimal policies.
    """
    validate(p,c,0)
    evaluate(p,c,0,solution.batches)  # Validate the ordered partition.
    tail=sorted(solution.batches[-1],key=lambda i:
                (c[i]/(1-p[i]) if p[i]<1 else float('inf'),i))
    batches=solution.batches[:-1]+tuple((i,) for i in tail)
    return Solution(evaluate(p,c,0,batches),batches)


def solve_zero_setup(p, c):
    """Exact beta=0 optimizer: O(n log n) arithmetic, O(n) storage.

    An optimal singleton schedule can put a strict record path ending at a
    global minimum marginal before all remaining checks. Only this terminal
    marginal needs a lower-envelope pass. The residual tail is ratio sorted.
    """
    validate(p,c,0)
    n,total=len(p),sum(c)
    q=min(p)
    if q==1:
        return Solution(total,tuple((i,) for i in range(n)))
    order=sorted(range(n),key=lambda i:(-p[i],i))
    hull=[(1,0,None)];starts=[float('-inf')];pred={}
    best=None;pos=0
    while pos<n:
        end=pos+1
        while end<n and p[order[end]]==p[order[pos]]:end+=1
        group=order[pos:end]
        if p[group[0]]==1:
            pos=end;continue
        candidates=[]
        for j in group:
            at=bisect_right(starts,c[j])-1
            m,b,parent=hull[at]
            d=b+(m-q)*c[j]
            pred[j]=parent
            candidates.append((d,j))
        intercept,j=min(candidates)
        if p[j]==q:
            best=j
            break
        slope=p[j]
        while hull:
            cross=(intercept-hull[-1][1])/(hull[-1][0]-slope)
            if cross>starts[-1]:break
            hull.pop();starts.pop()
        if not hull:cross=float('-inf')
        hull.append((slope,intercept,j));starts.append(cross)
        pos=end
    path=[];node=best
    while node is not None:
        path.append(node);node=pred[node]
    path=tuple(reversed(path));chosen=set(path)
    tail=sorted((i for i in range(n) if i not in chosen),key=lambda i:
                (c[i]/(1-p[i]) if p[i]<1 else float('inf'),i))
    batches=tuple((i,) for i in path+tuple(tail))
    return Solution(evaluate(p,c,0,batches),batches)


def solve_policy(p, c, beta):
    """Operational policy: eliminate cost-free terminal batching at zero setup.

    Uses the general normal-form optimizer, then its pointwise dominating
    refinement. solve_zero_setup is a faster alternative at beta=0; robust
    ties can select different prefixes, so their nominal costs may differ.
    """
    result=solve_envelope(p,c,beta)
    return refine_zero_setup(p,c,result) if beta==0 else result


def empirical_costs(c, beta, batches, outcomes):
    """Per-episode costs; outcomes[e,i] is True exactly when check i passes."""
    import numpy as np
    x = np.asarray(outcomes, dtype=bool)
    alive, cost = np.ones(len(x), dtype=bool), np.zeros(len(x))
    for b in batches:
        cost[alive] += beta + sum(c[i] for i in b)
        alive &= x[:, list(b)].all(axis=1)
    return cost


def coupling_lp(p, c, beta, batches):
    """Full 2^n-outcome ambiguity LP, independent of prefix-min evaluation."""
    import numpy as np
    from scipy.optimize import linprog
    x = np.array([[bool(s >> i & 1) for i in range(len(p))]
                  for s in range(1 << len(p))])
    costs = empirical_costs(c, beta, batches, x)
    eq = np.vstack([np.ones(len(x)), x.T.astype(float)])
    r = linprog(-costs, A_eq=eq, b_eq=[1, *p], bounds=(0, None), method='highs')
    if not r.success:
        raise RuntimeError(r.message)
    return -r.fun
