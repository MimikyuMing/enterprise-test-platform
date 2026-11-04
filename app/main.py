from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import SessionLocal, init_db
from app.models import Execution
from app.schemas import ExecutionCreate, ExecutionResponse
from app.tasks import run_execution

app = FastAPI(title="Enterprise Test Platform")


init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"database error: {e}")
    finally:
        db.close()
    return {"status": "ok", "database": db_status}


@app.post("/executions", response_model=ExecutionResponse, status_code=201)
def create_execution(payload: ExecutionCreate, db: Session = Depends(get_db)):
    execution = Execution(status="pending", total_cases=payload.total_cases)
    db.add(execution)
    db.commit()
    db.refresh(execution)

    run_execution.delay(execution.id)

    return execution


@app.get("/executions/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: int, response: Response, db: Session = Depends(get_db)):
    execution = db.get(Execution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="execution not found")
    if execution.status in ("pending", "running"):
        response.headers["Retry-After"] = "2"
    return execution
