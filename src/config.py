"""
Customer360 - Central Configuration

Shared configuration for:

    - Project directories
    - Generated source data
    - CSV processing
    - Source files
    - Output files
    - Logging
    - Customer360 schema
    - Invalid-record schema
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)

DATA_DIR = BASE_DIR / "data"

# Generated source CSV files:
#
# data/
#     generated_data/
#         batch_DATE_TIME/
#             customers.csv
#             bookings.csv
#             loyalty.csv
#             support_tickets.csv
#
GENERATED_DATA_DIR = (
    DATA_DIR / "generated_data"
)

LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR = BASE_DIR / "output"


# ============================================================
# CSV SETTINGS
# ============================================================

CSV_ENCODING = "utf-8"

CSV_SEPARATOR = ","

LOW_MEMORY = True


# ============================================================
# SOURCE FILES
# ============================================================

SOURCE_FILES = {
    "customers": "customers.csv",
    "bookings": "bookings.csv",
    "loyalty": "loyalty.csv",
    "support": "support_tickets.csv",
}


# ============================================================
# OUTPUT FILES
# ============================================================

CUSTOMER360_FILE = "customer360.csv"

INVALID_RECORDS_FILE = "invalid_records.csv"


# ============================================================
# LOGGING
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

LOG_DATE_FORMAT = (
    "%Y-%m-%d %H:%M:%S"
)

PIPELINE_LOG_PREFIX = "pipeline"


# ============================================================
# CUSTOMER MASTER
# ============================================================

CUSTOMER_ID_COLUMN = "customer_id"

CUSTOMER_COLUMNS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "country",
]


# ============================================================
# BOOKING METRICS
# ============================================================

BOOKING_METRIC_COLUMNS = [
    "total_bookings",
    "completed_bookings",
    "cancelled_bookings",
    "total_spend",
    "average_booking_value",
    "last_booking_date",
]


# ============================================================
# LOYALTY METRICS
# ============================================================

LOYALTY_METRIC_COLUMNS = [
    "loyalty_points",
    "loyalty_tier",
]


# ============================================================
# SUPPORT METRICS
# ============================================================

SUPPORT_METRIC_COLUMNS = [
    "total_support_tickets",
    "open_support_tickets",
    "closed_support_tickets",
]


# ============================================================
# FINAL CUSTOMER360 SCHEMA
# ============================================================

CUSTOMER360_COLUMNS = (
    CUSTOMER_COLUMNS
    + BOOKING_METRIC_COLUMNS
    + LOYALTY_METRIC_COLUMNS
    + SUPPORT_METRIC_COLUMNS
)


# ============================================================
# INVALID RECORD SCHEMA
# ============================================================

INVALID_RECORD_COLUMNS = [
    "source_system",
    "customer_id",
    "record_id",
    "field",
    "invalid_value",
    "reason",
    "action",
]