import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.db import get_db
from app.services import ticket_service, ai_service, sla_service, analytics_service

router = APIRouter(prefix="/tickets")
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, status: str = None, category: str = None,
              db: Session = Depends(get_db)):
    tickets = ticket_service.get_all_tickets(db, status=status, category=category)
    stats = ticket_service.get_stats(db)
    ticket_slas = {t.id: sla_service.get_sla_info(t) for t in tickets}
    major_incidents = sla_service.detect_major_incidents(tickets)
    low_conf_count = analytics_service.get_recent_low_confidence_count(db)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "tickets": tickets,
        "stats": stats,
        "ticket_slas": ticket_slas,
        "major_incidents": major_incidents,
        "low_conf_count": low_conf_count,
        "categories": ["Network", "Software", "Hardware", "Access", "Email", "Security"],
        "statuses": ["Open", "In Progress", "Resolved", "Closed"],
        "filter_status": status or "",
        "filter_category": category or "",
    })

@router.post("/create")
def create_ticket(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    priority: str = Form(...),
    assigned_team: str = Form(...),
    db: Session = Depends(get_db)
):
    ticket = ticket_service.create_ticket(db, {
        "title": title, "description": description,
        "category": category, "priority": priority, "assigned_team": assigned_team,
    })
    return RedirectResponse(url=f"/tickets/{ticket.id}?created=true", status_code=303)

@router.post("/{ticket_id}/analyze")
def analyze_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = ticket_service.get_ticket(db, ticket_id)
    resolved = ticket_service.get_resolved_tickets(db)
    guidance = ai_service.suggest_next_action(ticket, resolved)
    ticket_service.save_ai_guidance(db, ticket_id, json.dumps(guidance))
    actions_summary = "; ".join(guidance.get("next_actions", [])[:2])
    ticket_service.add_work_note(db, ticket_id, "ai_suggestion",
        f"AI Analysis — Risk: {guidance.get('risk_level','?')}. "
        f"Est. {guidance.get('estimated_resolution_hours','?')}h. "
        f"Actions: {actions_summary}")
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)

@router.post("/{parent_id}/sub")
def create_sub_ticket(
    parent_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    priority: str = Form(...),
    assigned_team: str = Form(...),
    db: Session = Depends(get_db)
):
    ticket_service.create_sub_ticket(db, parent_id, {
        "title": title, "description": description,
        "category": category, "priority": priority, "assigned_team": assigned_team,
    })
    return RedirectResponse(url=f"/tickets/{parent_id}", status_code=303)

@router.get("/{ticket_id}", response_class=HTMLResponse)
def ticket_detail(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    ticket = ticket_service.get_ticket(db, ticket_id)
    work_notes = ticket_service.get_work_notes(db, ticket_id)
    sub_tickets = ticket_service.get_sub_tickets(db, ticket_id)
    sla = sla_service.get_sla_info(ticket)

    ai_guidance = None
    if ticket.ai_guidance:
        try:
            ai_guidance = json.loads(ticket.ai_guidance)
        except Exception:
            ai_guidance = None

    parent = None
    if ticket.parent_ticket_id:
        parent = ticket_service.get_ticket(db, ticket.parent_ticket_id)

    return templates.TemplateResponse("ticket_detail.html", {
        "request": request,
        "ticket": ticket,
        "work_notes": work_notes,
        "sub_tickets": sub_tickets,
        "sla": sla,
        "ai_guidance": ai_guidance,
        "parent": parent,
    })
