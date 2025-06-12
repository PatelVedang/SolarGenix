import logging
import os
from datetime import datetime, timedelta, tzinfo
from logging import FileHandler

from slack_sdk.webhook import WebhookClient

# --- UTC Timezone Class ---


class UTCTimezone(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


utc_tz = UTCTimezone()


class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=UTCTimezone()):
        super().__init__(fmt, datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=self.tz)
        return dt.strftime(datefmt) if datefmt else dt.isoformat()


class SlackFormatter(TZFormatter):
    def format(self, record):
        separator = "\n" + "─" * 50 + "\n"

        # Risk level icons based on log level
        risk_icons = {
            logging.WARNING: ":warning:",
            logging.ERROR: ":rotating_light:",
            logging.CRITICAL: ":red_circle:",
            logging.FATAL: ":skull_and_crossbones:",
        }

        # Get the appropriate icon, default to warning for unknown levels
        risk_icon = risk_icons.get(record.levelno, ":warning:")

        # Format timestamp
        timestamp = self.formatTime(record, self.datefmt)

        # Use origin info if available; fall back to standard
        origin_file = getattr(record, "origin_file", record.pathname)
        origin_func = getattr(record, "origin_func", record.funcName)
        origin_line = getattr(record, "origin_line", record.lineno)

        # Build the message components
        message_parts = [
            f"{risk_icon} *RISK LEVEL*: {record.levelname}",
            f":clock1: *Timestamp [UTC]*: {timestamp}",
            f":file_folder: *File*: {origin_file}",
            f":triangular_ruler: *Function*: {origin_func}",
            f":1234: *Line*: {origin_line}",
            f":memo: *Message*:\n```{record.getMessage()}```",
        ]

        # Join all parts
        message = "\n".join(message_parts)

        return message + separator


class SlackLogHandler(logging.Handler):
    def __init__(self, webhook_url, level=logging.WARNING):
        super().__init__(level=level)
        self.webhook = WebhookClient(webhook_url)

    def emit(self, record):
        try:
            log_entry = self.format(record)
            print(
                f"Sending to Slack: {log_entry[:200]}..."
            )  # Print first 200 chars for debugging

            # Send to Slack
            response = self.webhook.send(text=log_entry)

            if response.status_code == 200:
                print("Successfully sent to Slack")
            else:
                print(f"Failed to send to Slack. Status: {response.status_code}")

        except Exception as e:
            print(f"Error in SlackLogHandler: {e}")
            self.handleError(record)


class CappedFileHandler(FileHandler):
    def __init__(
        self, filename, max_bytes=30 * 1024 * 1024, mode="a", encoding=None, delay=False
    ):
        self.max_bytes = max_bytes
        super().__init__(filename, mode, encoding, delay)

    def emit(self, record):
        try:
            if (
                os.path.exists(self.baseFilename)
                and os.path.getsize(self.baseFilename) >= self.max_bytes
            ):
                self.close()
                self.stream = open(self.baseFilename, "w")
            super().emit(record)
        except Exception:
            self.handleError(record)


class IgnoreDjangoInternalErrorsFilter(logging.Filter):
    def filter(self, record):
        # Ignore logs coming from Django internal modules
        internal_paths = [
            "django/utils/log",  # most internal exceptions
            "django/core/handlers",  # request handlers
            "django/db/backends",  # DB-level exceptions
            "django/core/servers/basehttp",  # HTTP server errors
        ]
        return not any(path in record.pathname for path in internal_paths)
