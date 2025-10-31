from celery import Celery

from packages.shared.shared.config import get_settings


def create_celery() -> Celery:
    """Create the Celery application with default settings."""

    settings = get_settings()
    celery_app = Celery(
        "crdc_precheck_worker",
        broker=settings.redis_broker_url,
        backend=settings.redis_result_url,
        include=["apps.worker.worker.tasks"],
    )
    celery_app.conf.update(
        task_routes={"worker.tasks.*": {"queue": "default"}},
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
    )
    return celery_app


app = create_celery()
