from celery import Celery


celery = Celery(
    "ecommerce",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    task_track_started=True,

    task_acks_late=True,
    task_reject_on_worker_lost=True,

    worker_prefetch_multiplier=1,

    timezone="UTC",
    enable_utc=True,
)