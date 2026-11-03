"""Rwanda case study inputs (Electricity & E-Cooking)
"""

N_PERIODS = 12  # planning horizon, 2023-2034

# ----------------- COUNTRY-LEVEL INPUTS ----------------------
TAX_RATE  = 28
INFLATION = 5

NTL      = [5]*12   # expected non-technical losses (%)
DAYS_REC = [30]*12  # Receivables, days of revenues
DAYS_PAY = [30]*12  # Payables, days of OPEX costs

# ----------------- TECHNO-ECONOMIC INPUTS ----------------------
TECHNO = {
    'GRID': {
        'Demand':             [1473.6, 1616.8, 1793.2, 1954.5, 2101.6, 2235.1, 2355.9, 2518.5, 2659.5, 2786.4, 2900, 3001],
        'CAPEX - Growth':     [257.3,  324.6,  321.4,  318.2, 315, 311.8, 382, 451.1, 446.6, 442.1, 437.7, 290.8],
        'CAPEX - Maintenance':[0]*12,
        'OPEX':               [48.2,   54.6,   62.2,   69.6, 77, 84.1, 91.1, 102.2, 112.7, 123, 133.1, 143],
        'D&A':                35,
    },
    'OFF-GRID': {
        'Demand':             [368.4, 379.3, 393.6, 400.3, 400.3, 394.4, 383.5, 376.3, 362.7, 344.4, 322.2, 296.8],
        'CAPEX - Growth':     [39.5,  50.3, 49.8, 49.3, 48.8, 48.4, 15.4, -17.1, -16.9, -16.8, -16.6, -1.7],
        'CAPEX - Maintenance':[0]*12,
        'OPEX':               [56.1,  64.7, 74.9, 84.8, 94.5, 104, 113.4, 111.6, 105.1, 98.8, 92.6, 86.4],
        'D&A':                25,
    },
}

UPSTREAM = [0]*12

# Baseline tariff (reference only)
TARIFF_BASELINE = [0.15, 0.16, 0.17, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.26]