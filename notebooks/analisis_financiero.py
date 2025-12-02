# %% [markdown]
# # Análisis financiero paso a paso
# 
# Este notebook calcula automáticamente:
# - Fondo de Maniobra (FM)
# - Capital Corriente (CC)
# - Necesidades Operativas de Fondo (NOF)
# - Margen Bruto, Margen de Contribución y Punto Muerto
# - ROA y ROE
# - Descomposición DuPont
# - EVA (Valor Económico Añadido)
#
# Tú SOLO tienes que modificar el diccionario `inputs` en la celda de datos.
# Todo lo demás se recalcula a partir de esos datos.

# %%
from __future__ import annotations

import sys
from math import isfinite
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from finanzasim.financial_calculator import simulate_quarter

# %% [markdown]
# ## 1. Datos de entrada
#
# Aquí defines la "foto" económico-financiera de una empresa.
#
# Variables principales:
# - PN: Patrimonio Neto (recursos propios)
# - PnC: Pasivo no Corriente (deuda a largo plazo)
# - AnC: Activo no Corriente (inmovilizado, inversiones a LP)
# - AC: Activo Corriente (existencias, clientes, tesorería...)
# - PC: Pasivo Corriente (proveedores, deudas CP, HP acreedora...)
# - ACO: Activo Corriente Operativo (existencias, clientes, tesorería mínima…)
# - PCO: Pasivo Corriente Operativo (proveedores, acreedores operativos…)
#
# Cuenta de resultados:
# - Ventas: Importe neto de la cifra de negocios
# - CosteVentas: Coste de las ventas (para margen bruto)
# - CostesVariables: Costes variables totales (ligados al nivel de ventas)
# - CostesFijos: Costes fijos totales
# - BAIT: Beneficio Antes de Intereses e Impuestos (EBIT)
# - BN: Beneficio Neto (después de impuestos)
#
# Otros:
# - Intereses: gastos financieros anuales
# - WACC: coste medio ponderado de capital (como decimal, ej. 0.08 = 8%)
# - Capital_empleado: capital invertido que genera EVA (suele ser Activo operativo neto)

# %%
inputs = {
    # Balance
    "PN": 400_000,            # Patrimonio Neto
    "PnC": 300_000,           # Pasivo no Corriente
    "AnC": 550_000,           # Activo no Corriente
    "AC": 600_000,            # Activo Corriente
    "PC": 350_000,            # Pasivo Corriente

    # Parte operativa (NOF)
    "ACO": 500_000,           # Activo Corriente Operativo
    "PCO": 200_000,           # Pasivo Corriente Operativo

    # Cuenta de resultados
    "Ventas": 1_200_000,
    "CosteVentas": 500_000,   # Coste de las ventas (para margen bruto)
    "CostesVariables": 450_000,
    "CostesFijos": 200_000,
    "BAIT": 150_000,          # Beneficio antes de intereses e impuestos
    "BN": 90_000,             # Beneficio neto

    # Financieros y EVA
    "Intereses": 40_000,
    "WACC": 0.08,             # 8 %
    "Capital_empleado": 800_000,
}
inputs

# %% [markdown]
# ## 2. Cálculo de indicadores clave
# Ajusta `inputs` y vuelve a ejecutar esta celda para recalcular todo.

# %%
def compute_indicators(values: dict) -> pd.DataFrame:
    assets_total = values["AnC"] + values["AC"]
    fm = values["AC"] - values["PC"]
    cc = values["PN"] + values["PnC"] - values["AnC"]
    nof = values["ACO"] - values["PCO"]

    margen_bruto = (values["Ventas"] - values["CosteVentas"]) / values["Ventas"]
    margen_contribucion = (values["Ventas"] - values["CostesVariables"]) / values["Ventas"]
    punto_muerto = values["CostesFijos"] / margen_contribucion if margen_contribucion != 0 else float("nan")

    roa = values["BAIT"] / assets_total
    roe = values["BN"] / values["PN"] if values["PN"] else float("nan")

    margen_neto = values["BN"] / values["Ventas"]
    rotacion_activos = values["Ventas"] / assets_total if assets_total else float("nan")
    apalancamiento = assets_total / values["PN"] if values["PN"] else float("nan")

    # Aproximamos NOPAT con BAIT (sin impuestos explícitos en los inputs)
    nopat = values["BAIT"]
    eva = nopat - values["WACC"] * values["Capital_empleado"]

    rows = [
        ("Fondo de Maniobra (FM)", fm),
        ("Capital Corriente (CC)", cc),
        ("Necesidades Operativas de Fondo (NOF)", nof),
        ("Margen Bruto", margen_bruto),
        ("Margen de Contribución", margen_contribucion),
        ("Punto Muerto (ventas)", punto_muerto),
        ("ROA", roa),
        ("ROE", roe),
        ("Margen Neto", margen_neto),
        ("Rotación de Activos", rotacion_activos),
        ("Apalancamiento Financiero", apalancamiento),
        ("EVA", eva),
    ]
    return pd.DataFrame(rows, columns=["Indicador", "Valor"])


