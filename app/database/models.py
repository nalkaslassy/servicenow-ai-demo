from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.database.db import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id                    = Column(Integer, primary_key=True, index=True)
    ticket_number         = Column(String, unique=True, index=True)
    title                 = Column(String, nullable=False)
    description           = Column(Text, nullable=False)
    category              = Column(String, nullable=False)
    priority              = Column(String, default="P3")
    status                = Column(String, default="Open")
    assigned_team         = Column(String, nullable=False)
    resolution            = Column(Text, nullable=True)
    resolution_notes      = Column(Text, nullable=True)
    resolution_time_hours = Column(Integer, nullable=True)
    tags                  = Column(String, nullable=True)
    created_at            = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at           = Column(DateTime, nullable=True)
    parent_ticket_id      = Column(Integer, nullable=True)
    ai_guidance           = Column(Text, nullable=True)

class Team(Base):
    __tablename__ = "teams"

    id                      = Column(Integer, primary_key=True)
    name                    = Column(String, unique=True)
    description             = Column(Text)
    handles_categories      = Column(String)
    avg_resolution_hours    = Column(Integer)
    contact                 = Column(String)

class WorkNote(Base):
    __tablename__ = "work_notes"

    id         = Column(Integer, primary_key=True, index=True)
    ticket_id  = Column(Integer, nullable=False, index=True)
    note_type  = Column(String, default="comment")
    content    = Column(Text, nullable=False)
    author     = Column(String, default="Agent")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class GuidanceFeedback(Base):
    __tablename__ = "guidance_feedback"

    id                 = Column(Integer, primary_key=True, index=True)
    description        = Column(Text, nullable=False)
    helpful            = Column(Integer, nullable=False)  # 1=yes, 0=no
    referenced_tickets = Column(String, nullable=True)
    created_at         = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SearchLog(Base):
    __tablename__ = "search_logs"

    id               = Column(Integer, primary_key=True, index=True)
    description      = Column(Text, nullable=False)
    confidence       = Column(String, nullable=False)
    referenced_count = Column(Integer, default=0)
    created_at       = Column(DateTime, default=lambda: datetime.now(timezone.utc))
