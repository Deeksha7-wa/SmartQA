import os
from celery import Celery

REDIS_URL = os.environ["REDIS_URL"]  # NO fallback

celery = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    imports=("app.workers.tasks",)
)