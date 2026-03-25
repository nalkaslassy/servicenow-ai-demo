"""
One-shot migration — adds new columns to the existing tickets table.
Safe to run multiple times (checks before altering).
"""
from app.database.db import engine

def run_migrations():
    with engine.connect() as conn:
        existing = [row[1] for row in conn.execute("PRAGMA table_info(tickets)")]
        if "parent_ticket_id" not in existing:
            conn.execute("ALTER TABLE tickets ADD COLUMN parent_ticket_id INTEGER")
        if "ai_guidance" not in existing:
            conn.execute("ALTER TABLE tickets ADD COLUMN ai_guidance TEXT")
