import time
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Execution
from app.executor import get_executor


@celery_app.task
def run_execution(execution_id: int):
    db = SessionLocal()
    try:
        execution = db.get(Execution, execution_id)
        if not execution:
            return {"error": f"execution {execution_id} not found"}

        execution.status = "running"
        execution.started_at = datetime.now(timezone.utc)
        db.commit()

        executor = get_executor()
        result = executor.execute(execution.total_cases)

        if(result.error):
            execution.status = "error"
        elif result.failed > 0:
            execution.status = "failed"
        else:
            execution.status = "success"

        execution.total_cases = result.total
        execution.passed = result.passed
        execution.failed = result.failed
        execution.finished_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "execution_id": execution_id,
            "status": execution.status,
            "total": result.total,
            "passed": result.passed,
            "failed": result.failed,
            "error": result.error,
        }
    except Exception as e:
        execution = db.get(Execution, execution_id)
        if execution:
            execution.status = "error"
            execution.finished_at = datetime.now(timezone.utc)
            db.commit()
        raise
    finally:
        db.close()