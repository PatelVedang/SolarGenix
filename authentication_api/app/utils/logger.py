import logging
import os
from datetime import datetime, timedelta, tzinfo
from logging import FileHandler

from slack_sdk.webhook import WebhookClient

# --- UTC Timezone Class ---


class UTCTimezone(tzinfo):
    """
    A timezone class representing Coordinated Universal Time (UTC).

    This class inherits from `tzinfo` and provides implementations for the required
    methods to represent the UTC timezone. It can be used with Python's `datetime`
    objects to ensure they are timezone-aware and set to UTC.

    Methods:
        utcoffset(dt): Returns the offset from UTC, which is always zero.
        tzname(dt): Returns the name of the timezone, which is "UTC".
        dst(dt): Returns the daylight saving time offset, which is always zero for UTC.
    """

    def utcoffset(self, dt):
        return timedelta(hours=0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


utc_tz = UTCTimezone()


class TZFormatter(logging.Formatter):
    """
    A custom logging formatter that supports timezone-aware timestamps.

    Args:
        fmt (str, optional): Log message format string.
        datefmt (str, optional): Date/time format string.
        tz (datetime.tzinfo, optional): Timezone to use for timestamps. Defaults to UTCTimezone().

    Methods:
        formatTime(record, datefmt=None):
            Formats the creation time of the specified LogRecord as a timezone-aware string.
    """

    def __init__(self, fmt=None, datefmt=None, tz=UTCTimezone()):
        super().__init__(fmt, datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=self.tz)
        return dt.strftime(datefmt) if datefmt else dt.isoformat()


class SlackFormatter(TZFormatter):
    """
    SlackFormatter formats log records for Slack notifications with enhanced readability and context.

    This formatter extends TZFormatter and customizes log output to include:
    - Risk level icons based on the log level (e.g., warning, error, critical, fatal).
    - Timestamp in UTC.
    - Originating file, function, and line number (with support for custom attributes if present).
    - The log message, formatted in a code block for clarity.
    - A separator line for visual distinction between log entries.

    Attributes:
        None

    Methods:
        format(record):
            Formats a logging.LogRecord into a Slack-friendly message string, including risk icons,
            timestamp, origin details, and the log message.
    """

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
    """
    A custom logging handler that sends log records to a Slack channel via a webhook.

    Args:
        webhook_url (str): The Slack webhook URL to which log messages will be sent.
        level (int, optional): The logging level for this handler. Defaults to logging.WARNING.

    Methods:
        emit(record):
            Formats and sends the log record to the configured Slack webhook.
            If an error occurs during sending, it prints the error and calls handleError.
    """

    def __init__(self, webhook_url, level=logging.WARNING):
        super().__init__(level=level)
        self.webhook = WebhookClient(webhook_url)

    def emit(self, record):
        """Emit a log record to Slack."""
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
    """
    A custom logging file handler that caps the log file size.

    This handler extends the standard FileHandler to ensure that the log file does not exceed a specified maximum size.
    When the file reaches or exceeds `max_bytes`, it is truncated (overwritten) before new log records are written.

    Args:
        filename (str): The name of the log file.
        max_bytes (int, optional): The maximum allowed size of the log file in bytes. Defaults to 30 MB.
        mode (str, optional): The mode to open the file. Defaults to "a" (append).
        encoding (str, optional): The encoding to use for the file. Defaults to None.
        delay (bool, optional): If True, file opening is deferred until the first call to emit(). Defaults to False.

    Methods:
        emit(record):
            Writes a log record to the file. If the file size exceeds `max_bytes`, the file is truncated before writing.
    """
    def __init__(
        self, filename, max_bytes=30 * 1024 * 1024, mode="a", encoding="utf-8", delay=False
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
    """
    A logging filter that ignores log records originating from Django's internal modules.

    This filter is useful for suppressing noise from common internal Django exceptions and errors,
    such as those from request handlers, database backends, and HTTP server errors, allowing
    application-specific logs to be more visible.

    Returns:
        bool: True if the log record does not originate from specified Django internal paths; False otherwise.
    """
    def filter(self, record):
        # Ignore logs coming from Django internal modules
        internal_paths = [
            "django/utils/log",  # most internal exceptions
            "django/core/handlers",  # request handlers
            "django/db/backends",  # DB-level exceptions
            "django/core/servers/basehttp",  # HTTP server errors
        ]
        return not any(path in record.pathname for path in internal_paths)
