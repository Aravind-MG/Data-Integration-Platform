"""
Customer360 - Data Validation

Rules
-----
1. customer_id is the only field that can reject a record.
2. Missing/invalid/unknown customer_id -> reject complete row.
3. Other invalid fields -> replace with NULL and continue.
4. Every invalid value is stored in invalid_records.
5. Valid status values are normalized.
"""

import pandas as pd

from src.config import INVALID_RECORD_COLUMNS
from src.logger import get_logger


logger = get_logger()


# ============================================================
# BASIC HELPERS
# ============================================================

def text(series):
    """Convert values to text and remove extra spaces."""
    return series.astype("string").str.strip()


def missing(series):
    """Return True for NULL or blank values."""
    return series.isna() | text(series).eq("")


# ============================================================
# INVALID RECORD
# ============================================================

def invalid_record(
    df,
    mask,
    source,
    record_column,
    field,
    reason,
    action,
):
    """
    Create invalid-record information for matching rows.
    """

    records = []

    for index in df.index[mask]:

        customer_id = df.at[
            index,
            "customer_id",
        ]

        record_id = (
            df.at[index, record_column]
            if record_column in df.columns
            else None
        )

        value = df.at[
            index,
            field,
        ]

        customer_id = (
            "NULL"
            if pd.isna(customer_id)
            else str(customer_id)
        )

        record_id = (
            "NULL"
            if pd.isna(record_id)
            else str(record_id)
        )

        value = (
            "NULL"
            if pd.isna(value)
            else str(value)
        )

        logger.warning(
            "%s | customer_id=%s | record_id=%s | "
            "field=%s | invalid_value=%s | "
            "reason=%s | action=%s",
            source,
            customer_id,
            record_id,
            field,
            value,
            reason,
            action,
        )

        records.append({
            "source_system": source,
            "customer_id": customer_id,
            "record_id": record_id,
            "field": field,
            "invalid_value": value,
            "reason": reason,
            "action": action,
        })

    return records


# ============================================================
# CUSTOMER ID VALIDATION
# ============================================================

def validate_customer_id(
    df,
    source,
    record_column,
    valid_ids=None,
):
    """
    Validate customer_id.

    Missing or invalid customer_id:
        -> record rejected

    Unknown customer_id:
        -> record rejected
    """

    customer_id = text(
        df["customer_id"]
    )

    # --------------------------------------------------------
    # Missing customer_id
    # --------------------------------------------------------

    missing_id = missing(
        customer_id
    )

    # --------------------------------------------------------
    # Wrong customer_id format
    #
    # Valid example:
    # C001
    # C025
    # C100
    # --------------------------------------------------------

    invalid_id = (
        ~customer_id.str.match(
            r"^C\d+$",
            na=False,
        )
        & ~missing_id
    )

    # --------------------------------------------------------
    # Customer does not exist
    # --------------------------------------------------------

    unknown_id = pd.Series(
        False,
        index=df.index,
    )

    if valid_ids is not None:

        unknown_id = (
            ~customer_id.isin(valid_ids)
            & ~missing_id
            & ~invalid_id
        )

    # --------------------------------------------------------
    # Complete rejection mask
    # --------------------------------------------------------

    rejected = (
        missing_id
        | invalid_id
        | unknown_id
    )

    records = []

    # --------------------------------------------------------
    # Missing ID records
    # --------------------------------------------------------

    records.extend(
        invalid_record(
            df,
            missing_id,
            source,
            record_column,
            "customer_id",
            "Missing customer_id",
            "Record rejected",
        )
    )

    # --------------------------------------------------------
    # Invalid ID records
    # --------------------------------------------------------

    records.extend(
        invalid_record(
            df,
            invalid_id,
            source,
            record_column,
            "customer_id",
            "Invalid customer_id",
            "Record rejected",
        )
    )

    # --------------------------------------------------------
    # Unknown ID records
    # --------------------------------------------------------

    records.extend(
        invalid_record(
            df,
            unknown_id,
            source,
            record_column,
            "customer_id",
            "customer_id does not exist",
            "Record rejected",
        )
    )

    # ========================================================
    # REJECTION SUMMARY
    # ========================================================

    if rejected.any():

        reasons = []

        missing_count = int(
            missing_id.sum()
        )

        invalid_count = int(
            invalid_id.sum()
        )

        unknown_count = int(
            unknown_id.sum()
        )

        if missing_count:
            reasons.append(
                f"Missing customer_id={missing_count}"
            )

        if invalid_count:
            reasons.append(
                f"Invalid customer_id={invalid_count}"
            )

        if unknown_count:
            reasons.append(
                f"customer_id does not exist={unknown_count}"
            )

        logger.warning(
            "%s | rejected records=%d | reasons: %s",
            source,
            int(rejected.sum()),
            ", ".join(reasons),
        )

    return rejected, records


# ============================================================
# FIELD VALIDATORS
# ============================================================

