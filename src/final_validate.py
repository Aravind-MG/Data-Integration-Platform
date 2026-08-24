"""
Customer360 - Final Validation

Checks the final Customer360 data before writing output.

Rules
-----
- Final dataset must not be empty.
- All required Customer360 columns must exist.
- customer_id must exist and be unique.
- Numeric metrics must contain valid numeric values.

This file only validates.
It does not modify the data.
"""

import pandas as pd

from src.config import (
    CUSTOMER360_COLUMNS,
    CUSTOMER_ID_COLUMN,
)

from src.logger import get_logger


logger = get_logger()


# ============================================================
# FINAL VALIDATION
# ============================================================

def validate_final_data(df):
    """
    Validate the final Customer360 DataFrame.

    Returns:
        Same DataFrame if all checks pass.
    """

    logger.info(
        "Final Customer360 validation started"
    )

    # --------------------------------------------------------
    # Check dataset is not empty.
    # --------------------------------------------------------

    if df.empty:
        raise ValueError(
            "Final Customer360 dataset is empty"
        )

    # --------------------------------------------------------
    # Check required columns.
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in CUSTOMER360_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing Customer360 columns: "
            + ", ".join(missing_columns)
        )

    # --------------------------------------------------------
    # Check customer_id.
    # --------------------------------------------------------

    if (
        CUSTOMER_ID_COLUMN not in df.columns
    ):
        raise ValueError(
            "customer_id column is missing"
        )

    if df[CUSTOMER_ID_COLUMN].isna().any():
        raise ValueError(
            "Final dataset contains missing customer_id"
        )

    if df[CUSTOMER_ID_COLUMN].duplicated().any():
        raise ValueError(
            "Final dataset contains duplicate customer_id"
        )

    # --------------------------------------------------------
    # Check numeric metrics.
    # --------------------------------------------------------

    numeric_columns = [
        "total_bookings",
        "completed_bookings",
        "cancelled_bookings",
        "total_spend",
        "average_booking_value",
        "loyalty_points",
        "total_support_tickets",
        "open_support_tickets",
        "closed_support_tickets",
    ]

    for column in numeric_columns:

        values = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        invalid = (
            df[column].notna()
            & values.isna()
        )

        if invalid.any():
            raise ValueError(
                f"Invalid numeric values in "
                f"{column}"
            )

    logger.info(
        "Final Customer360 validation passed | "
        "records=%d | columns=%d",
        len(df),
        len(df.columns),
    )

    return df