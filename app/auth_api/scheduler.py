import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from auth_api.services.remove_expire_tokens import clean_expired_tokens

logger = logging.getLogger("django")


def start():
    """
    Starts the background scheduler to periodically clean expired tokens.

    This function initializes a BackgroundScheduler, schedules the `clean_expired_tokens`
    job to run daily at midnight UTC, and starts the scheduler. It also ensures that the
    scheduler is shut down cleanly when the application exits.

    Raises:
        Exception: If the scheduler fails to start or shut down properly.
    """

    scheduler = BackgroundScheduler()

    # Run the job every day at midnight UTC
    scheduler.add_job(
        clean_expired_tokens,
        trigger=CronTrigger(hour=0, minute=0, timezone="UTC"),
        id="remove_expire_token_job",
        replace_existing=True,
    )

    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started: Expire Token Clearance Job")

    # Shut down cleanly on exit
    atexit.register(lambda: scheduler.shutdown())