def invalid_name(series):
    """Check whether a name is missing or malformed."""

    values = text(series)

    return (
        missing(values)
        | values.str.contains(
            r"[^A-Za-zÀ-ÿ' -]",
            na=False,
        )
    )


def invalid_email(series):
    """Check basic email format."""

    values = text(series)

    return (
        missing(values)
        | ~values.str.match(
            r"^[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            na=False,
        )
    )


def invalid_phone(series):
    """Check for a valid 10-digit phone number."""

    values = (
        text(series)
        .str.replace(
            r"\.0$",
            "",
            regex=True,
        )
    )

    return (
        missing(values)
        | ~values.str.fullmatch(
            r"\d{10}",
            na=False,
        )
    )


def invalid_record_id(series, prefix):
    """Check booking_id or ticket_id."""

    values = text(series)

    return (
        missing(values)
        | ~values.str.match(
            rf"^{prefix}\d+$",
            na=False,
        )
    )


def invalid_date(series):
    """
    Check whether a date is missing, invalid,
    or in the future.
    """

    values = pd.to_datetime(
        text(series),
        format="%Y-%m-%d",
        errors="coerce",
    )

    return (
        values.isna()
        | values.gt(pd.Timestamp.now())
    )


def invalid_amount(series):
    """Check missing, non-numeric or negative amount."""

    values = pd.to_numeric(
        series,
        errors="coerce",
    )

    return (
        values.isna()
        | values.lt(0)
    )


def invalid_points(series):
    """Check missing, non-numeric or negative points."""

    values = pd.to_numeric(
        series,
        errors="coerce",
    )

    return (
        values.isna()
        | values.lt(0)
    )


# ============================================================
# STATUS
# ============================================================

def normalize_status(series, valid_values):
    """
    Convert valid status values to standard case.

    Example:

        COMPLETED -> Completed
        completed -> Completed
        CANCELLED -> Cancelled
    """

    values = text(series).str.lower()

    mapping = {
        value.lower(): value
        for value in valid_values
    }

    return values.replace(mapping)


def invalid_status(series, valid_values):
    """Check whether status is missing or invalid."""

    values = text(series).str.lower()

    return (
        missing(values)
        | ~values.isin(
            [
                value.lower()
                for value in valid_values
            ]
        )
    )


# ============================================================
# VALIDATION RULES
# ============================================================

CUSTOMER_RULES = {

    "first_name": (
        invalid_name,
        "Missing or invalid first_name",
    ),

    "last_name": (
        invalid_name,
        "Missing or invalid last_name",
    ),

    "email": (
        invalid_email,
        "Missing or invalid email",
    ),

    "phone": (
        invalid_phone,
        "Missing or invalid phone",
    ),

    "country": (
        missing,
        "Missing country",
    ),
}


BOOKING_RULES = {

    "booking_id": (
        lambda x: invalid_record_id(x, "B"),
        "Missing or invalid booking_id",
    ),

    "booking_date": (
        invalid_date,
        "Missing or invalid booking_date",
    ),

    "amount": (
        invalid_amount,
        "Missing, invalid, or negative amount",
    ),

    "status": (
        lambda x: invalid_status(
            x,
            ["Completed", "Cancelled"],
        ),
        "Missing or invalid booking status",
    ),
}


LOYALTY_RULES = {

    "membership_type": (
        missing,
        "Missing membership_type",
    ),

    "loyalty_points": (
        invalid_points,
        "Missing, invalid, or negative loyalty_points",
    ),

    "loyalty_tier": (
        lambda x: invalid_status(
            x,
            [
                "Bronze",
                "Silver",
                "Gold",
                "Platinum",
            ],
        ),
        "Missing or invalid loyalty_tier",
    ),
}


SUPPORT_RULES = {

    "ticket_id": (
        lambda x: invalid_record_id(x, "T"),
        "Missing or invalid ticket_id",
    ),

    "issue_type": (
        missing,
        "Missing issue_type",
    ),

    "created_date": (
        invalid_date,
        "Missing or invalid created_date",
    ),

    "status": (
        lambda x: invalid_status(
            x,
            ["Open", "Closed"],
        ),
        "Missing or invalid support status",
    ),
}


# ============================================================
# VALIDATE OTHER FIELDS
# ============================================================

def validate_fields(
    df,
    rules,
    source,
    record_column,
):
    """
    Validate non-customer_id fields.

    Invalid fields are replaced with NULL.
    The record is NOT rejected.
    """

    records = []

    for field, (check, reason) in rules.items():

        if field not in df.columns:
            continue

        bad = check(
            df[field]
        )

        if not bad.any():
            continue

        # ----------------------------------------------------
        # Store invalid information
        # ----------------------------------------------------

        records.extend(
            invalid_record(
                df,
                bad,
                source,
                record_column,
                field,
                reason,
                "Replaced with NULL",
            )
        )

        # ----------------------------------------------------
        # Replace invalid value with NULL
        # ----------------------------------------------------

        df.loc[
            bad,
            field,
        ] = pd.NA

        logger.warning(
            "%s | field=%s | invalid records=%d | "
            "action=Replaced with NULL",
            source,
            field,
            int(bad.sum()),
        )

    return df, records


