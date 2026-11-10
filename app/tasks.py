import time
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Execution, CaseResult
from app.executor import get_executor
from app.metrics import (
    test_case_total,
    test_execution_duration_seconds,
    test_execution_total,
)


@celery_app.task
def run_execution(execution_id: int):
    db = SessionLocal()
    start_time = time.monotonic()
    final_status = "error"  # 兜底，异常时也会记一次
    try:
        execution = db.get(Execution, execution_id)
        if not execution:
            return {"error": f"execution {execution_id} not found"}

        execution.status = "running"
        execution.started_at = datetime.now(timezone.utc)
        db.commit()

        executor = get_executor()
        result = executor.execute(execution.total_cases)

        if result.error:
            final_status = "error"
        elif result.failed > 0:
            final_status = "failed"
        else:
            final_status = "success"

        execution.status = final_status
        execution.total_cases = result.total
        execution.passed = result.passed
        execution.failed = result.failed
        execution.finished_at = datetime.now(timezone.utc)
        db.commit()

        inserted = 0
        if result.case_results:
            case_rows = [
                CaseResult(
                    execution_id=execution_id,
                    nodeid=cr.nodeid[:255],
                    outcome=cr.outcome[:20],
                    duration=cr.duration,
                    message=cr.message,
                )
                for cr in result.case_results
            ]
            db.add_all(case_rows)
            db.commit()
            inserted = len(case_rows)

            for cr in result.case_results:
                test_case_total.labels(outcome=cr.outcome).inc()

        return {
            "execution_id": execution_id,
            "status": final_status,
            "total": result.total,
            "passed": result.passed,
            "failed": result.failed,
            "error": result.error,
            "case_results_inserted": inserted,
        }
    except Exception:
        execution = db.get(Execution, execution_id)
        if execution:
            execution.status = "error"
            execution.finished_at = datetime.now(timezone.utc)
            db.commit()
        raise
    finally:
        test_execution_total.labels(status=final_status).inc()
        test_execution_duration_seconds.observe(time.monotonic() - start_time)
        db.close()