"""
Logging utilities for Z platform
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with file and console handlers

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level
        format_str: Custom format string

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Default format
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(format_str)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_video_logger(video_id: str, base_log_dir: str = "logs") -> logging.Logger:
    """
    Create a logger for a specific video processing session

    Args:
        video_id: YouTube video ID
        base_log_dir: Base directory for log files

    Returns:
        Logger instance for this video
    """
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(base_log_dir, f"{video_id}_{timestamp}.log")

    logger = setup_logger(
        name=f"z2.video.{video_id}",
        log_file=log_file,
        level=logging.INFO
    )

    return logger


# Main application logger
def get_app_logger() -> logging.Logger:
    """Get the main application logger"""
    return setup_logger(
        name="z2",
        log_file="logs/z2.log",
        level=logging.INFO
    )
