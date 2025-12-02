from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConstants:
    cost_per_unit: float = 25
    fixed_opex: float = 10_000
    tax_rate: float = 0.20
    base_demand: float = 1_200
    marketing_effect_per_dollar: float = 0.1
    price_elasticity: float = 20
    reference_price: float = 50


SIMULATION_CONSTANTS = SimulationConstants()
