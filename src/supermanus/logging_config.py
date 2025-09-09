# src/supermanus/logging_config.py
import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = "app.log", level: int = logging.INFO) -> None:
    """
    Sets up logging configuration for the application.

    Args:
        log_file (str): Path to the log file.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s - %(name)s - %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Log the setup
    logger.info(f"Logging configured. Log file: {log_file}, Level: {logging.getLevelName(level)}")
