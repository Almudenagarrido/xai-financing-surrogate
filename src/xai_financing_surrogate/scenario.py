from . import rwanda_inputs as rw
from .model import make_capex_data, make_k1_k2

SCENARIO = 'Electricity & E-Cooking'
FUEL = 'Electricity'
N_PERIODS = len(rw.TARIFFS[FUEL])
YEARS_REALISATION = 8


def fixed_params() -> dict:
    tech_dict = rw.TECHNO_ELEC[SCENARIO]
    fuel_fin = rw.FUEL_FIN[FUEL]
    demand_base, k1, k2 = make_k1_k2(tech_dict, N_PERIODS)

    return {
        'capex_total':          make_capex_data(tech_dict, N_PERIODS),
        'demand_base':          demand_base,
        'K1':                   k1,
        'K2':                   k2,
        'cost_upstream_data':   dict(enumerate(rw.UPSTREAMS[FUEL])),
        'ntlosses_data':        {t: v / 100 for t, v in enumerate(fuel_fin['NTL'])},
        'days_receivable_data': dict(enumerate(fuel_fin['DAYS_REC'])),
        'days_payable_data':    dict(enumerate(fuel_fin['DAYS_PAY'])),
        'TAXRATE':              rw.TAX_RATE / 100,
        'years_realisation':    YEARS_REALISATION,
        'N_PERIODS':            N_PERIODS,
    }


def tariff_path(tariff_y1: float) -> dict:
    growth = 1 + rw.INFLATION / 100
    return {t: tariff_y1 * growth ** t for t in range(N_PERIODS)}