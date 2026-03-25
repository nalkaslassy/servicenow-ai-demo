from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.services import ticket_service

router = APIRouter(prefix="/tickets")

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
    ticket_id: int,
    new_status: str = Form(...),
    author: str = Form("Agent"),
    resolution: str = Form(""),
    resolution_notes: str = Form(""),
    db: Session = Depends(get_db)
):
    ticket_service.update_ticket_status(
        db, ticket_id, new_status, author,
        resolution=resolution or None,
        resolution_notes=resolution_notes or None,
    )
    return RedirectResponse(url=f"/tickets/{ticket_id}", status_code=303)
