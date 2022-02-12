import os
from flask_apscheduler import APScheduler
from apscheduler.events import (
    EVENT_JOB_ADDED,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_MISSED,
    EVENT_JOB_ERROR,
)


def job_added(event):
    """Job added event."""
    print(f"CronJob added ID={event.job_id}")


def job_submitted(event):
    """Job scheduled to run event."""
    print(f"CronJob submitted ID={event.job_id}")


def job_removed(event):
    """Job removed event."""
    print(f"CronJob removed ID={event.job_id}")


def job_missed(event):
    """Job missed event."""
    print(f"CronJob missed ID={event.job_id}")


def job_error(event):
    """Job error event."""
    print(f"CronJob error ID={event.job_id}")


if os.getenv("SCHEDULER") == "True":
    scheduler = APScheduler()
    scheduler.add_listener(job_added, EVENT_JOB_ADDED)
    scheduler.add_listener(job_submitted, EVENT_JOB_SUBMITTED)
    scheduler.add_listener(job_removed, EVENT_JOB_REMOVED)
    scheduler.add_listener(job_missed, EVENT_JOB_MISSED)
    scheduler.add_listener(job_error, EVENT_JOB_ERROR)
else:
    scheduler = None
