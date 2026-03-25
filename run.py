import uvicorn
from app.database.db import init_db
from app.database.seed import seed_if_empty

if __name__ == "__main__":
    init_db()
    seed_if_empty()
    print("\n  ServiceNow AI Demo running at http://localhost:8000\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
