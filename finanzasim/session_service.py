from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .cfa_questions import QUESTION_INDEX, apply_option_impact, pick_random_question
from .financial_calculator import simulate_quarter


@dataclass
class Company:
    name: str
    financials: list
    decisions: Dict
    agent_chat: list
    active_question_id: str | None = None
    selected_option_id: str | None = None
    question_history: list | None = None


@dataclass
class Session:
    id: str
    game_code: str
    game_status: str
    current_quarter: int
    last_update_time: int
    companies: Dict[str, Company]


class InMemorySessionRepository:
    def __init__(self, initial_sessions: Dict[str, Session] | None = None):
        self.sessions = dict(initial_sessions or {})

    def get_by_id(self, session_id: str) -> Session | None:
        return self.sessions.get(session_id)

    def save(self, session: Session) -> Session:
        self.sessions[session.id] = session
        return session


class SessionService:
    def __init__(self, session_repository: InMemorySessionRepository):
        self.session_repository = session_repository

    def assign_quarter_questions(self, session_id: str) -> Session:
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        updated_companies: Dict[str, Company] = {}
        for company_id, company in session.companies.items():
            history = list(company.question_history or [])
            question = pick_random_question(history)
            history.append(question.id)

            updated_companies[company_id] = Company(
                name=company.name,
                financials=list(company.financials),
                decisions=dict(company.decisions),
                agent_chat=list(company.agent_chat),
                active_question_id=question.id,
                selected_option_id=None,
                question_history=history,
            )

        updated_session = Session(
            id=session.id,
            game_code=session.game_code,
            game_status=session.game_status,
            current_quarter=session.current_quarter,
            last_update_time=session.last_update_time,
            companies=updated_companies,
        )

        return self.session_repository.save(updated_session)

    def close_quarter(self, session_id: str) -> Session:
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        updated_companies: Dict[str, Company] = {}
        for company_id, company in session.companies.items():
            previous_financials = company.financials[-1]
            base_decision = company.decisions

            question_id = company.active_question_id or pick_random_question().id
            selected_option = None
            if question := QUESTION_INDEX.get(question_id):
                selected_option = next(
                    (option for option in question.options if option.id == company.selected_option_id),
                    None,
                )

            effective_decision = (
                apply_option_impact(base_decision, selected_option) if selected_option else base_decision
            )

            result = simulate_quarter(previous_financials, effective_decision)
            history = list(company.question_history or [])
            if not history or history[-1] != question_id:
                history.append(question_id)
            updated_companies[company_id] = Company(
                name=company.name,
                financials=company.financials + [result.__dict__],
                decisions={},
                agent_chat=list(company.agent_chat),
                active_question_id=None,
                selected_option_id=None,
                question_history=history,
            )

        next_quarter = session.current_quarter + 1
        game_status = "Finished" if next_quarter > 4 else f"Q{next_quarter}"

        updated_session = Session(
            id=session.id,
            game_code=session.game_code,
            game_status=game_status,
            current_quarter=next_quarter,
            last_update_time=session.last_update_time,
            companies=updated_companies,
        )

        return self.session_repository.save(updated_session)
