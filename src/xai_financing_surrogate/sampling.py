"""Sampling space of the negotiation parameters and Latin Hypercube design."""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import qmc


def triangular(low: float, mode: float, high: float):
    """Continuous triangular distribution from (min, most likely, max)."""
    return stats.triang(c=(mode - low) / (high - low), loc=low, scale=high - low)


def discrete_triangular(low: int, mode: int, high: int):
    """Triangular distribution over whole years, peaking at the most likely one."""
    years = np.arange(low, high + 1)
    weights = np.minimum((years - low + 1) / (mode - low + 1), (high - years + 1) / (high - mode + 1))
    return stats.rv_discrete(values=(years, weights / weights.sum()))()


# Full negotiable range: uniform distributions, the maximum-entropy choice when
# only the bounds of each input are known
SPACE_UNIFORM = {
    'pct_debt':            stats.uniform(loc=0.30, scale=0.90 - 0.30),  # 0.30 - 0.90
    'cost_debt':           stats.uniform(loc=0.02, scale=0.15 - 0.02),  # 2 % - 15 %
    'equity_premium':      stats.uniform(loc=0.01, scale=0.15 - 0.01),  # 1 - 15 points
    'grace_period':        stats.randint(0, 5 + 1),                     # 0 - 5 years
    'amortization_period': stats.randint(15, 25 + 1),                   # 15 - 25 years
    'pct_grants':          stats.uniform(loc=0.00, scale=0.50 - 0.00),  # 0 - 0.50
    'years_realisation':   stats.randint(1, 5 + 1),                     # 1 - 5 years
    'tariff_y1':           stats.uniform(loc=0.08, scale=0.25 - 0.08),  # 0.08 - 0.25
}

# Typical negotiations: triangular distributions (expert elicitation: min, mode, max)
SPACE_TRIANGULAR = {
    'pct_debt':            triangular(0.30, 0.80, 0.90),
    'cost_debt':           triangular(0.02, 0.08, 0.15),
    'equity_premium':      triangular(0.01, 0.08, 0.15),
    'grace_period':        discrete_triangular(0, 2, 5),
    'amortization_period': discrete_triangular(15, 20, 25),
    'pct_grants':          triangular(0.00, 0.20, 0.50),
    'years_realisation':   discrete_triangular(1, 3, 5),
    'tariff_y1':           triangular(0.08, 0.15, 0.25),
}


def sample_inputs(space: dict, n: int, seed: int = 42) -> pd.DataFrame:
    """Draw n Latin Hypercube samples from the given sampling space."""
    # 1. Latin Hypercube Sampling: n points in the unit cube [0, 1)^d, with
    #    exactly one point in each of the n equal strata of every input
    sampler = qmc.LatinHypercube(d=len(space), rng=np.random.default_rng(seed))
    unit = sampler.random(n)

    # 2. Inverse transform sampling: each input's inverse CDF (ppf) maps the
    #    stratified uniform values onto its own distribution
    samples = {name: dist.ppf(unit[:, j]) for j, (name, dist) in enumerate(space.items())}
    df = pd.DataFrame(samples)

    # ppf returns floats even for discrete distributions; years must be integers
    int_cols = [name for name, dist in space.items() if isinstance(dist.dist, stats.rv_discrete)]
    return df.astype({col: int for col in int_cols})