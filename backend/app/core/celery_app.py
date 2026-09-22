from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "shopdb2",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.alert_tasks"],
)

celery_app.conf.timezone = "Asia/Seoul"

celery_app.conf.beat_schedule = {
    "check-admin-alerts-every-5-minutes": {
        "task": "app.tasks.alert_tasks.run_alert_checks",
        "schedule": crontab(minute="*/5"),
    },
}