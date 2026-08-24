"""
Customer360 - Centralized Logger

One log file is created for each pipeline execution.

Example:

logs/
└── batch_2026-08-23_23-14-55-712759/
    └── pipeline_2026-08-23_23-14-55-712759.log
"""

import logging
from pathlib import Path

from src.config import (
    LOG_DIR,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    PIPELINE_LOG_PREFIX,
)


# ============================================================
# LOGGER
# ============================================================

LOGGER_NAME = "Customer360"

logger = logging.getLogger(
    LOGGER_NAME
)

logger.setLevel(
    logging.INFO
)

logger.propagate = False


# ============================================================
# INITIALIZE LOGGER
# ============================================================

def initialize_logger(batch_id):
    """
    Initialize logging for the current pipeline batch.

    batch_id can be either:
        - string
        - pathlib.Path

    Example:
        batch_2026-08-23_23-14-55-712759
    """

    # --------------------------------------------------------
    # Convert Path to string safely
    # --------------------------------------------------------

    batch_id = Path(batch_id).name

    # --------------------------------------------------------
    # Remove handlers from previous execution
    # --------------------------------------------------------

    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # --------------------------------------------------------
    # Create batch-specific log directory
    # --------------------------------------------------------

    log_dir = (
        Path(LOG_DIR)
        / batch_id
    )

    log_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Create log filename
    # --------------------------------------------------------

    timestamp = batch_id

    if timestamp.startswith("batch_"):
        timestamp = timestamp[len("batch_"):]

    log_file = (
        log_dir
        / f"{PIPELINE_LOG_PREFIX}_{timestamp}.log"
    )

    # --------------------------------------------------------
    # Create file handler
    # --------------------------------------------------------

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    # --------------------------------------------------------
    # Initial log
    # --------------------------------------------------------

    logger.info(
        "=" * 70
    )

    logger.info(
        "Customer360 Pipeline Started"
    )

    logger.info(
        "Batch ID: %s",
        batch_id,
    )

    logger.info(
        "Log File: %s",
        log_file,
    )

    logger.info(
        "=" * 70
    )

    return log_file


# ============================================================
# GET LOGGER
# ============================================================

def get_logger():
    """
    Return the shared Customer360 logger.
    """

    return logger


# ============================================================
# PIPELINE COMPLETION
# ============================================================

def log_pipeline_end(
    batch_id,
    customer_count,
    invalid_count,
):
    """
    Log successful pipeline completion.
    """

    logger.info(
        "=" * 70
    )

    logger.info(
        "Customer360 Pipeline Completed Successfully"
    )

    logger.info(
        "Batch ID: %s",
        Path(batch_id).name,
    )

    logger.info(
        "Final Customers: %d",
        customer_count,
    )

    logger.info(
        "Invalid Records: %d",
        invalid_count,
    )

    logger.info(
        "=" * 70
    )


# ============================================================
# PIPELINE FAILURE
# ============================================================

def log_pipeline_error(error):
    """
    Log an unexpected pipeline error including traceback.
    """

    logger.exception(
        "Customer360 Pipeline Failed | %s",
        error,
    )