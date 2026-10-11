"""Exact integer CP-SAT model for marginally robust capacity-limited batches."""
from ortools.sat.python import cp_model
from recordbatch import Solution, evaluate


def solve_capacity(p_units, c, beta, loads, capacity, denominator=1000, seconds=30):
    n, P = len(c), denominator
    if not n or len(p_units) != n or len(loads) != n:
        raise ValueError('array sizes')
    if any(not isinstance(v, int) or not 0 <= v <= P for v in p_units):
        raise ValueError('integer probabilities required')
    if any(not isinstance(v, int) or v < 0 for v in [*c, beta, *loads, capacity]) or capacity <= 0:
        raise ValueError('integer nonnegative costs and positive capacity required')
    model = cp_model.CpModel()
    x = [[model.new_bool_var(f'x_{i}_{b}') for b in range(n)] for i in range(n)]
    active = [model.new_bool_var(f'a_{b}') for b in range(n)]
    s = [model.new_int_var(0, P, f's_{b}') for b in range(n+1)]
    model.add(s[0] == P)
    for i in range(n):
        model.add_exactly_one(x[i])
    objective = []
    for b in range(n):
        count = sum(x[i][b] for i in range(n))
        model.add(count >= active[b])
        model.add(count <= n*active[b])
        if b:
            model.add(active[b] <= active[b-1])
        model.add(sum(loads[i]*x[i][b] for i in range(n)) <= capacity)
        # Each expression equals p_i if assigned here, and P otherwise.
        model.add_min_equality(s[b+1], [s[b]] + [P-(P-p_units[i])*x[i][b] for i in range(n)])
        charge = model.new_int_var(0, beta+sum(c), f'charge_{b}')
        model.add(charge == beta*active[b]+sum(c[i]*x[i][b] for i in range(n)))
        z = model.new_int_var(0, P*(beta+sum(c)), f'z_{b}')
        model.add_multiplication_equality(z, [s[b], charge])
        objective.append(z)
    model.minimize(sum(objective))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 1720406
    status = solver.solve(model)
    result = dict(status=solver.status_name(status), bound=solver.best_objective_bound/P,
                  seconds=solver.wall_time, branches=solver.num_branches)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        batches = tuple(tuple(i for i in range(n) if solver.value(x[i][b]))
                        for b in range(n) if solver.value(active[b]))
        result.update(value=solver.objective_value/P, batches=batches)
        check = evaluate([v/P for v in p_units], c, beta, batches)
        assert abs(check-result['value']) < 1e-6
    return result
