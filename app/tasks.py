import time
from datetime import datetime

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Execution


@celery_app.task
def run_execution(execution_id: int):
    db = SessionLocal()
    try:
        execution = db.get(Execution, execution_id)
        if not execution:
            return {"error": f"execution {execution_id} not found"}

        execution.status = "running"
        execution.started_at = datetime.now()
        db.commit()

        # 模拟执行：Day 4 会替换成真实测试执行
        time.sleep(2)
        total = execution.total_cases
        passed = total
        failed = 0

        execution.status = "success"
        execution.passed = passed
        execution.failed = failed
        execution.finished_at = datetime.now()
        db.commit()

        return {"execution_id": execution_id, "passed": passed, "failed": failed}
    finally:
        db.close()