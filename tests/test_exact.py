import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from fractions import Fraction as Q
from itertools import product
import random
import pytest
from recordbatch import (solve, solve_envelope, subset_dp, evaluate, coupling_lp,
                         solve_zero_setup, refine_zero_setup, solve_policy)
from capacity_cp import solve_capacity


def test_rational_grid():
    """Every 3-test instance on a 3x2x3 parameter grid: 648 exact checks."""
    for p in product([Q(0), Q(1,2), Q(1)], repeat=3):
        for c in product([0, 2], repeat=3):
            for beta in [0, 1, 5]:
                a, b = solve(p, c, beta), subset_dp(p, c, beta)
                assert a.value == b.value
                assert solve_envelope(p,c,beta).value == b.value
                assert a.value == evaluate(p, c, beta, a.batches)


def test_random_oracle():
    rng = random.Random(1720406)
    for n in range(1, 10):
        for _ in range(30):
            p = [Q(rng.randrange(101),100) for _ in range(n)]
            c = [rng.randrange(21) for _ in range(n)]
            beta = rng.randrange(20)
            a, b = solve(p,c,beta), subset_dp(p,c,beta)
            assert a.value == b.value
            assert solve_envelope(p,c,beta).value == b.value
            assert a.value == evaluate(p,c,beta,a.batches)


def test_full_coupling_lp():
    rng = random.Random(417)
    for n in range(2,9):
        for _ in range(10):
            p = [rng.random() for _ in range(n)]
            c = [rng.randrange(1,30) for _ in range(n)]
            order = rng.sample(range(n),n)
            batches = tuple(tuple(order[i:i+2]) for i in range(0,n,2))
            assert coupling_lp(p,c,3,batches) == pytest.approx(evaluate(p,c,3,batches),abs=1e-7)


def test_capacity_oracle():
    rng = random.Random(328)
    for n in range(2,8):
        for _ in range(3):
            pu = [rng.randrange(101) for _ in range(n)]
            c = [rng.randrange(1,10) for _ in range(n)]
            loads = [rng.randrange(1,5) for _ in range(n)]
            beta = rng.randrange(1,10)
            a = solve_capacity(pu,c,beta,loads,6,denominator=100,seconds=30)
            b = subset_dp([Q(v,100) for v in pu],c,beta,loads=loads,capacity=6)
            assert a['status'] == 'OPTIMAL'
            assert a['value'] == pytest.approx(float(b.value),abs=1e-7)


def test_invalid_inputs():
    for p,c,b in [([],[],1),([1],[1,2],1),([1.1],[1],1),([.5],[-1],1),([.5],[1],-1)]:
        with pytest.raises(ValueError): solve(p,c,b)
    # A finite exact-rational instance must not fail during float validation.
    p=[Q(4,5),Q(3,10),Q(7,10)]
    c=[10**400,2*10**400,3*10**400]
    assert solve_envelope(p,c,1).value==subset_dp(p,c,1).value
    for loads,cap in [(None,2),([1],2),([1,-1],2),([1,1],0)]:
        with pytest.raises(ValueError):subset_dp([.5,.5],[1,1],1,loads=loads,capacity=cap)
    for x in [[[0,2]],[[1,float('nan')]],[]]:
        with pytest.raises(ValueError):subset_dp([.5,.5],[1,1],1,law='empirical',outcomes=x)


def test_near_coincident_envelopes():
    rng=random.Random(601)
    for n in [10,20,40]:
        for rep in range(5):
            p=[Q(10**12-rng.randrange(1,1000),10**12) for _ in range(n)]
            c=[rng.randrange(100) for _ in range(n)]
            beta=Q(rep,10**12)
            assert solve_envelope(p,c,beta).value==solve(p,c,beta).value


def test_empirical_dp_and_robust_bound():
    import numpy as np
    rng=np.random.default_rng(971)
    for n in range(2,9):
        x=rng.random((30,n))<rng.uniform(.1,.9,n)
        p=x.mean(axis=0).tolist();c=list(range(1,n+1))
        s=subset_dp(p,c,2,law='empirical',outcomes=x)
        from recordbatch import empirical_costs
        assert s.value==pytest.approx(empirical_costs(c,2,s.batches,x).mean())
        assert s.value<=evaluate(p,c,2,s.batches)+1e-8


def test_unbounded_gap_family():
    for m in range(2,9):
        eps=Q(1,m*m)
        p=[Q(1,2)]*m+[eps];c=[1]*m+[3]
        opt=solve_envelope(p,c,0)
        assert opt.value==Q(5,2)+eps*(m-1)
        independent=subset_dp(p,c,0,law='independent')
        assert evaluate(p,c,0,independent.batches)==Q(m,2)+2


def test_zero_setup_exact_and_pointwise_refinement():
    import numpy as np
    from recordbatch import empirical_costs
    rng=random.Random(120726)
    for n in range(1,9):
        x=np.array(list(product([False,True],repeat=n)))
        for rep in range(20):
            p=[Q(rng.randrange(11),10) for _ in range(n)]
            c=[rng.randrange(11) for _ in range(n)]
            raw=solve_envelope(p,c,0)
            refined=refine_zero_setup(p,c,raw)
            fast=solve_zero_setup(p,c)
            oracle=subset_dp(p,c,0)
            assert raw.value==refined.value==fast.value==oracle.value
            assert all(len(b)==1 for b in refined.batches+fast.batches)
            assert np.all(empirical_costs(c,0,refined.batches,x)<=
                          empirical_costs(c,0,raw.batches,x))
            assert evaluate(p,c,0,refined.batches,'independent')<=evaluate(p,c,0,raw.batches,'independent')
            assert solve_policy(p,c,0)==refined


def test_nominal_weight_breaks_record_normal_form():
    p=[Q(1,2)]*3;c=[1]*3
    serial=((0,),(1,),(2,))
    records=[((0,1,2),),((0,),(1,2))]
    for weight in [Q(0),Q(1,2),Q(999,1000)]:
        score=lambda bs:weight*evaluate(p,c,0,bs)+(1-weight)*evaluate(p,c,0,bs,'independent')
        assert all(score(serial)<score(bs) for bs in records)


def test_float_stress_against_exact():
    rng=random.Random(121227)
    for n in [3,6,10]:
        for rep in range(40):
            den=10**rng.choice([2,6,12])
            p=[Q(den-rng.randrange(1,min(den,100)),den) for _ in range(n)]
            c=[Q(rng.randrange(1,100),10**rng.randrange(-0,7)) for _ in range(n)]
            beta=Q(rng.randrange(10),10**rng.randrange(0,13))
            exact=solve_envelope(p,c,beta)
            pf=list(map(float,p));cf=list(map(float,c))
            actual=solve_envelope(pf,cf,float(beta))
            # Recheck the returned schedule on the original exact instance.
            assert float(evaluate(p,c,beta,actual.batches))==pytest.approx(float(exact.value),rel=1e-10,abs=1e-12)
