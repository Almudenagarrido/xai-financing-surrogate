"""Sanity checks on the Pyomo model before generating the synthetic dataset.

Two questions to be answered:
  1. Is the big-M large enough? On/off logic (profit vs. loss, subsidy vs. margin, taxed vs. carried-forward losses) is modelled as x <= M * binary. 
  2. How long does one solve take? Almost all of the run time is the MILP solve itself and this cost decides how many samples the dataset can afford.
"""

import os
import statistics
import time

from pyomo.environ import value

from xai_financing_surrogate.model import run_model
from xai_financing_surrogate.scenario import build_params

BIG_M = 1e4 
WARN_SHARE = 0.9

GUARDED_VARS = ['profit', 'loss', 'lt_subsidies', 'service_margin', 'taxable', 'cum']

CASES = {
    'TFG baseline': dict(
        pct_debt=0.8, cost_debt=0.08, equity_premium=0.08, grace_period=5,
        amortization_period=25, pct_grants=0.13, years_realisation=5, tariff_y1=0.15),
    'harsh terms': dict(
        pct_debt=0.9, cost_debt=0.15, equity_premium=0.15, grace_period=0,
        amortization_period=15, pct_grants=0.0, years_realisation=1, tariff_y1=0.08),
    'generous terms': dict(
        pct_debt=0.3, cost_debt=0.02, equity_premium=0.01, grace_period=5,
        amortization_period=25, pct_grants=0.5, years_realisation=5, tariff_y1=0.25),
    'high tariff, no grants': dict(
        pct_debt=0.9, cost_debt=0.15, equity_premium=0.15, grace_period=0,
        amortization_period=15, pct_grants=0.0, years_realisation=1, tariff_y1=0.25),
    'low tariff, max grants': dict(
        pct_debt=0.3, cost_debt=0.02, equity_premium=0.01, grace_period=5,
        amortization_period=25, pct_grants=0.5, years_realisation=5, tariff_y1=0.08),
}

solve_times = []
for name, case in CASES.items():
    start = time.perf_counter()
    status, debt, model = run_model(build_params(**case))
    solve_times.append(time.perf_counter() - start)

    print(f"\n{name}: status={status}, total debt={debt}, time={solve_times[-1]:.2f} s")
    if status != 'optimal':
        continue

    for var_name in GUARDED_VARS:
        var = getattr(model, var_name)
        peak = max(value(var[t]) for t in model.T)
        flag = '  <-- close to M!' if peak >= WARN_SHARE * BIG_M else ''
        print(f"  {var_name:<15} peak {peak:9.2f}  ({100 * peak / BIG_M:5.1f}% of M){flag}")

# Independent runs, dataset can be solved in parallel accross cores
mean_t = statistics.mean(solve_times)
n_cores = os.cpu_count()
print(f"\nMean time per solve: {mean_t:.2f} s | cores available: {n_cores}")
for n in (1000, 3000, 5000):
    print(f"  {n:>5} samples -> ~{n * mean_t / 60:.1f} min serial, "
          f"~{n * mean_t / n_cores / 60:.1f} min in parallel")