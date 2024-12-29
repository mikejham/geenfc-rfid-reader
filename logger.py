"""
Logger Module
============

Centralizes logging configuration for the RFID Reader application.
Provides consistent logging across all modules with both file and console output.

Features:
    - Rotating log files with size limits
    - Separate logging levels for file and console
    - Timestamp and module information in logs
    - UTF-8 encoding support
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = None) -> logging.Logger:
    """
    Configure and return a logger instance with both file and console handlers.

    Args:
        name: Optional name for the logger. If None, returns the root logger.

    Returns:
        logging.Logger: Configured logger instance

    The logger will output:
        - INFO and above to a rotating log file (max 5MB, 5 backup files)
        - INFO and above to the console
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Get the logger
    logger = logging.getLogger(name)

    # Only configure if it hasn't been configured before
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")

        # File handler (rotating)
        file_handler = RotatingFileHandler(
            "logs/rfid_reader.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger
