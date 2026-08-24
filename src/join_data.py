"""
Customer360 - Data Joining

Purpose
-------
Combine:
    Customer Master
    + Booking Metrics
    + Loyalty Metrics
    + Support Metrics

Customer master is the base table.

Business Rule
-------------
Every valid customer must appear in Customer360,
even when booking, loyalty, or support information
is unavailable.
"""

import pandas as pd

from src.config import (
    CUSTOMER_COLUMNS,
    CUSTOMER360_COLUMNS,
)

from src.logger import get_logger


logger = get_logger()


# ============================================================
# MAIN JOIN
# ============================================================

def join_customer_data(data):
    """
    Build the final Customer360 dataset.
    """

    logger.info(
        "Customer360 join started"
    )

    # --------------------------------------------------------
    # 1. Customer master
    # --------------------------------------------------------
    # Customer table is the base.
    # Therefore every valid customer is retained.

    customer360 = (
        data["customers"][
            CUSTOMER_COLUMNS
        ]
        .set_index("customer_id")
    )

    # --------------------------------------------------------
    # 2. Join booking metrics
    # --------------------------------------------------------

    booking_metrics = (
        data["booking_metrics"]
        .set_index("customer_id")
    )

    customer360 = customer360.join(
        booking_metrics,
        how="left",
    )

    # --------------------------------------------------------
    # 3. Join loyalty metrics
    # --------------------------------------------------------

    loyalty_metrics = (
        data["loyalty_metrics"]
        .set_index("customer_id")
    )

    customer360 = customer360.join(
        loyalty_metrics,
        how="left",
    )

    # --------------------------------------------------------
    # 4. Join support metrics
    # --------------------------------------------------------

    support_metrics = (
        data["support_metrics"]
        .set_index("customer_id")
    )

    customer360 = customer360.join(
        support_metrics,
        how="left",
    )

    # --------------------------------------------------------
    # 5. Convert customer_id back to a column
    # --------------------------------------------------------

    customer360 = customer360.reset_index()

    # --------------------------------------------------------
    # 6. Missing numeric metrics = 0
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

    customer360[numeric_columns] = (
        customer360[numeric_columns]
        .fillna(0)
    )

    # --------------------------------------------------------
    # 7. Arrange final Customer360 columns
    # --------------------------------------------------------

    customer360 = customer360[
        CUSTOMER360_COLUMNS
    ]

    logger.info(
        "Customer360 join completed | records=%d",
        len(customer360),
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "customer360": customer360,
        "batch_folder": data.get(
            "batch_folder"
        ),
        "invalid_records": data.get(
            "invalid_records",
            pd.DataFrame(),
        ),
    }