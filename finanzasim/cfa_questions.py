from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class QuestionOption:
    id: str
    text: str
    impact: Dict[str, float]


@dataclass(frozen=True)
class Question:
    id: str
    prompt: str
    options: Sequence[QuestionOption]


def apply_option_impact(decision: Dict[str, float], option: QuestionOption) -> Dict[str, float]:
    """Return a new decision dict adjusted by the option's impact factors."""
    production = max(
        0.0,
        decision.get("production", 0.0) * option.impact.get("production_multiplier", 1.0)
        + option.impact.get("production_delta", 0.0),
    )
    price = max(
        0.0,
        decision.get("price", 0.0) * option.impact.get("price_multiplier", 1.0)
        + option.impact.get("price_delta", 0.0),
    )
    marketing = max(
        0.0,
        decision.get("marketing", 0.0) * option.impact.get("marketing_multiplier", 1.0)
        + option.impact.get("marketing_delta", 0.0),
    )
    return {
        "production": production,
        "price": price,
        "marketing": marketing,
    }


def pick_random_question(exclude_ids: Sequence[str] | None = None) -> Question:
    available = [q for q in QUESTION_BANK if not exclude_ids or q.id not in exclude_ids]
    if not available:
        available = list(QUESTION_BANK)
    return random.choice(available)


