"""
Logging utility for IntelliDesk AI
"""

import io
import logging
import sys
from config import Config


def _utf8_stdout():
    """
    Return a UTF-8 stream wrapping stdout.

    On Windows the default console encoding is usually cp1252, which cannot
    encode emoji or arrow characters that appear in IntelliDesk log messages.
    We reconfigure sys.stdout when possible; otherwise fall back to a
    TextIOWrapper that replaces un-encodable characters rather than crashing.
    """
    try:
        # Python 3.7+ — reconfigure the real stdout in-place
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        return sys.stdout
    except AttributeError:
        pass

    # Older Python / frozen environments
    try:
        return io.TextIOWrapper(
            sys.stdout.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )
    except AttributeError:
        # sys.stdout has no .buffer (e.g. inside some IDEs) — use as-is
        return sys.stdout


class Logger:
    """Custom logger for the application"""

    _loggers: dict = {}

    @classmethod
    def get_logger(cls, name: str = "IntelliDesk") -> logging.Logger:
        """Get or create a named logger instance."""
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers when the same logger is requested twice
        if logger.handlers:
            cls._loggers[name] = logger
            return logger

        # ── Console handler (INFO+) — UTF-8 safe ─────────────────────────────
        console_handler = logging.StreamHandler(_utf8_stdout())
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

        # ── File handler (DEBUG+) ─────────────────────────────────────────────
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        _file_fmt = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(_file_fmt)

        # ── Error file handler (ERROR+) ───────────────────────────────────────
        error_handler = logging.FileHandler(Config.ERROR_LOG_FILE, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(_file_fmt)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

        cls._loggers[name] = logger
        return logger

# Convenience functions
def info(message):
    Logger.get_logger().info(message)

def debug(message):
    Logger.get_logger().debug(message)

def warning(message):
    Logger.get_logger().warning(message)

def error(message):
    Logger.get_logger().error(message)

def critical(message):
    Logger.get_logger().critical(message)