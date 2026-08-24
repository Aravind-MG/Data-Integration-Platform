"""
Support ticket data generator for Customer360 project.

Generates realistic support ticket records.

Features:
- Random issue generation
- User-defined record count
- 80% valid records
- 20% invalid records

Invalid scenarios:
- Missing values
- Invalid customer references
- Invalid dates
- Invalid statuses
- Duplicate IDs
"""

import random

import pandas as pd
from faker import Faker


fake = Faker()



# Valid ticket statuses

STATUSES = [
    "Open",
    "Closed"
]



# Valid issue categories

ISSUE_TYPES = [
    "Refund Request",
    "Booking Modification",
    "Cancellation",
    "Baggage Issue",
    "Flight Delay",
    "Payment Issue",
    "Flight Cancellation",
    "Food Complaint",
    "Seat Selection",
    "Crew Behavior",
    "Loyalty Points",
    "Check-in Issue",
    "Lost Item",
    "Overbooking Complaint"
]



# Invalid values

INVALID_STATUSES = [
    "Pending",
    "Resolved",
    "Unknown",
    "",
    None
]


INVALID_ISSUES = [
    "Random Issue",
    "ABC",
    "",
    None
]



SUPPORT_COLUMNS = [
    "ticket_id",
    "customer_id",
    "issue_type",
    "created_date",
    "status"
]



INVALID_SUPPORT_TYPES = [
    "missing_ticket_id",
    "duplicate_ticket_id",
    "missing_customer_id",
    "invalid_customer_id",
    "missing_issue_type",
    "invalid_issue_type",
    "invalid_date",
    "future_date",
    "missing_status",
    "invalid_status"
]



def _generate_created_date():
    """
    Generate valid ticket creation date.
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



def _generate_valid_ticket(
    index,
    customer_ids
):
    """
    Generate one valid support ticket.
    """


    ticket_id = (
        f"T{index:03d}"
    )


    customer_id = random.choice(
        customer_ids
    )


    issue_type = random.choice(
        ISSUE_TYPES
    )


    created_date = _generate_created_date()



    status = random.choice(
        STATUSES
    )


    return [
        ticket_id,
        customer_id,
        issue_type,
        created_date,
        status
    ]



def _generate_invalid_customer_id():
    """
    Generate invalid customer references.
    """

    return random.choice(
        [
            "C999",
            "C888",
            "UNKNOWN",
            "INVALID",
            None
        ]
    )

def _generate_invalid_ticket(
    index,
    customer_ids,
    existing_records
):
    """
    Generate one invalid support ticket.

    Randomly introduces different
    data quality problems.
    """


    ticket = _generate_valid_ticket(
        index,
        customer_ids
    )


    invalid_type = random.choice(
        INVALID_SUPPORT_TYPES
    )



    if invalid_type == "missing_ticket_id":

        ticket[0] = None



    elif invalid_type == "duplicate_ticket_id":

        ticket[0] = "T001"



    elif invalid_type == "missing_customer_id":

        ticket[1] = None



    elif invalid_type == "invalid_customer_id":

        ticket[1] = (
            _generate_invalid_customer_id()
        )



    elif invalid_type == "missing_issue_type":

        ticket[2] = None



    elif invalid_type == "invalid_issue_type":

        ticket[2] = random.choice(
            INVALID_ISSUES
        )



    elif invalid_type == "invalid_date":

        ticket[3] = random.choice(
            [
                "wrong-date",
                "2026-15-50",
                "",
                None
            ]
        )



    elif invalid_type == "future_date":

        ticket[3] = (
            "2035-12-31"
        )



    elif invalid_type == "missing_status":

        ticket[4] = None



    elif invalid_type == "invalid_status":

        ticket[4] = random.choice(
            INVALID_STATUSES
        )


    return ticket




def _add_ticket_corruption(
    ticket
):
    """
    Add formatting issues to
    simulate real source data.
    """


    corruption = random.choice(
        [
            "space",
            "uppercase",
            "none"
        ]
    )



    if corruption == "space":

        if ticket[2]:

            ticket[2] = (
                " "
                + str(ticket[2])
                + " "
            )



    elif corruption == "uppercase":

        if ticket[4]:

            ticket[4] = (
                str(ticket[4])
                .upper()
            )


    return ticket




def _create_support_dataframe(
    records
):
    """
    Convert support records
    into pandas dataframe.
    """


    df = pd.DataFrame(
        records,
        columns=SUPPORT_COLUMNS
    )


    return df

def generate_support_tickets(
    customer_ids,
    valid_count,
    invalid_count
):
    """
    Generate support ticket records.

    Args:
        customer_ids:
            Customer IDs from customers.csv.

        valid_count:
            Number of valid ticket records.

        invalid_count:
            Number of invalid ticket records.

    Returns:
        pandas.DataFrame
    """


    tickets = []


    existing_records = []



    # Generate valid tickets

    for i in range(
        1,
        valid_count + 1
    ):

        ticket = _generate_valid_ticket(
            i,
            customer_ids
        )


        tickets.append(
            ticket
        )


        existing_records.append(
            ticket
        )



    # Generate invalid tickets

    for i in range(
        valid_count + 1,
        valid_count + invalid_count + 1
    ):

        ticket = _generate_invalid_ticket(
            i,
            customer_ids,
            existing_records
        )


        ticket = _add_ticket_corruption(
            ticket
        )


        tickets.append(
            ticket
        )



    # Mix valid and invalid records

    random.shuffle(
        tickets
    )



    df = _create_support_dataframe(
        tickets
    )



    # Keep flexible datatypes because
    # invalid records may contain None

    df = df.astype(
        {
            "ticket_id": "string",
            "customer_id": "string",
            "issue_type": "string",
            "created_date": "string",
            "status": "string"
        }
    )


    return df




if __name__ == "__main__":


    total_records = int(
        input(
            "Enter number of support ticket records: "
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



    df = generate_support_tickets(
        demo_customer_ids,
        valid_count,
        invalid_count
    )



    df.to_csv(
        "support_tickets.csv",
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