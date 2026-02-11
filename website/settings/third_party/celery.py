# region				-----External Imports-----
import os

# endregion

CELERY_BROKER_URL = f'redis://{os.environ.get("REDIS_HOST","127.0.0.1")}:{os.environ.get("REDIS_PORT",6379)}'
CELERY_RESULT_BACKEND = f'redis://{os.environ.get("REDIS_HOST","127.0.0.1")}:{os.environ.get("REDIS_PORT",6379)}'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Kiev"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
