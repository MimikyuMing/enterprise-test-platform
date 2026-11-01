from fastapi import FastAPI
from sqlalchemy import text

from app.db import SessionLocal

app = FastAPI(title="Enterprise Test Platform")


@app.get("/health")
def health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
    finally:
        db.close()
    return {"status": "ok", "database": db_status}