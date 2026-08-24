"""
Customer360 - Data Cleaning

Rules
-----
1. Remove completely duplicate rows from all source tables.
2. Customer master must contain only one row per customer_id.
3. Keep the first customer record when duplicate customer_id values exist.
4. Multiple bookings, loyalty records, and support tickets are valid.
5. Invalid customer_id records are already handled by validation.
"""

from src.logger import get_logger


logger = get_logger()


# ============================================================
# REMOVE DUPLICATE ROWS
# ============================================================

def remove_duplicates(df, table_name):
    """
    Remove completely identical rows.
    """

    before = len(df)

    df = df.drop_duplicates(
        ignore_index=True
    )

    removed = before - len(df)

    if removed > 0:
        logger.info(
            "%s | duplicate rows removed=%d",
            table_name,
            removed,
        )

    return df


# ============================================================
# CLEAN CUSTOMER MASTER
# ============================================================

def clean_customers(df):
    """
    Clean customer master.

    Removes:
    1. Completely duplicate rows.
    2. Duplicate customer_id records.

    The first customer record is retained.
    """

    df = remove_duplicates(
        df,
        "Customer System",
    )

    # Keep only the first record for each customer_id.
    before = len(df)

    df = df.drop_duplicates(
        subset="customer_id",
        keep="first",
        ignore_index=True,
    )

    removed = before - len(df)

    if removed > 0:
        logger.warning(
            "Customer System | "
            "duplicate customer_id records removed=%d",
            removed,
        )

    return df


# ============================================================
# MAIN CLEANING FUNCTION
# ============================================================

def clean_source_data(data):
    """
    Clean all validated source tables.
    """

    logger.info(
        "Data cleaning started"
    )

    # Customer master.
    customers = clean_customers(
        data["customers"]
    )

    # Related source tables.
    bookings = remove_duplicates(
        data["bookings"],
        "Booking System",
    )

    loyalty = remove_duplicates(
        data["loyalty"],
        "Loyalty System",
    )

    support = remove_duplicates(
        data["support"],
        "Support System",
    )

    logger.info(
        "Data cleaning completed"
    )

    return {
        "batch_folder": data["batch_folder"],
        "customers": customers,
        "bookings": bookings,
        "loyalty": loyalty,
        "support": support,
        "invalid_records": data["invalid_records"],
    }