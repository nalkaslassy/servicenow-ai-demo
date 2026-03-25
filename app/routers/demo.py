from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

@router.get("/demo", response_class=HTMLResponse)
def demo(request: Request):
    return templates.TemplateResponse("demo.html", {"request": request})
