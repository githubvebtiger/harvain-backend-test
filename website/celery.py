# region				-----External Imports-----
from __future__ import absolute_import, unicode_literals

import logging
import os
import sys
import time

import requests
from celery import Celery, signals
from celery.schedules import crontab
from celery.signals import worker_ready

# endregion

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

app = Celery("website")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task
def cache_matches():
    time.sleep(60)
    for kind_of_sport in range(1, 9):
        requests.get(f"https://admin.greekz.com/api/frontend/league/?kind_of_sport={kind_of_sport}&cache=True")


beat_schedules = {
    "task_satellites_balance_migrating": {
        "task": "task_satellites_balance_migrating",
        "schedule": 1 * 60,
        "args": (),
    },
    "task_start_news_import": {
        "task": "task_start_news_import",
        "schedule": crontab(minute=0, hour="*/1"),
        "args": (),
    },
    "task_clean_matches": {
        "task": "task_clean_matches",
        "schedule": crontab(minute=0, hour=11),
        "args": (),
    },
    "task_baseball_data_import": {
        "task": "task_baseball_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
    "task_basketball_data_import": {
        "task": "task_basketball_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
    "task_football_data_import": {
        "task": "task_football_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
    "task_formula_1_data_import": {
        "task": "task_formula_1_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
    "task_handball_data_import": {
        "task": "task_handball_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
    "task_hockey_data_import": {
        "task": "task_hockey_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
    "task_rugby_data_import": {
        "task": "task_rugby_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
    "task_volleyball_data_import": {
        "task": "task_volleyball_data_import",
        "schedule": crontab(minute=0, hour="3,12,18"),
        "args": (),
    },
}

app.conf.beat_schedule = beat_schedules


@signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s, %(thread)d  %(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
            "celery": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": "celery.log",
                "formatter": "default",
            },
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "loggers": {
            "celery": {
                "handlers": ["celery", "console"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {"handlers": ["default"], "level": "DEBUG"},
    }

    logging.config.dictConfig(config)


@worker_ready.connect
def at_start(**kwargs):
    cache_matches.apply_async()
