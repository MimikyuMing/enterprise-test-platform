from prometheus_client import make_asgi_app, Counter, Histogram

metrics_app = make_asgi_app()

test_execution_total = Counter(
    "test_execution_total",
    "Total number of test executions",
    ["status"]
)

test_execution_duration_seconds = Histogram(
    "test_execution_duration_seconds",
    "Execution duration in seconds",
    buckets=[1, 5, 10, 30, 60, 120, 300],
)

test_case_total = Counter(
    "test_case_total",
    "Total number of test case results",
    ["outcome"]
)