indicators_df = compute_indicators(inputs)
indicators_df

# %% [markdown]
# ### Descomposición DuPont
# - **ROE** = Margen Neto × Rotación de Activos × Apalancamiento Financiero
# - Modifica los datos de `inputs` y vuelve a ejecutar para ver el efecto.

# %%
assets_total = inputs["AnC"] + inputs["AC"]
margin = inputs["BN"] / inputs["Ventas"]
turnover = inputs["Ventas"] / assets_total
leverage = assets_total / inputs["PN"]
dupont_df = pd.DataFrame(
    {
        "Factor": ["Margen Neto", "Rotación de Activos", "Apalancamiento"],
        "Valor": [margin, turnover, leverage],
    }
)
dupont_df

# %% [markdown]
# ### Gráficas de ratios y EVA
# Usa estas visualizaciones rápidas para comparar liquidez, rentabilidad y creación de valor.

# %%
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

indicators_plot = indicators_df[indicators_df["Indicador"].isin(["ROA", "ROE", "Margen Neto", "Rotación de Activos"])]
axes[0].bar(indicators_plot["Indicador"], indicators_plot["Valor"], color="#4B89DC")
axes[0].set_title("Rentabilidad y eficiencia")
axes[0].tick_params(axis="x", rotation=20)
axes[0].grid(axis="y", linestyle="--", alpha=0.4)

axes[1].bar(["EVA"], [indicators_df.loc[indicators_df["Indicador"] == "EVA", "Valor"].iloc[0]], color="#E67E22")
axes[1].set_title("Valor Económico Añadido")
axes[1].grid(axis="y", linestyle="--", alpha=0.4)

fig.tight_layout()

# %% [markdown]
# ## 3. Escenarios listos para jugar (20 casos)
# Esta sección crea 20 situaciones con combinaciones de **producción**, **precio** e **inversión en marketing**.
# Cada escenario se evalúa con el motor `simulate_quarter` del juego.
#
# - Ajusta la lista `SCENARIOS` para explorar decisiones distintas.
# - Ejecuta la celda para recalcular ingresos, utilidad neta y liquidez de cada caso.
# - Al final se generan gráficas para comparar resultados.

# %%
BASE_STATE = {
    "quarter": 0,
    "cash": 50_000,
    "inventory": 1_000,
    "equity": 50_000,
}

SCENARIOS = [
    {"production": 1200, "price": 55, "marketing": 0},
    {"production": 1400, "price": 52, "marketing": 1000},
    {"production": 1500, "price": 50, "marketing": 2000},
    {"production": 1600, "price": 48, "marketing": 3000},
    {"production": 1700, "price": 46, "marketing": 4000},
    {"production": 1250, "price": 60, "marketing": 1500},
    {"production": 1350, "price": 58, "marketing": 2500},
    {"production": 1450, "price": 56, "marketing": 3500},
    {"production": 1550, "price": 54, "marketing": 4500},
    {"production": 1650, "price": 52, "marketing": 5500},
    {"production": 1750, "price": 50, "marketing": 6500},
    {"production": 1850, "price": 49, "marketing": 7500},
    {"production": 1950, "price": 47, "marketing": 8500},
    {"production": 2050, "price": 45, "marketing": 9500},
    {"production": 2150, "price": 44, "marketing": 10_500},
    {"production": 1250, "price": 53, "marketing": 500},
    {"production": 1350, "price": 51, "marketing": 1500},
    {"production": 1450, "price": 49, "marketing": 2500},
    {"production": 1550, "price": 47, "marketing": 3500},
    {"production": 1650, "price": 45, "marketing": 4500},
]
assert len(SCENARIOS) == 20, "Debes mantener 20 casos."

scenario_rows = []
for idx, decision in enumerate(SCENARIOS, start=1):
    result = simulate_quarter(BASE_STATE, decision)
    liquidity = result.liquidity_ratio if isfinite(result.liquidity_ratio) else None
    scenario_rows.append(
        {
            "Escenario": f"Caso {idx}",
            "Producción": decision["production"],
            "Precio": decision["price"],
            "Marketing": decision["marketing"],
            "Ingresos": result.revenue,
            "Utilidad Neta": result.net_income,
            "Liquidez": liquidity,
            "Unidades Vendidas": result.units_sold,
        }
    )

scenarios_df = pd.DataFrame(scenario_rows)
scenarios_df

# %% [markdown]
# ### Visualiza los 20 casos
# - **Ingresos vs. Utilidad Neta**: detecta qué estrategias generan más ventas y qué tan rentables son.
# - **Liquidez**: observa cómo varía la razón circulante con cada combinación.

# %%
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

