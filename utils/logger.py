"""
logger.py - Centralised logging setup.
Call get_logger(__name__) in any module to get a pre-configured logger.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from config.settings import LOG_LEVEL, LOG_FILE, OUTPUT_DIR


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes to both stdout and a rotating log file."""

    # Make sure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when the module is imported multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler (5 MB max, keep 3 backups)
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
