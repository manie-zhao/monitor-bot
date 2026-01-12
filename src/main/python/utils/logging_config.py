"""
Logging configuration for monitor-bot
Provides centralized logging setup with file and console output
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from src.main.resources.config import settings


def setup_logging(log_level: str = None) -> logging.Logger:
    """
    Setup logging configuration for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Use provided level or default from settings
    level = log_level or settings.LOG_LEVEL
    log_level_value = getattr(logging, level.upper(), logging.INFO)

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"monitor_bot_{timestamp}.log"

    # Create logger
    logger = logging.getLogger("monitor_bot")
    logger.setLevel(log_level_value)

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )

    # File handler (detailed logs)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Console handler (less detailed)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_value)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info(f"Logging initialized - Level: {level}, Log file: {log_file}")

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (optional)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"monitor_bot.{name}")
    return logging.getLogger("monitor_bot")
