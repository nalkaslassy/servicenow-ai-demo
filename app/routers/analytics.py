from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.db import get_db
from app.services import analytics_service, ai_service

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


def _build_analytics_context(db: Session) -> dict:
    return {
        "by_category": analytics_service.get_tickets_by_category(db),
        "by_priority": analytics_service.get_avg_resolution_by_priority(db),
        "escalation":  analytics_service.get_escalation_rate(db),
        "feedback":    analytics_service.get_feedback_stats(db),
        "gaps":        analytics_service.get_knowledge_gaps(db),
        "roi":         analytics_service.get_roi_metrics(db),
    }


@router.get("/analytics", response_class=HTMLResponse)
def analytics(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "analytics.html", {
        **_build_analytics_context(db),
        "nl_question": None,
        "nl_answer": None,
    })


@router.post("/analytics/query", response_class=HTMLResponse)
def analytics_query(request: Request, question: str = Form(...), db: Session = Depends(get_db)):
    ctx = _build_analytics_context(db)
    serialisable = {k: v for k, v in ctx.items() if k != "gaps"}
    answer = ai_service.query_analytics(question, serialisable)
    return templates.TemplateResponse(request, "analytics.html", {
        **ctx,
        "nl_question": question,
        "nl_answer": answer,
    })
