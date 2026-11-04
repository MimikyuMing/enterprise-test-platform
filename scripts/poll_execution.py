import time

import requests

BASE_URL = "http://127.0.0.1:8000"


def poll_execution(execution_id: int, max_wait: int = 300) -> dict:
    interval = 0.1
    max_interval = 30
    start = time.time()
    while True:
        resp = requests.get(f"{BASE_URL}/executions/{execution_id}")
        resp.raise_for_status()
        data = resp.json()
        status = data["status"]
        print(f"[{int(time.time() - start)}s] status={status}, interval={interval}s")
        if status in ("success", "failed"):
            return data
        if time.time() - start > max_wait:
            raise TimeoutError(f"execution {execution_id} 超过 {max_wait}s 未完成")
        time.sleep(interval)
        # interval = min(interval * 2, max_interval)


if __name__ == "__main__":
    resp = requests.post(f"{BASE_URL}/executions", json={"total_cases": 10})
    resp.raise_for_status()
    execution_id = resp.json()["id"]
    print(f"created execution {execution_id}")
    result = poll_execution(execution_id)
    print("final:", result)