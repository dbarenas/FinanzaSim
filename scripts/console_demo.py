from __future__ import annotations

import json
import pathlib
import sys
from datetime import datetime

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from finanzasim.cfa_questions import QUESTION_INDEX
from finanzasim.session_service import Company, InMemorySessionRepository, Session, SessionService


def create_demo_session() -> Session:
    return Session(
        id="demo-session",
        game_code="XYZ123",
        game_status="Q1",
        current_quarter=1,
        last_update_time=int(datetime.now().timestamp()),
        companies={
            "alpha": Company(
                name="Alpha Corp",
                financials=[{"quarter": 0, "cash": 50_000, "inventory": 1_000, "equity": 50_000, "debt": 0}],
                decisions={"production": 1_500, "price": 55, "marketing": 2_000},
                agent_chat=[],
            ),
            "beta": Company(
                name="Beta Inc",
                financials=[{"quarter": 0, "cash": 40_000, "inventory": 800, "equity": 40_000, "debt": 0}],
                decisions={"production": 1_200, "price": 48, "marketing": 2_500},
                agent_chat=[],
            ),
        },
    )


def print_company_snapshot(company: Company) -> None:
    latest = company.financials[-1]
    print(f"\n{company.name} - Q{latest['quarter']}")
    print(json.dumps({
        "Cash": latest["cash"],
        "Inventory": latest["inventory"],
        "Debt": latest["debt"],
        "Equity": latest["equity"],
        "Revenue": latest.get("revenue"),
        "NetIncome": latest.get("net_income"),
        "Liquidity": latest.get("liquidity_ratio"),
        "NetMargin": latest.get("net_margin"),
    }, indent=2))


def run_demo() -> None:
    repository = InMemorySessionRepository()
    service = SessionService(repository)
    session = create_demo_session()
    repository.save(session)
    session = service.assign_quarter_questions(session.id)

    print("=== FinanzaSim Console Demo (Python) ===")
    print("Preguntas CFA-style asignadas al inicio del trimestre:\n")
    prepared_companies = {}
    for company_id, company in session.companies.items():
        question = QUESTION_INDEX[company.active_question_id]
        default_option = question.options[0]
        print(f"- {company.name}: {question.prompt}")
        for option in question.options:
            print(f"    {option.id}) {option.text}")
        print(f"  -> Demo selecciona opción {default_option.id}\n")

        prepared_companies[company_id] = Company(
            name=company.name,
            financials=list(company.financials),
            decisions=dict(company.decisions),
            agent_chat=list(company.agent_chat),
            active_question_id=company.active_question_id,
            selected_option_id=default_option.id,
            question_history=list(company.question_history or []),
        )

    session = Session(
        id=session.id,
        game_code=session.game_code,
        game_status=session.game_status,
        current_quarter=session.current_quarter,
        last_update_time=session.last_update_time,
        companies=prepared_companies,
    )
    repository.save(session)

    print("Cerrando trimestre para la sesión demo...\n")
    updated = service.close_quarter("demo-session")

    for company in updated.companies.values():
        print_company_snapshot(company)

    print("\nEstado de la sesión:", {
        "quarter": updated.current_quarter,
        "status": updated.game_status,
    })


if __name__ == "__main__":
    run_demo()
