"""
Customer data generator for Customer360 project.

Generates realistic customer records using Faker.

Features:
- User-defined record count support
- Generates valid and invalid customer records
- Invalid records simulate real data quality issues:
    - Missing values
    - Invalid email
    - Invalid phone
    - Duplicate customer IDs
    - Invalid formats
    - Blank fields

The generator creates:
80% valid records
20% invalid records

Invalid records are intentionally created for testing
the data validation pipeline.
"""

import random
import re

import pandas as pd
from faker import Faker


# Faker instances

fake_name = Faker("en_IN")
fake_global = Faker()


# Invalid data generation options

INVALID_CUSTOMER_TYPES = [
    "missing_customer_id",
    "missing_first_name",
    "missing_last_name",
    "missing_email",
    "invalid_email",
    "invalid_phone",
    "missing_phone",
    "missing_country",
    "duplicate_customer_id",
    "invalid_customer_id"
]


# Valid customer columns

CUSTOMER_COLUMNS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "phone",
    "country"
]


def _clean_name_for_email(name):
    """
    Remove special characters from names
    to create email values.
    """

    return re.sub(
        r"[^a-zA-Z]",
        "",
        str(name)
    )


def _generate_phone():
    """
    Generate valid 10 digit phone number.
    """

    return random.randint(
        6000000000,
        9999999999
    )


def _generate_valid_email(first_name, last_name, index):
    """
    Generate valid email address.
    """

    first = _clean_name_for_email(
        first_name
    ).lower()

    last = _clean_name_for_email(
        last_name
    ).lower()

    return (
        f"{first}.{last}{index}"
        "@gmail.com"
    )


def _generate_valid_customer(index):
    """
    Generate one valid customer record.
    """

    first_name = fake_name.first_name()

    last_name = fake_name.last_name()

    customer_id = (
        f"C{index:03d}"
    )

    email = _generate_valid_email(
        first_name,
        last_name,
        index
    )

    phone = _generate_phone()

    country = fake_global.country()


    return [
        customer_id,
        first_name,
        last_name,
        email,
        phone,
        country
    ]


def _generate_invalid_email():
    """
    Generate different invalid email formats.
    """

    invalid_emails = [
        "abc",
        "abc@",
        "@gmail.com",
        "test.gmail.com",
        "user@domain"
    ]

    return random.choice(
        invalid_emails
    )


def _generate_invalid_phone():
    """
    Generate invalid phone values.
    """

    invalid_phones = [
        "12345",
        "98765",
        "abcdefgh",
        "",
        "123456789012"
    ]

    return random.choice(
        invalid_phones
    )


def _generate_invalid_customer_id():
    """
    Generate invalid customer IDs.
    """

    invalid_ids = [
        "",
        None,
        "CUS001",
        "123",
        "ABC"
    ]

    return random.choice(
        invalid_ids
    )

def _generate_invalid_customer(index, existing_customers):
    """
    Generate one invalid customer record.

    Different invalid scenarios are randomly applied.
    """

    # Start with a valid customer
    customer = _generate_valid_customer(index)

    invalid_type = random.choice(
        INVALID_CUSTOMER_TYPES
    )


    if invalid_type == "missing_customer_id":

        customer[0] = None


    elif invalid_type == "missing_first_name":

        customer[1] = None


    elif invalid_type == "missing_last_name":

        customer[2] = None


    elif invalid_type == "missing_email":

        customer[3] = None


    elif invalid_type == "invalid_email":

        customer[3] = _generate_invalid_email()


    elif invalid_type == "invalid_phone":

        customer[4] = _generate_invalid_phone()


    elif invalid_type == "missing_phone":

        customer[4] = None


    elif invalid_type == "missing_country":

        customer[5] = None


    elif invalid_type == "duplicate_customer_id":

        if existing_customers:

            duplicate_customer = random.choice(
                existing_customers
            )

            customer[0] = duplicate_customer[0]


    elif invalid_type == "invalid_customer_id":

        customer[0] = _generate_invalid_customer_id()


    return customer



def _generate_duplicate_email_customer(index):
    """
    Generate customer with duplicate email.

    Duplicate emails are common real-world
    data quality issues.
    """

    customer = _generate_valid_customer(
        index
    )

    customer[3] = (
        "duplicate@gmail.com"
    )

    return customer



def _add_extra_invalid_values(customer):
    """
    Randomly introduce additional issues.

    This creates more realistic corrupted data.
    """

    corruption = random.choice(
        [
            "space",
            "uppercase",
            "special_character",
            "none"
        ]
    )


    if corruption == "space":

        if customer[1]:

            customer[1] = (
                " "
                + str(customer[1])
                + " "
            )


    elif corruption == "uppercase":

        if customer[5]:

            customer[5] = (
                str(customer[5])
                .upper()
            )


    elif corruption == "special_character":

        if customer[1]:

            customer[1] = (
                str(customer[1])
                + "@"
            )


    return customer



def _create_customer_dataframe(records):
    """
    Convert customer records into dataframe.
    """

    df = pd.DataFrame(
        records,
        columns=CUSTOMER_COLUMNS
    )


    return df

def generate_customers(valid_count, invalid_count):
    """
    Generate customer records.

    Args:
        valid_count:
            Number of valid customer records.

        invalid_count:
            Number of invalid customer records.

    Returns:
        pandas.DataFrame
    """

    customers = []

    # Track valid customers for creating duplicates
    existing_customers = []


    # Generate valid customers

    for i in range(1, valid_count + 1):

        customer = _generate_valid_customer(i)

        customers.append(customer)

        existing_customers.append(customer)



    # Generate invalid customers

    for i in range(
        valid_count + 1,
        valid_count + invalid_count + 1
    ):

        customer = _generate_invalid_customer(
            i,
            existing_customers
        )

        customer = _add_extra_invalid_values(
            customer
        )

        customers.append(customer)



    # Shuffle so invalid records
    # are not always at the bottom

    random.shuffle(
        customers
    )


    df = _create_customer_dataframe(
        customers
    )


    # Keep datatypes flexible because
    # invalid records may contain None/string values

    df = df.astype(
        {
            "customer_id": "string",
            "first_name": "string",
            "last_name": "string",
            "email": "string",
            "country": "string"
        }
    )


    return df



if __name__ == "__main__":

    total_records = int(
        input(
            "Enter number of customer records: "
        )
    )


    invalid_count = int(
        total_records * 0.20
    )


    valid_count = (
        total_records
        -
        invalid_count
    )


    df = generate_customers(
        valid_count,
        invalid_count
    )


    df.to_csv(
        "customers.csv",
        index=False
    )


    print(df)

    print("\nData Types:")
    print(df.dtypes)

    print(
        "\nTotal Records:",
        len(df)
    )

    print(
        "Valid Records:",
        valid_count
    )

    print(
        "Invalid Records:",
        invalid_count
    )