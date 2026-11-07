import time
import pandas as pd
from pyomo.environ import value
from joblib import Parallel, delayed

from xai_financing_surrogate.model import run_model
from xai_financing_surrogate.scenario import build_params
from xai_financing_surrogate.sampling import SPACE_UNIFORM, sample_inputs


BIG_M = 1e4
GUARDED_VARS = ['profit', 'loss', 'lt_subsidies', 'service_margin', 'taxable', 'cum']
N_SAMPLES = 100
SEED = 42


def solve_one(inputs: dict) -> dict:
    """Solve the Pyomo model (the ground-truth function) for one input combination."""
    start = time.perf_counter()
    status, debt, model = run_model(build_params(**inputs))
    elapsed = time.perf_counter() - start

    max_bigm_share = None
    if status == 'optimal':
        max_bigm_share = max(
            value(getattr(model, var)[t]) for var in GUARDED_VARS for t in model.T
        ) / BIG_M

    return {'status': status, 'total_debt': debt,
            'max_bigm_share': max_bigm_share, 'solve_time': elapsed}


if __name__ == '__main__':
    # Latin Hypercube design over the full negotiable range (uniform space)
    inputs = sample_inputs(SPACE_UNIFORM, N_SAMPLES, seed=SEED)

    # Independent Pyomo solves, spread over all CPU cores
    results = Parallel(n_jobs=-1, verbose=5)(
        delayed(solve_one)(row) for row in inputs.to_dict('records')
    )

    dataset = pd.concat([inputs, pd.DataFrame(results)], axis=1)
    print(dataset.head())