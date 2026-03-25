from sqlalchemy.orm import Session
from app.database.models import Ticket, Team, WorkNote
from datetime import datetime, timezone
import random, string

def get_all_tickets(db: Session, status: str = None, category: str = None):
    q = db.query(Ticket)
    if status:
        q = q.filter(Ticket.status == status)
    if category:
        q = q.filter(Ticket.category == category)
    return q.order_by(Ticket.id.desc()).all()

def get_ticket(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def get_ticket_by_number(db: Session, number: str):
    return db.query(Ticket).filter(Ticket.ticket_number == number).first()

def get_resolved_tickets(db: Session):
    return db.query(Ticket).filter(Ticket.status == "Resolved").all()

def get_teams(db: Session):
    return db.query(Team).all()

def get_team_by_name(db: Session, name: str):
    return db.query(Team).filter(Team.name == name).first()

def create_ticket(db: Session, data: dict) -> Ticket:
    suffix = "".join(random.choices(string.digits, k=7))
    ticket = Ticket(
        ticket_number=f"INC{suffix}",
        title=data.get("title", "Untitled"),
        description=data.get("description", ""),
        category=data.get("category", "Software"),
        priority=data.get("priority", "P3"),
        status="Open",
        assigned_team=data.get("assigned_team", "Software Support"),
        created_at=datetime.now(timezone.utc),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_stats(db: Session) -> dict:
    total     = db.query(Ticket).count()
    open_     = db.query(Ticket).filter(Ticket.status == "Open").count()
    resolved  = db.query(Ticket).filter(Ticket.status == "Resolved").count()
    in_prog   = db.query(Ticket).filter(Ticket.status == "In Progress").count()
    return {"total": total, "open": open_, "resolved": resolved, "in_progress": in_prog}

# ── Work Notes ────────────────────────────────────────────────────────────────

def get_work_notes(db: Session, ticket_id: int):
    return db.query(WorkNote).filter(WorkNote.ticket_id == ticket_id)\
             .order_by(WorkNote.created_at.asc()).all()

def add_work_note(db: Session, ticket_id: int, note_type: str, content: str,
                  author: str = "Agent") -> WorkNote:
    note = WorkNote(ticket_id=ticket_id, note_type=note_type,
                    content=content, author=author)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

# ── Status transitions ────────────────────────────────────────────────────────

def update_ticket_status(db: Session, ticket_id: int, new_status: str,
                         author: str = "Agent", resolution: str = None,
                         resolution_notes: str = None) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    old_status = ticket.status
    ticket.status = new_status
    if new_status == "Resolved":
        ticket.resolved_at = datetime.now(timezone.utc)
        if resolution:
            ticket.resolution = resolution
        if resolution_notes:
            ticket.resolution_notes = resolution_notes
    db.commit()
    add_work_note(db, ticket_id, "status_change",
                  f"Status changed from {old_status} to {new_status}.", author)
    return ticket

# ── Sub-tickets ───────────────────────────────────────────────────────────────

def get_sub_tickets(db: Session, parent_id: int):
    return db.query(Ticket).filter(Ticket.parent_ticket_id == parent_id).all()

def create_sub_ticket(db: Session, parent_id: int, data: dict) -> Ticket:
    ticket = create_ticket(db, data)
    ticket.parent_ticket_id = parent_id
    db.commit()
    db.refresh(ticket)
    add_work_note(db, parent_id, "comment",
                  f"Sub-ticket {ticket.ticket_number} opened with {ticket.assigned_team}.")
    return ticket

# ── AI guidance ───────────────────────────────────────────────────────────────

def save_ai_guidance(db: Session, ticket_id: int, guidance_json: str) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    ticket.ai_guidance = guidance_json
    db.commit()
    db.refresh(ticket)
    return ticket