scenarios_df.plot(
    x="Escenario",
    y=["Ingresos", "Utilidad Neta"],
    kind="bar",
    ax=axes[0],
    title="Ingresos y Utilidad Neta por escenario",
)
axes[0].tick_params(axis="x", rotation=45)
axes[0].grid(axis="y", linestyle="--", alpha=0.4)

scenarios_df.plot(
    x="Escenario",
    y="Liquidez",
    kind="bar",
    color="#27AE60",
    ax=axes[1],
    title="Razón circulante (Liquidez)",
)
axes[1].tick_params(axis="x", rotation=45)
axes[1].grid(axis="y", linestyle="--", alpha=0.4)

fig.tight_layout()

# %% [markdown]
# ## 4. Dashboard trimestral estilo KPI
# Genera un panel con 6 gráficas para seguir la evolución por trimestre de las métricas clave
# inspiradas en el ejemplo proporcionado (ingresos, retorno, flujo de caja, precio,
# EBIT/gross profit y ratio Deuda/Patrimonio).

# %%
TIMELINE_DECISIONS = [
    {"production": 1400, "price": 55, "marketing": 2000},
    {"production": 1500, "price": 53, "marketing": 2500},
    {"production": 1600, "price": 51, "marketing": 3000},
    {"production": 1650, "price": 49, "marketing": 3200},
]


def simulate_timeline(base_state: dict, decisions: list[dict]) -> list[FinancialSnapshot]:
    """Simula varios trimestres consecutivos acumulando estados."""

    snapshots: list[FinancialSnapshot] = []
    state = base_state.copy()
    for decision in decisions:
        result = simulate_quarter(state, decision)
        snapshots.append(result)
        state = {
            "quarter": result.quarter,
            "cash": result.cash,
            "inventory": result.inventory,
            "equity": result.equity,
        }
    return snapshots


timeline_snaps = simulate_timeline(BASE_STATE, TIMELINE_DECISIONS)
timeline_df = pd.DataFrame(
    {
        "Quarter": [f"Q{snap.quarter}" for snap in timeline_snaps],
        "Revenue": [snap.revenue for snap in timeline_snaps],
        "ROI": [snap.net_income / snap.equity if snap.equity else 0 for snap in timeline_snaps],
        "CashFlow": [snap.cash - (timeline_snaps[idx - 1].cash if idx else BASE_STATE["cash"]) for idx, snap in enumerate(timeline_snaps)],
        "Price": [snap.price for snap in timeline_snaps],
        "EBIT": [snap.ebit for snap in timeline_snaps],
        "GrossProfit": [snap.gross_profit for snap in timeline_snaps],
        "DE": [
            (snap.debt / snap.equity) if snap.equity else 0
            for snap in timeline_snaps
        ],
    }
)

palette = ["#63C9F3", "#4DB3C8", "#E9B44C", "#EF767A"]

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# Revenue
axes[0, 0].bar(timeline_df["Quarter"], timeline_df["Revenue"], color=palette)
axes[0, 0].set_title("Revenue")
axes[0, 0].grid(axis="y", linestyle="--", alpha=0.35)

# ROI
axes[0, 1].bar(timeline_df["Quarter"], timeline_df["ROI"], color="orange")
axes[0, 1].set_title("Return on Investment")
axes[0, 1].grid(axis="y", linestyle="--", alpha=0.35)

# Cash Flow
axes[0, 2].bar(timeline_df["Quarter"], timeline_df["CashFlow"], color="#5ac4a7")
axes[0, 2].set_title("Cash Flow")
axes[0, 2].grid(axis="y", linestyle="--", alpha=0.35)

# Price trend
axes[1, 0].plot(timeline_df["Quarter"], timeline_df["Price"], marker="o", color="#5564D8")
axes[1, 0].set_title("Price")
axes[1, 0].grid(axis="y", linestyle="--", alpha=0.35)

# EBIT / Gross Profit
axes[1, 1].bar(timeline_df["Quarter"], timeline_df["EBIT"], label="EBIT", color="#63C9F3")
axes[1, 1].bar(timeline_df["Quarter"], timeline_df["GrossProfit"], label="Gross Profit", color="#FFB347", alpha=0.8)
axes[1, 1].set_title("EBIT / Gross Profit")
axes[1, 1].legend()
axes[1, 1].grid(axis="y", linestyle="--", alpha=0.35)

# D/E ratio
axes[1, 2].plot(timeline_df["Quarter"], timeline_df["DE"], marker="s", color="#A26769")
axes[1, 2].set_title("D/E Ratio")
axes[1, 2].grid(axis="y", linestyle="--", alpha=0.35)

fig.suptitle("Dashboard trimestral de métricas financieras", fontsize=16, y=0.98)
fig.tight_layout(rect=[0, 0, 1, 0.96])

# %% [markdown]
# ✅ Con estas celdas puedes iterar decisiones, recalcular automáticamente y observar su impacto financiero con gráficas listas para presentar.
