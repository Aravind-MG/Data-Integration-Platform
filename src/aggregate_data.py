"""
Customer360 - Data Aggregation

Purpose
-------
Calculate customer-level metrics from cleaned source data.

Business Rules
--------------
Bookings:
- Count all bookings.
- Count completed bookings.
- Count cancelled bookings.
- Only completed booking amounts contribute to total_spend.
- average_booking_value = total_spend / completed_bookings.
- If there are no completed bookings, average_booking_value = 0.

Loyalty:
- Sum loyalty points for each customer.
- Keep the available membership type and loyalty tier.

Support:
- Count all support tickets.
- Count open tickets.
- Count closed tickets.
"""

import pandas as pd

from src.logger import get_logger


logger = get_logger()


# ============================================================
# BOOKING AGGREGATION
# ============================================================

def aggregate_bookings(df):
    """
    Calculate booking metrics for each customer.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "total_bookings",
                "completed_bookings",
                "cancelled_bookings",
                "total_spend",
                "average_booking_value",
                "last_booking_date",
            ]
        )

    df = df.copy()

    # Normalize booking status.
    df["status"] = (
        df["status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # Convert amount to numeric.
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    )

    # Convert booking date.
    df["booking_date"] = pd.to_datetime(
        df["booking_date"],
        errors="coerce",
    )

    # Only completed bookings contribute to spending.
    df["completed_amount"] = df["amount"].where(
        df["status"] == "completed",
        0,
    )

    result = (
        df.groupby("customer_id")
        .agg(
            total_bookings=(
                "customer_id",
                "count",
            ),

            completed_bookings=(
                "status",
                lambda x: (
                    x == "completed"
                ).sum(),
            ),

            cancelled_bookings=(
                "status",
                lambda x: (
                    x == "cancelled"
                ).sum(),
            ),

            total_spend=(
                "completed_amount",
                "sum",
            ),

            last_booking_date=(
                "booking_date",
                "max",
            ),
        )
        .reset_index()
    )

    # Average = total spend / completed bookings.
    result["average_booking_value"] = (
        result["total_spend"]
        .div(
            result["completed_bookings"]
        )
        .fillna(0)
    )

    return result[
        [
            "customer_id",
            "total_bookings",
            "completed_bookings",
            "cancelled_bookings",
            "total_spend",
            "average_booking_value",
            "last_booking_date",
        ]
    ]


# ============================================================
# LOYALTY AGGREGATION
# ============================================================

def aggregate_loyalty(df):
    """
    Calculate loyalty metrics for each customer.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "membership_type",
                "loyalty_points",
                "loyalty_tier",
            ]
        )

    df = df.copy()

    # Convert loyalty points to numeric.
    df["loyalty_points"] = pd.to_numeric(
        df["loyalty_points"],
        errors="coerce",
    )

    # Sum loyalty points per customer.
    points = (
    df.groupby("customer_id")
    .agg(
        loyalty_points=("loyalty_points", "sum")
    )
)

    # Keep the last available membership/tier.
    loyalty_info = (
        df[
            [
                "customer_id",
                "membership_type",
                "loyalty_tier",
            ]
        ]
        .drop_duplicates(
            "customer_id",
            keep="last",
        )
        .set_index("customer_id")
    )

    result = points.join(
        loyalty_info,
        how="left",
    )

    return result.reset_index()[
        [
            "customer_id",
            "membership_type",
            "loyalty_points",
            "loyalty_tier",
        ]
    ]


# ============================================================
# SUPPORT AGGREGATION
# ============================================================

def aggregate_support(df):
    """
    Calculate support ticket metrics for each customer.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "total_support_tickets",
                "open_support_tickets",
                "closed_support_tickets",
            ]
        )

    df = df.copy()

    # Normalize status.
    df["status"] = (
        df["status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    result = (
        df.groupby("customer_id")
        .agg(
            total_support_tickets=(
                "customer_id",
                "size",
            ),

            open_support_tickets=(
                "status",
                lambda x: (
                    x == "open"
                ).sum(),
            ),

            closed_support_tickets=(
                "status",
                lambda x: (
                    x == "closed"
                ).sum(),
            ),
        )
        .reset_index()
    )

    return result


# ============================================================
# MAIN AGGREGATION
# ============================================================

def aggregate_data(data):
    """
    Calculate all customer-level metrics.
    """

    logger.info(
        "Data aggregation started"
    )

    booking_metrics = aggregate_bookings(
        data["bookings"]
    )

    loyalty_metrics = aggregate_loyalty(
        data["loyalty"]
    )

    support_metrics = aggregate_support(
        data["support"]
    )

    logger.info(
        "Data aggregation completed"
    )

    return {
        "booking_metrics": booking_metrics,
        "loyalty_metrics": loyalty_metrics,
        "support_metrics": support_metrics,
        "batch_folder": data.get(
            "batch_folder"
        ),
        "invalid_records": data.get(
            "invalid_records",
            pd.DataFrame(),
        ),
    }