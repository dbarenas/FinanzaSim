import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from finanzasim.cfa_questions import QUESTION_INDEX, apply_option_impact
from finanzasim.session_service import Company, InMemorySessionRepository, Session, SessionService


def test_apply_option_impact_scales_decision():
    base_decision = {"production": 1000, "price": 50, "marketing": 2000}
    option = QUESTION_INDEX["q02"].options[1]  # descuento parcial y más volumen

    adjusted = apply_option_impact(base_decision, option)

    assert adjusted["price"] == 50 * 0.97
    assert adjusted["production"] == 1000 * 1.05
    assert adjusted["marketing"] == 2000


def test_close_quarter_uses_selected_option():
    repository = InMemorySessionRepository()
    service = SessionService(repository)
    company = Company(
        name="Gamma",
        financials=[{"quarter": 0, "cash": 10_000, "inventory": 500, "equity": 10_000, "debt": 0}],
        decisions={"production": 800, "price": 52, "marketing": 1_000},
        agent_chat=[],
        active_question_id="q03",
        selected_option_id="A",  # recorte de marketing 20%
        question_history=[],
    )
    session = Session(
        id="s1",
        game_code="CODE1",
        game_status="Q1",
        current_quarter=1,
        last_update_time=0,
        companies={"gamma": company},
    )
    repository.save(session)

    updated = service.close_quarter("s1")
    latest = updated.companies["gamma"].financials[-1]

    assert latest["marketing"] == 800  # 1000 * 0.8
    assert updated.companies["gamma"].question_history  # registra la pregunta
