import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from auth_api.services.remove_expire_tokens import clean_expired_tokens

logger = logging.getLogger("django")


def start():
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
    logger.info("✅ Scheduler started: Expire Token Clearance Job")

    # Shut down cleanly on exit
    atexit.register(lambda: scheduler.shutdown())
