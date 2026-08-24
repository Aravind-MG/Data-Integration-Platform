"""
Booking data generator for Customer360 project.

Generates realistic booking records.

Features:
- Faker based flight generation
- User-defined record count
- 80% valid records
- 20% invalid records

Invalid scenarios:
- Missing values
- Invalid customer references
- Invalid status
- Invalid amount
- Invalid dates
- Duplicate IDs
"""

import random

import pandas as pd
from faker import Faker


fake = Faker()


# Valid booking statuses

STATUSES = [
    "Completed",
    "Cancelled"
]


# Invalid status values

INVALID_STATUSES = [
    "Pending",
    "Done",
    "Unknown",
    "",
    None
]


BOOKING_COLUMNS = [
    "booking_id",
    "customer_id",
    "flight",
    "booking_date",
    "amount",
    "status"
]


INVALID_BOOKING_TYPES = [
    "missing_booking_id",
    "duplicate_booking_id",
    "missing_customer_id",
    "invalid_customer_id",
    "invalid_flight",
    "missing_flight",
    "invalid_date",
    "future_date",
    "missing_amount",
    "negative_amount",
    "invalid_status",
    "missing_status"
]



def _generate_flight_code():
    """
    Generate random airline style flight code.

    Example:
    AI-452
    QZ-901
    """

    return fake.bothify(
        text="??-###",
        letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )



def _generate_booking_date():
    """
    Generate valid booking date.
    """

    month = random.randint(
        1,
        3
    )

    day = random.randint(
        1,
        28
    )

    return (
        f"2026-{month:02d}-{day:02d}"
    )



def _generate_valid_booking(
    index,
    customer_ids
):
    """
    Generate one valid booking.
    """

    booking_id = (
        f"B{index:03d}"
    )

    customer_id = random.choice(
        customer_ids
    )

    flight = _generate_flight_code()

    booking_date = _generate_booking_date()

    amount = random.randint(
        15000,
        95000
    )

    status = random.choice(
        STATUSES
    )


    return [
        booking_id,
        customer_id,
        flight,
        booking_date,
        amount,
        status
    ]

def _generate_invalid_booking(
    index,
    customer_ids
):
    """
    Generate one invalid booking record.

    Randomly applies different
    data quality issues.
    """

    booking = _generate_valid_booking(
        index,
        customer_ids
    )


    invalid_type = random.choice(
        INVALID_BOOKING_TYPES
    )


    if invalid_type == "missing_booking_id":

        booking[0] = None


    elif invalid_type == "duplicate_booking_id":

        booking[0] = "B001"


    elif invalid_type == "missing_customer_id":

        booking[1] = None


    elif invalid_type == "invalid_customer_id":

        invalid_customer_ids = [
            "C999",
            "C888",
            "ABC",
            "123",
            ""
        ]

        booking[1] = random.choice(
            invalid_customer_ids
        )


    elif invalid_type == "invalid_flight":

        booking[2] = random.choice(
            [
                "12345",
                "INVALID",
                "",
                None
            ]
        )


    elif invalid_type == "missing_flight":

        booking[2] = None


    elif invalid_type == "invalid_date":

        booking[3] = random.choice(
            [
                "2026-15-40",
                "wrong-date",
                "",
                None
            ]
        )


    elif invalid_type == "future_date":

        booking[3] = (
            "2035-12-31"
        )


    elif invalid_type == "missing_amount":

        booking[4] = None


    elif invalid_type == "negative_amount":

        booking[4] = random.randint(
            -50000,
            -1000
        )


    elif invalid_type == "invalid_status":

        booking[5] = random.choice(
            INVALID_STATUSES
        )


    elif invalid_type == "missing_status":

        booking[5] = None


    return booking



def _create_invalid_customer_reference():

    """
    Create customer_id values that
    do not exist in customer source.
    """

    return random.choice(
        [
            "C999",
            "C888",
            "C777",
            "UNKNOWN",
            "INVALID"
        ]
    )



def _add_booking_corruption(
    booking
):
    """
    Add additional random formatting issues.
    """

    corruption = random.choice(
        [
            "space",
            "uppercase",
            "none"
        ]
    )


    if corruption == "space":

        if booking[2]:

            booking[2] = (
                " "
                + str(booking[2])
                + " "
            )


    elif corruption == "uppercase":

        if booking[5]:

            booking[5] = (
                str(booking[5])
                .upper()
            )


    return booking



def _create_booking_dataframe(
    records
):
    """
    Convert booking records
    into pandas dataframe.
    """

    df = pd.DataFrame(
        records,
        columns=BOOKING_COLUMNS
    )


    return df

def generate_bookings(
    customer_ids,
    valid_count,
    invalid_count
):
    """
    Generate booking records.

    Args:
        customer_ids:
            Valid customer IDs from customers.csv.

        valid_count:
            Number of valid booking records.

        invalid_count:
            Number of invalid booking records.

    Returns:
        pandas.DataFrame
    """

    bookings = []


    # Generate valid bookings

    for i in range(
        1,
        valid_count + 1
    ):

        booking = _generate_valid_booking(
            i,
            customer_ids
        )

        bookings.append(
            booking
        )



    # Generate invalid bookings

    for i in range(
        valid_count + 1,
        valid_count + invalid_count + 1
    ):

        booking = _generate_invalid_booking(
            i,
            customer_ids
        )


        booking = _add_booking_corruption(
            booking
        )


        bookings.append(
            booking
        )



    # Mix valid and invalid records

    random.shuffle(
        bookings
    )


    df = _create_booking_dataframe(
        bookings
    )


    # Keep flexible datatypes because
    # invalid records can contain None

    df = df.astype(
        {
            "booking_id": "string",
            "customer_id": "string",
            "flight": "string",
            "booking_date": "string",
            "status": "string"
        }
    )


    return df



if __name__ == "__main__":


    total_records = int(
        input(
            "Enter number of booking records: "
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


    demo_customer_ids = [
        f"C{i:03d}"
        for i in range(1, 21)
    ]



    df = generate_bookings(
        demo_customer_ids,
        valid_count,
        invalid_count
    )


    df.to_csv(
        "bookings.csv",
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