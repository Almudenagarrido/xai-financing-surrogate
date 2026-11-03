from . import rwanda_inputs as CASE
from .model import make_capex_data, make_k1_k2

N_PERIODS = CASE.N_PERIODS


def fixed_params() -> dict:
    demand_base, k1, k2 = make_k1_k2(CASE.TECHNO, N_PERIODS)

    return {
        'capex_total':          make_capex_data(CASE.TECHNO, N_PERIODS),
        'demand_base':          demand_base,
        'K1':                   k1,
        'K2':                   k2,
        'cost_upstream_data':   dict(enumerate(CASE.UPSTREAM)),
        'ntlosses_data':        {t: v / 100 for t, v in enumerate(CASE.NTL)},
        'days_receivable_data': dict(enumerate(CASE.DAYS_REC)),
        'days_payable_data':    dict(enumerate(CASE.DAYS_PAY)),
        'TAXRATE':              CASE.TAX_RATE / 100,
        'N_PERIODS':            N_PERIODS,
    }


def tariff_path(tariff_y1: float) -> dict:
    growth = 1 + CASE.INFLATION / 100
    return {t: tariff_y1 * growth ** t for t in range(N_PERIODS)}