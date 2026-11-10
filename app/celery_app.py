from celery import Celery
from celery.signals import worker_ready
from prometheus_client import start_http_server

celery_app = Celery(
    "etp",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=False,
)


@worker_ready.connect
def start_metrics_server(**kwargs):
    start_http_server(9100)