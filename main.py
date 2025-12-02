import time
import uuid
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from finanzasim.session_service import (
    Company,

    InMemorySessionRepository,
    Session,
    SessionService,
)
from finanzasim.cfa_questions import QUESTION_INDEX, Question

# Initial state for a new company
INITIAL_FINANCIALS = [
    {
        "quarter": 0,
        "cash": 50_000,
        "inventory": 1_000,
        "equity": 50_000,
        "debt": 0.0,
        "revenue": 0.0,
        "cogs": 0.0,
        "gross_profit": 0.0,
        "operating_expenses": 0.0,
        "ebit": 0.0,
        "taxes": 0.0,
        "net_income": 0.0,
        "units_sold": 0.0,
        "liquidity_ratio": 0.0,
        "net_margin": 0.0,
        "price": 0.0,
        "marketing": 0.0,
        "production": 0.0,
    }
]

# --- Pydantic Models for API validation ---

class CompanyDecisionSubmission(BaseModel):
    company_id: str
    production: float
    price: float
    marketing: float

class CompanyAnswer(BaseModel):
    company_id: str
    option_id: str

class CreateSessionRequest(BaseModel):
    company_names: list[str]

# --- API Implementation ---

app = FastAPI(
    title="FinanzaSim API",
    description="API for managing multiplayer financial simulation games.",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# In-memory repository for simplicity
session_repository = InMemorySessionRepository()
session_service = SessionService(session_repository)

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/questions/{question_id}", response_model=Question)
def get_question(question_id: str):
    """
    Retrieves the details of a specific question.
    """
    question = QUESTION_INDEX.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.post("/sessions", response_model=Session, status_code=201)
def create_session(request: CreateSessionRequest):
    """
    Creates a new game session with one or more companies.
    """
    session_id = str(uuid.uuid4())
    game_code = str(uuid.uuid4())[:6].upper()
    companies = {}
    for name in request.company_names:
        company_id = name.lower().replace(" ", "_")
        companies[company_id] = Company(
            name=name,
            financials=list(INITIAL_FINANCIALS),
            decisions={},
            agent_chat=[],
            question_history=[],
        )

    new_session = Session(
        id=session_id,
        game_code=game_code,
        game_status="Q1",
        current_quarter=1,
        last_update_time=int(time.time()),
        companies=companies,
    )
    # Save the session first
    session_repository.save(new_session)
    # Then assign questions, which will update and save it again
    session_with_questions = session_service.assign_quarter_questions(session_id)
    return session_with_questions


@app.get("/sessions/{session_id}", response_model=Session)
def get_session(session_id: str):
    """
    Retrieves the current state of a game session.
    """
    session = session_repository.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/sessions/{session_id}/decisions", response_model=Session)
def submit_decision(session_id: str, submission: CompanyDecisionSubmission):
    """
    Submits a company's financial decisions for the current quarter.
    """
    session = session_repository.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    company = session.companies.get(submission.company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{submission.company_id}' not found in session")

    company.decisions = {
        "production": submission.production,
        "price": submission.price,
        "marketing": submission.marketing
    }
    session_repository.save(session)
    return session


@app.post("/sessions/{session_id}/answer", response_model=Session)
def submit_answer(session_id: str, answer: CompanyAnswer):
    """
    Submits a company's answer to the active question.
    """
    session = session_repository.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    company = session.companies.get(answer.company_id)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{answer.company_id}' not found in session")

    company.selected_option_id = answer.option_id
    session_repository.save(session)
    return session

@app.post("/sessions/{session_id}/close_quarter", response_model=Session)
def close_quarter(session_id: str):
    """
    Closes the current quarter, simulates the results, and moves to the next quarter.
    """
    try:
        updated_session = session_service.close_quarter(session_id)
        # Assign questions for the new quarter if the game is not finished
        if updated_session.game_status != "Finished":
             session_with_new_questions = session_service.assign_quarter_questions(session_id)
             session_with_new_questions.last_update_time = int(time.time())
             session_repository.save(session_with_new_questions)
             return session_with_new_questions
        return updated_session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
