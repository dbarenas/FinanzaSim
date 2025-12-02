import math
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from finanzasim.financial_calculator import simulate_quarter


base_state = {"quarter": 0, "cash": 50_000, "inventory": 1_000, "equity": 50_000, "debt": 0}


def test_simulate_quarter_profitable_case():
    decision = {"production": 1_500, "price": 55, "marketing": 2_000}
    result = simulate_quarter(base_state, decision)

    assert result.quarter == 1
    assert result.units_sold == 1_300
    assert result.revenue == 71_500
    assert result.cogs == 32_500
    assert result.operating_expenses == 12_000
    assert result.ebit == 27_000
    assert result.taxes == 5_400
    assert result.net_income == 21_600
    assert result.cash == 72_000
    assert result.inventory == 1_200
    assert result.debt == 0
    assert result.equity == 71_600
    assert math.isfinite(result.net_margin)
    assert 0.3 < result.net_margin < 0.31


def test_simulate_quarter_short_term_debt():
    decision = {"production": 0, "price": 30, "marketing": 0}
    start = {"quarter": 0, "cash": 1_000, "inventory": 0, "equity": 1_000, "debt": 0}
    result = simulate_quarter(start, decision)

    assert result.quarter == 1
    assert result.units_sold == 0
    assert result.revenue == 0
    assert result.net_income == -10_000
    assert result.cash == 0
    assert result.debt == 9_000
    assert result.equity == -9_000
    assert result.liquidity_ratio == 0
    assert result.net_margin == 0