# ============================================================
# VALIDATE ONE TABLE
# ============================================================

def validate_table(
    df,
    source,
    record_column,
    rules,
    valid_ids=None,
):
    """
    Validate one source table.

    customer_id is always validated first.

    Invalid customer_id:
        -> reject row

    Other invalid fields:
        -> replace with NULL
    """

    df = df.copy()

    # --------------------------------------------------------
    # Clean text spacing
    # --------------------------------------------------------

    for column in df.columns:

        if df[column].dtype == "object":

            df[column] = text(
                df[column]
            )

    # --------------------------------------------------------
    # Normalize phone
    # --------------------------------------------------------

    if "phone" in df.columns:

        df["phone"] = (
            text(df["phone"])
            .str.replace(
                r"\.0$",
                "",
                regex=True,
            )
        )

    # --------------------------------------------------------
    # Normalize status
    # --------------------------------------------------------

    if "status" in df.columns:

        if source == "Booking System":

            df["status"] = normalize_status(
                df["status"],
                [
                    "Completed",
                    "Cancelled",
                ],
            )

        elif source == "Support System":

            df["status"] = normalize_status(
                df["status"],
                [
                    "Open",
                    "Closed",
                ],
            )

    # ========================================================
    # STEP 1: CUSTOMER ID
    # ========================================================

    rejected, records = validate_customer_id(
        df,
        source,
        record_column,
        valid_ids,
    )

    # ========================================================
    # STEP 2: KEEP ONLY VALID CUSTOMER IDs
    # ========================================================

    valid_rows = df.loc[
        ~rejected
    ].copy()

    # ========================================================
    # STEP 3: VALIDATE OTHER FIELDS
    # ========================================================

    valid_rows, field_records = validate_fields(
        valid_rows,
        rules,
        source,
        record_column,
    )

    records.extend(
        field_records
    )

    return valid_rows, records


# ============================================================
# MAIN VALIDATION
# ============================================================

def validate_source_data(data):
    """
    Validate all source systems.

    Returns:
        Valid source DataFrames
        and invalid_records DataFrame.
    """

    logger.info(
        "Source validation started"
    )

    # ========================================================
    # CUSTOMER SYSTEM
    # ========================================================

    customers, customer_records = validate_table(
        data["customers"],
        "Customer System",
        "customer_id",
        CUSTOMER_RULES,
    )

    customer_rejected = (
        len(data["customers"]) - len(customers)
    )

    logger.info(
        "Customer System | valid=%d | rejected=%d",
        len(customers),
        customer_rejected,
    )

    # Valid customer IDs become master IDs.
    valid_customer_ids = set(
        customers["customer_id"].dropna()
    )

    # ========================================================
    # BOOKING SYSTEM
    # ========================================================

    bookings, booking_records = validate_table(
        data["bookings"],
        "Booking System",
        "booking_id",
        BOOKING_RULES,
        valid_customer_ids,
    )

    booking_rejected = (
        len(data["bookings"]) - len(bookings)
    )

    logger.info(
        "Booking System | valid=%d | rejected=%d",
        len(bookings),
        booking_rejected,
    )

    # ========================================================
    # LOYALTY SYSTEM
    # ========================================================

    loyalty, loyalty_records = validate_table(
        data["loyalty"],
        "Loyalty System",
        "customer_id",
        LOYALTY_RULES,
        valid_customer_ids,
    )

    loyalty_rejected = (
        len(data["loyalty"]) - len(loyalty)
    )

    logger.info(
        "Loyalty System | valid=%d | rejected=%d",
        len(loyalty),
        loyalty_rejected,
    )

    # ========================================================
    # SUPPORT SYSTEM
    # ========================================================

    support, support_records = validate_table(
        data["support"],
        "Support System",
        "ticket_id",
        SUPPORT_RULES,
        valid_customer_ids,
    )

    support_rejected = (
        len(data["support"]) - len(support)
    )

    logger.info(
        "Support System | valid=%d | rejected=%d",
        len(support),
        support_rejected,
    )

    # ========================================================
    # COMBINE INVALID RECORDS
    # ========================================================

    all_records = (
        customer_records
        + booking_records
        + loyalty_records
        + support_records
    )

    invalid_records = pd.DataFrame(
        all_records,
        columns=INVALID_RECORD_COLUMNS,
    )

    # ========================================================
    # FINAL VALIDATION SUMMARY
    # ========================================================

    logger.info(
        "Source validation completed | "
        "customers=%d | bookings=%d | "
        "loyalty=%d | support=%d | "
        "invalid_records=%d",
        len(customers),
        len(bookings),
        len(loyalty),
        len(support),
        len(invalid_records),
    )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "batch_folder": data["batch_folder"],
        "customers": customers,
        "bookings": bookings,
        "loyalty": loyalty,
        "support": support,
        "invalid_records": invalid_records,
    }