from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .constants import SIMULATION_CONSTANTS


@dataclass
class Decision:
    production: float
    price: float
    marketing: float


@dataclass
class FinancialSnapshot:
    quarter: int
    cash: float
    inventory: float
    equity: float
    debt: float = 0.0
    revenue: float = 0.0
    cogs: float = 0.0
    gross_profit: float = 0.0
    operating_expenses: float = 0.0
    ebit: float = 0.0
    taxes: float = 0.0
    net_income: float = 0.0
    units_sold: float = 0.0
    liquidity_ratio: float = 0.0
    net_margin: float = 0.0
    price: float = 0.0
    marketing: float = 0.0
    production: float = 0.0


def calculate_demand(decision: Decision) -> float:
    price_effect = (SIMULATION_CONSTANTS.reference_price - decision.price) * SIMULATION_CONSTANTS.price_elasticity
    marketing_effect = decision.marketing * SIMULATION_CONSTANTS.marketing_effect_per_dollar
    raw_demand = SIMULATION_CONSTANTS.base_demand + price_effect + marketing_effect
    return max(0, raw_demand)


def calculate_ratios(financial_snapshot: FinancialSnapshot) -> Tuple[float, float]:
    current_assets = financial_snapshot.cash + financial_snapshot.inventory
    current_liabilities = financial_snapshot.debt
    liquidity_ratio = float("inf") if current_liabilities == 0 else current_assets / current_liabilities
    net_margin = 0 if financial_snapshot.revenue == 0 else financial_snapshot.net_income / financial_snapshot.revenue
    return liquidity_ratio, net_margin


def simulate_quarter(previous: Dict, decision: Dict) -> FinancialSnapshot:
    decision_obj = Decision(**decision)
    demand = calculate_demand(decision_obj)
    available_units = decision_obj.production + previous["inventory"]
    units_sold = min(demand, available_units)

    revenue = units_sold * decision_obj.price
    cogs = units_sold * SIMULATION_CONSTANTS.cost_per_unit
    gross_profit = revenue - cogs

    operating_expenses = SIMULATION_CONSTANTS.fixed_opex + decision_obj.marketing
    ebit = gross_profit - operating_expenses
    taxes = max(0, ebit * SIMULATION_CONSTANTS.tax_rate)
    net_income = ebit - taxes

    cash_change = revenue - (decision_obj.production * SIMULATION_CONSTANTS.cost_per_unit) - operating_expenses
    new_cash = previous["cash"] + cash_change
    debt = max(0, -new_cash)
    adjusted_cash = max(0, new_cash)
    new_inventory = previous["inventory"] + decision_obj.production - units_sold
    new_equity = previous["equity"] + net_income

    snapshot = FinancialSnapshot(
        quarter=previous["quarter"] + 1,
        revenue=revenue,
        cogs=cogs,
        gross_profit=gross_profit,
        operating_expenses=operating_expenses,
        ebit=ebit,
        taxes=taxes,
        net_income=net_income,
        cash=adjusted_cash,
        inventory=new_inventory,
        debt=debt,
        equity=new_equity,
        units_sold=units_sold,
        production=decision_obj.production,
        price=decision_obj.price,
        marketing=decision_obj.marketing,
    )

    liquidity_ratio, net_margin = calculate_ratios(snapshot)
    snapshot.liquidity_ratio = liquidity_ratio
    snapshot.net_margin = net_margin
    return snapshot
