from celery import Celery, Task
from celery.schedules import crontab 
from datetime import date, time, timedelta

def init_celery_app(app):
    celery = Celery(
        "celery_app_tasks",
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"]         
    )

    celery.conf.update(
        timezone='Asia/Kolkata',
        task_serializer = 'json',
        result_serializer = 'json'
    )

    # Clear out task results from redis result backend after 30 min.
    celery.conf.result_expires = 1800

    ## Celery cron jobs
    celery.conf.beat_schedule = {
        "auto-assign-doctor-weekly-availability": {
            "task": "app_backend_Flask.application.celery_tasks.reset_doctor_weekly_availability",
            "schedule": crontab(hour=0, minute=0, day_of_week=1),  # Every Monday midnight
            # 'schedule': crontab(minute='*/1') # for testing every 1 minute
        },
        "cancel_pending_appointment_slot1": {
            "task": "app_backend_Flask.application.celery_tasks.cancel_pending_appointments",
            "schedule": crontab(hour=12, minute=0),  # after 12:00 PM 
            # 'schedule': crontab(minute='*/1'), # for testing every 1 minute
            "args": ("12:00",)
        },
        "cancel_pending_appointment_slot2": {
            "task": "app_backend_Flask.application.celery_tasks.cancel_pending_appointments",
            "schedule": crontab(hour=17, minute=0),  # after 5:00 PM 
            # 'schedule': crontab(minute='*/1'), # for testing every 1 minute
            "args": ("17:00",)
        },
        "cancel_pending_appointment_slot3": {
            "task": "app_backend_Flask.application.celery_tasks.cancel_pending_appointments",
            "schedule": crontab(hour=22, minute=0),  # after 10:00 PM 
            # 'schedule': crontab(minute='*/1'), # for testing every 1 minute
            "args": ("22:00",)
        },
        "notify_booked_patient_appointments": {
            "task": "app_backend_Flask.application.celery_tasks.notify_patient_appointments",
            "schedule": crontab(hour=8, minute=0)  # every morning 08:00 AM 
            # 'schedule': crontab(minute='*/2') # for testing every 2 minute
        },
    }

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery.Task = ContextTask
    celery.set_default()
    return celery