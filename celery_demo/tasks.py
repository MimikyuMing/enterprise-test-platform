from celery import Celery

app = Celery(
    "demo",
    broker="redis://localhost:6379/0", # 0号库,存放执行任务
    backend="redis://localhost:6379/1", # 1号库,存放执行结果
)


@app.task
def add(a, b):
    return a + b