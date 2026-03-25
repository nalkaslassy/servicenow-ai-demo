from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.db import get_db
from app.services import analytics_service

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/analytics", response_class=HTMLResponse)
def analytics(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "by_category":     analytics_service.get_tickets_by_category(db),
        "by_priority":     analytics_service.get_avg_resolution_by_priority(db),
        "escalation":      analytics_service.get_escalation_rate(db),
        "feedback":        analytics_service.get_feedback_stats(db),
        "gaps":            analytics_service.get_knowledge_gaps(db),
    })
