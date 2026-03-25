from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.db import get_db
from app.database.models import SearchLog
from app.services import ticket_service, ai_service

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    stats = ticket_service.get_stats(db)
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})

@router.post("/search", response_class=HTMLResponse)
def search(request: Request, description: str = Form(...), db: Session = Depends(get_db)):
    resolved = ticket_service.get_resolved_tickets(db)
    guidance = ai_service.get_specialist_guidance(description, resolved)

    # Look up the referenced tickets so specialist can drill into them
    referenced = []
    for number in guidance.get("referenced_tickets", []):
        ticket = ticket_service.get_ticket_by_number(db, number)
        if ticket:
            referenced.append(ticket)

    # Log every search for knowledge gap detection
    db.add(SearchLog(
        description=description,
        confidence=guidance.get("confidence", "Low"),
        referenced_count=len(referenced),
    ))
    db.commit()

    return templates.TemplateResponse("results.html", {
        "request": request,
        "description": description,
        "guidance": guidance,
        "referenced": referenced,
    })

@router.get("/classify", response_class=HTMLResponse)
def classify_form(request: Request, description: str = "", db: Session = Depends(get_db)):
    teams = ticket_service.get_teams(db)
    classification = None
    if description:
        classification = ai_service.classify_new_ticket(description, teams)
    return templates.TemplateResponse("new_ticket.html", {
        "request": request,
        "description": description,
        "classification": classification,
    })
