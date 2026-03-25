from fastapi import APIRouter, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import GuidanceFeedback

router = APIRouter()

@router.post("/feedback/")
def submit_feedback(
    description: str = Form(...),
    helpful: int = Form(...),
    referenced_tickets: str = Form(""),
    db: Session = Depends(get_db),
):
    db.add(GuidanceFeedback(
        description=description,
        helpful=helpful,
        referenced_tickets=referenced_tickets or None,
    ))
    db.commit()
    return RedirectResponse(url="/", status_code=303)
