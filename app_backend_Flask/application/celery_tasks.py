from celery import shared_task
from app_backend_Flask.application.extensions import db
from datetime import datetime, timedelta

@shared_task()
def test_task(name):
    print("*> From Inside test task. Hello", name)