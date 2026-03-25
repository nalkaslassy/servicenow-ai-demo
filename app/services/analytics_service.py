from sqlalchemy.orm import Session
from app.database.models import Ticket, GuidanceFeedback, SearchLog


def get_tickets_by_category(db: Session) -> list[dict]:
    rows = db.query(Ticket.category, Ticket.id).all()
    counts: dict[str, int] = {}
    for cat, _ in rows:
        counts[cat] = counts.get(cat, 0) + 1
    return [{"category": k, "count": v} for k, v in sorted(counts.items(), key=lambda x: -x[1])]


def get_avg_resolution_by_priority(db: Session) -> list[dict]:
    tickets = db.query(Ticket).filter(
        Ticket.status == "Resolved",
        Ticket.resolution_time_hours.isnot(None),
    ).all()
    totals: dict[str, list[int]] = {}
    for t in tickets:
        totals.setdefault(t.priority, []).append(t.resolution_time_hours)
    result = []
    for p in ["P1", "P2", "P3", "P4"]:
        if p in totals:
            avg = round(sum(totals[p]) / len(totals[p]), 1)
            result.append({"priority": p, "avg_hours": avg, "count": len(totals[p])})
    return result


def get_escalation_rate(db: Session) -> dict:
    total = db.query(Ticket).count()
    escalated = db.query(Ticket).filter(Ticket.parent_ticket_id.isnot(None)).count()
    rate = round((escalated / total * 100), 1) if total else 0
    return {"total": total, "escalated": escalated, "rate_pct": rate}


def get_feedback_stats(db: Session) -> dict:
    rows = db.query(GuidanceFeedback).all()
    if not rows:
        return {"total": 0, "helpful": 0, "not_helpful": 0, "helpful_pct": 0}
    helpful = sum(1 for r in rows if r.helpful == 1)
    total = len(rows)
    return {
        "total": total,
        "helpful": helpful,
        "not_helpful": total - helpful,
        "helpful_pct": round(helpful / total * 100, 1),
    }


def get_knowledge_gaps(db: Session, limit: int = 5) -> list[dict]:
    """Return recent Low-confidence searches with 0 referenced tickets."""
    gaps = (
        db.query(SearchLog)
        .filter(SearchLog.confidence == "Low", SearchLog.referenced_count == 0)
        .order_by(SearchLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [{"description": g.description, "created_at": g.created_at} for g in gaps]


def get_recent_low_confidence_count(db: Session, hours: int = 24) -> int:
    from datetime import datetime, timezone, timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return (
        db.query(SearchLog)
        .filter(SearchLog.confidence == "Low", SearchLog.created_at >= cutoff)
        .count()
    )
