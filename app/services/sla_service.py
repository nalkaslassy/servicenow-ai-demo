from datetime import datetime, timedelta, timezone
from collections import defaultdict

SLA_HOURS = {"P1": 1, "P2": 4, "P3": 8, "P4": 24}

def get_sla_info(ticket) -> dict:
    if ticket.status in ("Resolved", "Closed"):
        return {"color": "green", "breached": False, "pct_used": 0, "label": "Resolved"}

    now = datetime.now(timezone.utc)
    created = ticket.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)

    budget = SLA_HOURS.get(ticket.priority, 8)
    elapsed = (now - created).total_seconds() / 3600
    pct = min((elapsed / budget) * 100, 100)

    if pct >= 100:
        color = "red"
    elif pct >= 75:
        color = "yellow"
    else:
        color = "green"

    return {
        "color": color,
        "breached": pct >= 100,
        "pct_used": round(pct, 1),
        "elapsed_hours": round(elapsed, 1),
        "budget_hours": budget,
        "label": f"{round(elapsed, 1)}h / {budget}h",
    }

def detect_major_incidents(tickets: list) -> list:
    # Flag any category with 3+ currently open/in-progress tickets
    buckets = defaultdict(int)
    for t in tickets:
        if t.status not in ("Resolved", "Closed"):
            buckets[t.category] += 1
    return [{"category": cat, "count": cnt} for cat, cnt in buckets.items() if cnt >= 3]
