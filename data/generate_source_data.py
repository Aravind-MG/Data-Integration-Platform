"""
Customer360 - Source Data Generation

Responsibilities:
- Ask the user for the number of records.
- Generate 80% valid and 20% invalid records.
- Generate all four source datasets.
- Create one unique batch directory per execution.
- Store all source CSV files inside that batch directory.

Generated structure:

data/
└── generated_data/
    └── batch_YYYY-MM-DD_HH-MM-SS/
        ├── customers.csv
        ├── bookings.csv
        ├── loyalty.csv
        └── support_tickets.csv
"""

from datetime import datetime

from data.bookings import generate_bookings
from data.customers import generate_customers
from data.loyalty import generate_loyalty
from data.support_tickets import generate_support_tickets

from src.config import (
    GENERATED_DATA_DIR,
    SOURCE_FILES,
)

from src.logger import get_logger


logger = get_logger()


# ============================================================
# INPUT
# ============================================================

def get_record_count():
    """
    Ask the user for the number of records to generate.

    Returns:
        int: Positive number of records.
    """

    user_input = input(
        "Enter number of records to generate: "
    ).strip()

    try:
        record_count = int(user_input)

    except ValueError as error:
        raise ValueError(
            "Record count must be a valid integer."
        ) from error

    if record_count <= 0:
        raise ValueError(
            "Record count must be greater than zero."
        )

    return record_count


def calculate_record_split(total_records):
    """
    Split records into 80% valid and 20% invalid.
    """

    invalid_count = int(
        total_records * 0.20
    )

    valid_count = (
        total_records - invalid_count
    )

    return valid_count, invalid_count


# ============================================================
# BATCH
# ============================================================

def create_batch_folder():
    """
    Create a unique batch folder inside generated_data.

    Structure:

        data/
        └── generated_data/
            └── batch_TIMESTAMP/
    """

    GENERATED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    batch_folder = (
        GENERATED_DATA_DIR
        / f"batch_{timestamp}"
    )

    # Prevent accidental overwrite if two executions
    # happen within the same second.
    counter = 1
    original_folder = batch_folder

    while batch_folder.exists():

        batch_folder = (
            original_folder.parent
            / f"{original_folder.name}_{counter}"
        )

        counter += 1

    batch_folder.mkdir(
        parents=True,
        exist_ok=False,
    )

    logger.info(
        "Source batch folder created: %s",
        batch_folder,
    )

    return batch_folder


# ============================================================
# FILE WRITING
# ============================================================

def save_source_file(
    dataframe,
    batch_folder,
    file_key,
):
    """
    Save one generated DataFrame to the batch folder.

    Args:
        dataframe: Generated DataFrame.
        batch_folder: Current batch folder.
        file_key: Key from SOURCE_FILES.
    """

    file_name = SOURCE_FILES[
        file_key
    ]

    file_path = (
        batch_folder
        / file_name
    )

    dataframe.to_csv(
        file_path,
        index=False,
    )

    logger.info(
        "%s generated successfully | records=%d | file=%s",
        file_name,
        len(dataframe),
        file_path,
    )


# ============================================================
# SOURCE DATA GENERATION
# ============================================================

def generate_source_data():
    """
    Generate one complete Customer360 source batch.

    Processing order:

        1. Get record count
        2. Calculate valid/invalid split
        3. Create batch folder
        4. Generate customers
        5. Generate bookings
        6. Generate loyalty
        7. Generate support tickets
        8. Save all CSV files

    Returns:
        Path: Generated batch folder.
    """

    logger.info(
        "Source data generation started"
    )

    # --------------------------------------------------------
    # Record count
    # --------------------------------------------------------

    total_records = get_record_count()

    valid_count, invalid_count = (
        calculate_record_split(
            total_records
        )
    )

    logger.info(
        "Generation configuration | "
        "total=%d | valid=%d | invalid=%d",
        total_records,
        valid_count,
        invalid_count,
    )


    # --------------------------------------------------------
    # Create batch
    # --------------------------------------------------------

    batch_folder = (
        create_batch_folder()
    )


    # --------------------------------------------------------
    # Customers
    # --------------------------------------------------------

    logger.info(
        "Generating customer source data"
    )

    customers_df = generate_customers(
        valid_count,
        invalid_count,
    )

    save_source_file(
        customers_df,
        batch_folder,
        "customers",
    )

    # Only non-null customer IDs are passed to
    # dependent source generators.
    customer_ids = (
        customers_df["customer_id"]
        .dropna()
        .astype("string")
        .tolist()
    )

    # --------------------------------------------------------
    # Bookings
    # --------------------------------------------------------

    logger.info(
        "Generating booking source data"
    )

    bookings_df = generate_bookings(
        customer_ids,
        valid_count,
        invalid_count,
    )

    save_source_file(
        bookings_df,
        batch_folder,
        "bookings",
    )

    # --------------------------------------------------------
    # Loyalty
    # --------------------------------------------------------

    logger.info(
        "Generating loyalty source data"
    )

    loyalty_df = generate_loyalty(
        customer_ids,
        valid_count,
        invalid_count,
    )

    save_source_file(
        loyalty_df,
        batch_folder,
        "loyalty",
    )

    # --------------------------------------------------------
    # Support
    # --------------------------------------------------------

    logger.info(
        "Generating support-ticket source data"
    )

    support_df = generate_support_tickets(
        customer_ids,
        valid_count,
        invalid_count,
    )

    save_source_file(
        support_df,
        batch_folder,
        "support",
    )

    # --------------------------------------------------------
    # Completion
    # --------------------------------------------------------

    logger.info(
        "Source data generation completed | batch=%s",
        batch_folder,
    )


    return batch_folder


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":
    generate_source_data()