QUESTION_BANK: List[Question] = [
    Question(
        id="q01",
        prompt="Un comité de riesgos propone cubrir la exposición cambiaria elevando el precio en 2%. ¿Cómo respondes?",
        options=[
            QuestionOption("A", "Aceptas el aumento para proteger margen", {"price_delta": 1.0}),
            QuestionOption("B", "Mantienes precio y refuerzas marketing para ganar cuota", {"marketing_multiplier": 1.25}),
            QuestionOption("C", "Reducir producción para priorizar liquidez", {"production_multiplier": 0.9}),
        ],
    ),
    Question(
        id="q02",
        prompt="El equipo de ventas pide un descuento táctico del 5% por trimestre para cerrar contratos grandes.",
        options=[
            QuestionOption("A", "Aprobado: descuento completo", {"price_multiplier": 0.95}),
            QuestionOption("B", "Descuento parcial y más volumen", {"price_multiplier": 0.97, "production_multiplier": 1.05}),
            QuestionOption("C", "Sin descuento, en su lugar branding", {"marketing_multiplier": 1.2}),
        ],
    ),
    Question(
        id="q03",
        prompt="Finanzas advierte sobre capital de trabajo tensionado. Se sugiere recortar marketing un 20%.",
        options=[
            QuestionOption("A", "Aceptas el recorte para liberar caja", {"marketing_multiplier": 0.8}),
            QuestionOption("B", "Mantienes marketing pero bajas producción", {"production_multiplier": 0.9}),
            QuestionOption("C", "Contrarrestas con subida de precio", {"price_delta": 2.0}),
        ],
    ),
    Question(
        id="q04",
        prompt="Un proveedor ofrece pago anticipado con 3% de descuento en costo unitario si produces más.",
        options=[
            QuestionOption("A", "Incrementas producción para capturar descuento", {"production_multiplier": 1.15}),
            QuestionOption("B", "Mantienes producción y reservas liquidez", {"production_multiplier": 1.0}),
            QuestionOption("C", "Bajas precio para rotar inventario", {"price_multiplier": 0.98}),
        ],
    ),
    Question(
        id="q05",
        prompt="Marketing propone campaña digital adicional. Requiere +$500 y promete +8% en demanda.",
        options=[
            QuestionOption("A", "Apruebas la campaña completa", {"marketing_delta": 500.0}),
            QuestionOption("B", "Aprobación parcial y subes precio 1%", {"marketing_delta": 250.0, "price_multiplier": 1.01}),
            QuestionOption("C", "Rechazas y reasignas a producción", {"production_multiplier": 1.05}),
        ],
    ),
    Question(
        id="q06",
        prompt="Se detecta obsolescencia en inventario. Se propone rebaja temporal del 3% en precio.",
        options=[
            QuestionOption("A", "Aplicar rebaja total", {"price_multiplier": 0.97}),
            QuestionOption("B", "Rebaja parcial y más marketing de liquidación", {"price_multiplier": 0.985, "marketing_multiplier": 1.15}),
            QuestionOption("C", "Sin rebaja, ajustas producción a la baja", {"production_multiplier": 0.9}),
        ],
    ),
    Question(
        id="q07",
        prompt="El director comercial sugiere producir 10% más para evitar roturas de stock en Q4.",
        options=[
            QuestionOption("A", "Sigues la recomendación", {"production_multiplier": 1.1}),
            QuestionOption("B", "Producción neutra y refuerzo de marketing", {"marketing_multiplier": 1.1}),
            QuestionOption("C", "Moderación: +5% producción y precio +1", {"production_multiplier": 1.05, "price_delta": 1.0}),
        ],
    ),
    Question(
        id="q08",
        prompt="Una auditoría ESG sugiere invertir en eficiencia, reduciendo OPEX futuro pero elevando marketing ahora.",
        options=[
            QuestionOption("A", "Incrementas marketing para visibilidad ESG", {"marketing_multiplier": 1.3}),
            QuestionOption("B", "Subes precio 2% para financiar la iniciativa", {"price_multiplier": 1.02}),
            QuestionOption("C", "Aplazas la iniciativa y mantienes estructura actual", {}),
        ],
    ),
    Question(
        id="q09",
        prompt="Competencia lanza producto sustituto 4% más barato. ¿Cuál es tu respuesta?",
        options=[
            QuestionOption("A", "Igualas el precio y subes marketing", {"price_multiplier": 0.96, "marketing_multiplier": 1.2}),
            QuestionOption("B", "Mantienes precio, refuerzas valor percibido", {"marketing_multiplier": 1.1}),
            QuestionOption("C", "Reduces producción para evitar excedentes", {"production_multiplier": 0.92}),
        ],
    ),
    Question(
        id="q10",
        prompt="El CFO sugiere priorizar flujo de caja, proponiendo bajar marketing 10% y precio +1%.",
        options=[
            QuestionOption("A", "Sigues la recomendación", {"marketing_multiplier": 0.9, "price_delta": 1.0}),
            QuestionOption("B", "Solo aplicas la subida de precio", {"price_delta": 1.0}),
            QuestionOption("C", "Prefieres impulsar volumen con más producción", {"production_multiplier": 1.08}),
        ],
    ),
    Question(
        id="q11",
        prompt="Recibes una línea de crédito barata para financiar crecimiento. ¿Cómo la usas?",
        options=[
            QuestionOption("A", "Escalas producción 15%", {"production_multiplier": 1.15}),
            QuestionOption("B", "Campaña masiva de marketing", {"marketing_multiplier": 1.4}),
            QuestionOption("C", "Equilibrio: +5% precio y +5% marketing", {"price_multiplier": 1.05, "marketing_multiplier": 1.05}),
        ],
    ),
    Question(
        id="q12",
        prompt="Clientes corporativos piden contratos a plazo con descuento pero pagos adelantados.",
        options=[
            QuestionOption("A", "Aceptas descuento 2% para asegurar volumen", {"price_multiplier": 0.98, "production_multiplier": 1.07}),
            QuestionOption("B", "Rechazas descuento y mantienes mix actual", {}),
            QuestionOption("C", "Compensas con campaña de upselling", {"marketing_multiplier": 1.15}),
        ],
    ),
    Question(
        id="q13",
        prompt="El comité de auditoría sugiere construir inventario defensivo ante riesgo de supply chain.",
        options=[
            QuestionOption("A", "Construyes inventario: +12% producción", {"production_multiplier": 1.12}),
            QuestionOption("B", "Producción neutra, reservas liquidez", {}),
            QuestionOption("C", "Optimización: +5% producción y +1 en precio", {"production_multiplier": 1.05, "price_delta": 1.0}),
        ],
    ),
    Question(
        id="q14",
        prompt="Se detecta caída en ROI de marketing. Se proponen recortes y reorientación a pricing.",
        options=[
            QuestionOption("A", "Recortas 15% marketing y subes precio 1%", {"marketing_multiplier": 0.85, "price_multiplier": 1.01}),
            QuestionOption("B", "Mantienes marketing y subes producción", {"production_multiplier": 1.08}),
            QuestionOption("C", "Experimentas: +5% marketing con storytelling ESG", {"marketing_multiplier": 1.05}),
        ],
    ),
    Question(
        id="q15",
        prompt="El consejo pide acelerar ROE mediante mayor apalancamiento operativo.",
        options=[
            QuestionOption("A", "Subes producción 18%", {"production_multiplier": 1.18}),
            QuestionOption("B", "Subes precio 3% para mejorar margen", {"price_multiplier": 1.03}),
            QuestionOption("C", "Blend: +8% producción y +1% precio", {"production_multiplier": 1.08, "price_multiplier": 1.01}),
        ],
    ),
    Question(
        id="q16",
        prompt="Se plantea reducción táctica de inventario para liberar capital de trabajo.",
        options=[
            QuestionOption("A", "Bajas producción 12%", {"production_multiplier": 0.88}),
            QuestionOption("B", "Aumentas precio 2% para frenar ventas menos rentables", {"price_multiplier": 1.02}),
            QuestionOption("C", "Más marketing para acelerar rotación", {"marketing_multiplier": 1.18}),
        ],
    ),
    Question(
        id="q17",
        prompt="Una encuesta revela sensibilidad al precio menor a la estimada. ¿Cómo capturas valor?",
        options=[
            QuestionOption("A", "Incrementas precio 4%", {"price_multiplier": 1.04}),
            QuestionOption("B", "Mantienes precio y elevas marketing premium", {"marketing_multiplier": 1.25}),
            QuestionOption("C", "Subes producción para aprovechar demanda", {"production_multiplier": 1.1}),
        ],
    ),
    Question(
        id="q18",
        prompt="La tesorería detecta exceso de caja no asignada. Se sugiere invertir en crecimiento orgánico.",
        options=[
            QuestionOption("A", "Financias marketing intensivo", {"marketing_multiplier": 1.35}),
            QuestionOption("B", "Rebajas precio 2% para impulsar volumen", {"price_multiplier": 0.98}),
            QuestionOption("C", "Balanceas: +6% producción y +1% precio", {"production_multiplier": 1.06, "price_multiplier": 1.01}),
        ],
    ),
    Question(
        id="q19",
        prompt="La Junta evalúa expandir a un nicho premium con menor elasticidad de precio.",
        options=[
            QuestionOption("A", "Estrategia premium: +6% precio, marketing +10%", {"price_multiplier": 1.06, "marketing_multiplier": 1.1}),
            QuestionOption("B", "Piloto moderado: +3% precio y producción estable", {"price_multiplier": 1.03}),
            QuestionOption("C", "Esperas datos, priorizas liquidez", {"production_multiplier": 0.95}),
        ],
    ),
    Question(
        id="q20",
        prompt="Un comité de supply chain recomienda horas extra para aprovechar capacidad ociosa.",
        options=[
            QuestionOption("A", "Aumentas producción 20%", {"production_multiplier": 1.2}),
            QuestionOption("B", "Producción +10% y marketing +5%", {"production_multiplier": 1.1, "marketing_multiplier": 1.05}),
            QuestionOption("C", "No cambias producción, subes precio 1%", {"price_multiplier": 1.01}),
        ],
    ),
]


QUESTION_INDEX = {q.id: q for q in QUESTION_BANK}
