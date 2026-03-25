from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.routers import tickets, search, work_notes, feedback, analytics, demo
from app.database.db import init_db
from app.database.seed import seed_if_empty, seed_work_notes_if_empty

app = FastAPI(title="ServiceNow AI Demo")

BASE = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

app.include_router(tickets.router)
app.include_router(work_notes.router)
app.include_router(search.router)
app.include_router(feedback.router)
app.include_router(analytics.router)
app.include_router(demo.router)

@app.on_event("startup")
def startup():
    init_db()
    seed_if_empty()
    seed_work_notes_if_empty()
