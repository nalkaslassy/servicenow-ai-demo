from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import ticket_service, sla_service
import json

router = APIRouter(prefix="/tickets")
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.post("/{ticket_id}/notes")
def add_note(
    ticket_id: int,
    content: str = Form(...),
    note_type: str = Form("comment"),
    author: str = Form("Agent"),
    db: Session = Depends(get_db)
):
    ticket_service.add_work_note(db, ticket_id, note_type, content, author)
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)

@router.post("/{ticket_id}/status")
def change_status(
    request: Request,
    ticket_id: int,
    new_status: str = Form(...),
    author: str = Form("Agent"),
    resolution: str = Form(""),
    resolution_notes: str = Form(""),
    db: Session = Depends(get_db)
):
    if new_status == "Resolved" and (not resolution.strip() or not resolution_notes.strip()):
        ticket = ticket_service.get_ticket(db, ticket_id)
        work_notes = ticket_service.get_work_notes(db, ticket_id)
        sub_tickets = ticket_service.get_sub_tickets(db, ticket_id)
        sla = sla_service.get_sla_info(ticket)
        ai_guidance = None
        if ticket.ai_guidance:
            try:
                ai_guidance = json.loads(ticket.ai_guidance)
            except Exception:
                pass
        parent = ticket_service.get_ticket(db, ticket.parent_ticket_id) if ticket.parent_ticket_id else None
        return templates.TemplateResponse("ticket_detail.html", {
            "request": request,
            "ticket": ticket,
            "work_notes": work_notes,
            "sub_tickets": sub_tickets,
            "sla": sla,
            "ai_guidance": ai_guidance,
            "parent": parent,
            "status_error": "Resolution summary and step-by-step notes are required before marking a ticket as Resolved.",
        }, status_code=422)

    ticket_service.update_ticket_status(
        db, ticket_id, new_status, author,
        resolution=resolution or None,
        resolution_notes=resolution_notes or None,
    )
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)
