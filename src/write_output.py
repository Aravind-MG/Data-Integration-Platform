"""
Customer360 - Output Writer

Creates:

output/
└── batch_YYYY-MM-DD_HH-MM-SS/
    ├── customer360.csv
    └── invalid_records.csv
"""

from pathlib import Path

import pandas as pd

from src.config import (
    OUTPUT_DIR,
    CUSTOMER360_FILE,
    INVALID_RECORDS_FILE,
    INVALID_RECORD_COLUMNS,
    CSV_ENCODING,
    CSV_SEPARATOR,
)

from src.logger import get_logger


logger = get_logger()


# ============================================================
# PREPARE CUSTOMER360
# ============================================================

def prepare_customer360(df):
    """
    Prepare Customer360 data for CSV output.

    Rules:
    - Numeric count/amount fields -> whole numbers.
    - Average booking value -> 2 decimal places.
    - Date -> YYYY-MM-DD.
    - Missing values -> NULL.
    """

    df = df.sort_values(
    "customer_id"
).reset_index(
    drop=True
)

    df = df.copy()

    # Whole-number fields.
    integer_columns = [
        "total_bookings",
        "completed_bookings",
        "cancelled_bookings",
        "total_spend",
        "loyalty_points",
        "total_support_tickets",
        "open_support_tickets",
        "closed_support_tickets",
    ]

    for column in integer_columns:

        if column in df.columns:
            df[column] = (
                pd.to_numeric(
                    df[column],
                    errors="coerce",
                )
                .round()
                .astype("Int64")
            )

    # Average booking value.
    if "average_booking_value" in df.columns:

        df["average_booking_value"] = (
            pd.to_numeric(
                df["average_booking_value"],
                errors="coerce",
            )
            .round(2)
        )

    # Last booking date.
    if "last_booking_date" in df.columns:

        df["last_booking_date"] = (
            pd.to_datetime(
                df["last_booking_date"],
                errors="coerce",
            )
            .dt.strftime("%Y-%m-%d")
        )

    # Missing values.
    return df.fillna("NULL")


# ============================================================
# PREPARE INVALID RECORDS
# ============================================================

def prepare_invalid_records(df):
    """
    Ensure invalid records follow the required schema.
    """

    if df is None or df.empty:
        return pd.DataFrame(
            columns=INVALID_RECORD_COLUMNS
        )

    df = df.copy()

    for column in INVALID_RECORD_COLUMNS:

        if column not in df.columns:
            df[column] = pd.NA

    return df[
        INVALID_RECORD_COLUMNS
    ].fillna("NULL")


# ============================================================
# MAIN OUTPUT
# ============================================================

def write_output(data):
    """
    Write Customer360 and invalid-record CSV files.
    """

    logger.info(
        "Output writing started"
    )

    customer360 = data.get(
        "customer360"
    )

    invalid_records = data.get(
        "invalid_records"
    )

    batch_folder = data.get(
        "batch_folder"
    )

    if customer360 is None:
        raise ValueError(
            "Customer360 data is missing"
        )

    if batch_folder is None:
        raise ValueError(
            "Batch folder is missing"
        )

    # --------------------------------------------------------
    # Create output directory.
    # --------------------------------------------------------

    output_dir = (
        Path(OUTPUT_DIR)
        / Path(batch_folder).name
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Prepare Customer360.
    # --------------------------------------------------------

    customer360 = prepare_customer360(
        customer360
    )

    # --------------------------------------------------------
    # Write Customer360.
    # --------------------------------------------------------

    customer360_path = (
        output_dir
        / CUSTOMER360_FILE
    )

    customer360.to_csv(
        customer360_path,
        index=False,
        encoding=CSV_ENCODING,
        sep=CSV_SEPARATOR,
    )

    # --------------------------------------------------------
    # Prepare invalid records.
    # --------------------------------------------------------

    invalid_records = prepare_invalid_records(
        invalid_records
    )

    # --------------------------------------------------------
    # Write invalid records.
    # --------------------------------------------------------

    invalid_records_path = (
        output_dir
        / INVALID_RECORDS_FILE
    )

    invalid_records.to_csv(
        invalid_records_path,
        index=False,
        encoding=CSV_ENCODING,
        sep=CSV_SEPARATOR,
    )

    logger.info(
        "Output writing completed | "
        "Customer360 records=%d | "
        "Invalid records=%d | "
        "directory=%s",
        len(customer360),
        len(invalid_records),
        output_dir,
    )

    return {
        "output_dir": output_dir,
        "customer360": customer360_path,
        "invalid_records": invalid_records_path,
    }