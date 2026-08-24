"""
Customer360 - Source Data Reader

Purpose
-------
Read the four source CSV files from one timestamped batch.

Source structure:

data/
└── generated_data/
    └── batch_YYYY-MM-DD_HH-MM-SS/
        ├── customers.csv
        ├── bookings.csv
        ├── loyalty.csv
        └── support_tickets.csv

This module only:
- Finds the latest source batch.
- Checks required files.
- Reads each CSV.
- Logs basic file information.
- Returns the source DataFrames.

Validation, duplicate removal, cleaning, aggregation,
and joining are handled by later pipeline stages.
"""

from pathlib import Path

import pandas as pd

from src.config import (
    GENERATED_DATA_DIR,
    SOURCE_FILES,
    CSV_ENCODING,
    LOW_MEMORY,
)

from src.logger import get_logger


logger = get_logger()


# ============================================================
# FIND LATEST BATCH
# ============================================================

def get_latest_batch():
    """
    Find the latest generated source-data batch.

    Returns:
        str: Batch folder name.
    """

    batches = sorted(
        path
        for path in GENERATED_DATA_DIR.glob(
            "batch_*"
        )
        if path.is_dir()
    )

    if not batches:
        raise FileNotFoundError(
            "No source batch found in "
            f"{GENERATED_DATA_DIR}"
        )

    batch = batches[-1]

    logger.info(
        "Source batch selected | batch=%s",
        batch.name,
    )

    return batch.name


# ============================================================
# READ ONE CSV
# ============================================================

def read_csv(
    batch_dir,
    file_name,
    source_name,
):
    """
    Read one source CSV file.

    Args:
        batch_dir: Current batch directory.
        file_name: CSV filename.
        source_name: Name used in logs.

    Returns:
        pandas.DataFrame
    """

    file_path = (
        batch_dir / file_name
    )

    if not file_path.is_file():

        raise FileNotFoundError(
            f"Missing source file: {file_path}"
        )

    logger.info(
        "Reading %s | file=%s",
        source_name,
        file_path,
    )

    df = pd.read_csv(
        file_path,
        encoding=CSV_ENCODING,
        low_memory=LOW_MEMORY,
    )

    logger.info(
        "%s | records=%d | columns=%d",
        source_name,
        len(df),
        len(df.columns),
    )

    return df


# ============================================================
# READ ALL SOURCE DATA
# ============================================================

def read_source_data(
    batch_id=None,
):
    """
    Read all four source CSV files from one batch.

    If batch_id is not provided, the latest generated
    batch is automatically selected.

    Returns:
        dict:
            batch_folder
            batch_dir
            customers
            bookings
            loyalty
            support
    """

    # --------------------------------------------------------
    # Select batch
    # --------------------------------------------------------

    if batch_id is None:
        batch_id = get_latest_batch()

    batch_dir = (
        GENERATED_DATA_DIR / batch_id
    )

    if not batch_dir.is_dir():

        raise FileNotFoundError(
            f"Source batch not found: "
            f"{batch_dir}"
        )

    logger.info(
        "Source reading started | batch=%s",
        batch_id,
    )

    # --------------------------------------------------------
    # Customers
    # --------------------------------------------------------

    customers = read_csv(
        batch_dir,
        SOURCE_FILES["customers"],
        "Customer System",
    )

    # --------------------------------------------------------
    # Bookings
    # --------------------------------------------------------

    bookings = read_csv(
        batch_dir,
        SOURCE_FILES["bookings"],
        "Booking System",
    )

    # --------------------------------------------------------
    # Loyalty
    # --------------------------------------------------------

    loyalty = read_csv(
        batch_dir,
        SOURCE_FILES["loyalty"],
        "Loyalty System",
    )

    # --------------------------------------------------------
    # Support
    # --------------------------------------------------------

    support = read_csv(
        batch_dir,
        SOURCE_FILES["support"],
        "Support System",
    )

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    logger.info(
        "Source reading completed | "
        "batch=%s",
        batch_id,
    )

    return {
        "batch_folder": batch_id,
        "batch_dir": batch_dir,
        "customers": customers,
        "bookings": bookings,
        "loyalty": loyalty,
        "support": support,
    }