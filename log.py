import logging
import os
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from typing import List, Literal

# os.environ["LOG_DIR_PATH"] = 'D:\python_project\spider\logs'
LOG_DIR_PATH = os.getenv("LOG_DIR_PATH")
PROJECT_NAME = os.getenv("PROJECT_NAME")

# Check if the environment variable contains a log directory path
if not LOG_DIR_PATH:
    LOG_DIR_PATH = './logs'
if not PROJECT_NAME:
    PROJECT_NAME = 'project'


def create_logger(
        log_name: str = PROJECT_NAME,
        log_dir_path: str = None,
        log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
):
    # Configure the log handler for the given log_name
    logger = logging.getLogger(log_name)
    if not logger.handlers:
        if not log_dir_path:
            log_dir_path = LOG_DIR_PATH

        # Define the log directory and log file name
        log_dir_path = Path(log_dir_path)
        log_dir_path.mkdir(parents=True, exist_ok=True)  # Create the log directory; ignore if it already exists
        log_file_path = log_dir_path / f"{log_name}.log"

        # Set the log level
        logger.setLevel(getattr(logging, log_level))
        log_format = '%(asctime)s | %(levelname)s | %(message)s'

        # File handler: rotate the log file daily
        file_handler = TimedRotatingFileHandler(
            str(log_file_path),
            when="midnight",
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )

        file_handler.setFormatter(logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S'))

        # Console handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(log_format))

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


if __name__ == '__main__':
    logger = create_logger(log_level="DEBUG")
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
