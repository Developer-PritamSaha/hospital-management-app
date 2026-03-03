from celery import Celery, Task
from celery.schedules import crontab

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

    # ## Celery cron jobs
    # celery.conf.beat_schedule = {
    #     "auto-assign-weekly-availability": {
    #         "task": "app_backend_Flask.application.celery_tasks.auto_assign_weekly_availability",
    #         "schedule": crontab(hour=0, minute=0, day_of_week=1),  # Every Monday midnight
    #     },
    #     "weekly-admin-report": {
    #         "task": "app_backend_Flask.application.celery_tasks.weekly_admin_report",
    #         "schedule": crontab(hour=8, minute=0, day_of_week=1),  # Monday 8 AM
    #     },
    # }

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery.Task = ContextTask
    celery.set_default()
    return celery