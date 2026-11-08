import time
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from pyomo.environ import value
from joblib import Parallel, delayed

from xai_financing_surrogate.model import run_model
from xai_financing_surrogate.scenario import build_params
from xai_financing_surrogate.sampling import SPACE_UNIFORM, sample_inputs


BIG_M = 1e4
GUARDED_VARS = ['profit', 'loss', 'lt_subsidies', 'service_margin', 'taxable', 'cum']
N_SAMPLES = 6000
SEED = 42
DATA_DIR = Path(__file__).resolve().parents[1] / 'data'


def solve_one(inputs: dict) -> dict:
    """Solve the Pyomo model (ground-truth function) for one input combination."""
    start = time.perf_counter()
    status, debt, model = run_model(build_params(**inputs))
    elapsed = time.perf_counter() - start

    outputs = {'status': status, 'total_debt': debt, 'max_bigm_share': None, 'total_grants': None, 'total_lt_subsidies': None,         'total_service_margin': None, 'equity': None, 'solve_time': elapsed}

    if status == 'optimal':
        # Check M validity
        outputs['max_bigm_share'] = max(
            value(getattr(model, var)[t]) for var in GUARDED_VARS for t in model.T
        ) / BIG_M

        outputs['total_grants'] = sum(value(model.grants[t]) for t in model.T)
        outputs['total_lt_subsidies'] = sum(value(model.lt_subsidies[t]) for t in model.T)
        outputs['total_service_margin'] = sum(value(model.service_margin[t]) for t in model.T)
        outputs['equity'] = sum(value(model.equity[t]) for t in model.T)

    return outputs


if __name__ == '__main__':
    # Latin Hypercube design over the full negotiable range (uniform space)
    inputs = sample_inputs(SPACE_UNIFORM, N_SAMPLES, seed=SEED)

    # Independent Pyomo solves, spread over all CPU cores
    rows = inputs.to_dict('records')
    results = list(tqdm(
        Parallel(n_jobs=-1, return_as='generator')(delayed(solve_one)(row) for row in rows),
        total=len(rows), desc='Solving Pyomo',
    ))

    dataset = pd.concat([inputs, pd.DataFrame(results)], axis=1)
    money_cols = ['total_debt', 'total_grants', 'total_lt_subsidies', 'total_service_margin', 'equity']
    dataset[money_cols] = dataset[money_cols].where(dataset[money_cols] >= 1e-6, 0.0)

    print(f"Non-optimal samples: {(dataset['status'] != 'optimal').sum()} / {len(dataset)}")
    print(f"Max share of big-M reached: {dataset['max_bigm_share'].max():.1%}")
    print(f"Samples with zero debt: {(dataset['total_debt'] == 0).sum()}")
    print(dataset['total_debt'].describe().round(2))

    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / f'dataset_uniform_n{N_SAMPLES}_seed{SEED}.csv'
    dataset.to_csv(out_path, index=False)
    print(f"Saved {out_path}")