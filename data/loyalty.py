"""
Loyalty data generator for Customer360 project.

Generates realistic loyalty records.

Features:
- Faker/random based data generation
- User-defined record count
- 80% valid records
- 20% invalid records

Invalid scenarios:
- Missing values
- Invalid customer references
- Invalid membership types
- Invalid loyalty tiers
- Invalid points
"""

import random

import pandas as pd



# Valid dropdown values

MEMBERSHIP_TYPES = [
    "Corporate",
    "Personal"
]


LOYALTY_TIERS = [
    "Bronze",
    "Silver",
    "Gold",
    "Platinum"
]


# Invalid dropdown values

INVALID_MEMBERSHIP_TYPES = [
    "Premium",
    "Unknown",
    "",
    None
]


INVALID_LOYALTY_TIERS = [
    "Diamond",
    "Basic",
    "Unknown",
    "",
    None
]


LOYALTY_COLUMNS = [
    "customer_id",
    "membership_type",
    "loyalty_points",
    "loyalty_tier"
]



INVALID_LOYALTY_TYPES = [
    "missing_customer_id",
    "invalid_customer_id",
    "duplicate_customer_id",
    "missing_membership",
    "invalid_membership",
    "missing_points",
    "negative_points",
    "invalid_points",
    "missing_tier",
    "invalid_tier"
]



def _generate_valid_loyalty(customer_id):
    """
    Generate one valid loyalty record.
    """


    membership_type = random.choice(
        MEMBERSHIP_TYPES
    )


    loyalty_points = random.randint(
        0,
        80000
    )


    loyalty_tier = random.choice(
        LOYALTY_TIERS
    )


    return [
        customer_id,
        membership_type,
        loyalty_points,
        loyalty_tier
    ]



def _generate_invalid_customer_id():

    """
    Generate customer IDs that
    do not exist.
    """

    return random.choice(
        [
            "C999",
            "C888",
            "INVALID",
            "",
            None
        ]
    )

def _generate_invalid_loyalty(
    customer_id,
    existing_records
):
    """
    Generate one invalid loyalty record.

    Randomly applies different
    data quality problems.
    """


    loyalty = _generate_valid_loyalty(
        customer_id
    )


    invalid_type = random.choice(
        INVALID_LOYALTY_TYPES
    )



    if invalid_type == "missing_customer_id":

        loyalty[0] = None



    elif invalid_type == "invalid_customer_id":

        loyalty[0] = (
            _generate_invalid_customer_id()
        )



    elif invalid_type == "duplicate_customer_id":

        if existing_records:

            duplicate_record = random.choice(
                existing_records
            )

            loyalty[0] = (
                duplicate_record[0]
            )



    elif invalid_type == "missing_membership":

        loyalty[1] = None



    elif invalid_type == "invalid_membership":

        loyalty[1] = random.choice(
            INVALID_MEMBERSHIP_TYPES
        )



    elif invalid_type == "missing_points":

        loyalty[2] = None



    elif invalid_type == "negative_points":

        loyalty[2] = random.randint(
            -50000,
            -1
        )



    elif invalid_type == "invalid_points":

        loyalty[2] = random.choice(
            [
                "ABC",
                "",
                "invalid",
                None
            ]
        )



    elif invalid_type == "missing_tier":

        loyalty[3] = None



    elif invalid_type == "invalid_tier":

        loyalty[3] = random.choice(
            INVALID_LOYALTY_TIERS
        )



    return loyalty




def _add_loyalty_corruption(
    loyalty
):
    """
    Add small formatting issues
    to simulate real source data.
    """

    corruption = random.choice(
        [
            "space",
            "uppercase",
            "none"
        ]
    )


    if corruption == "space":

        if loyalty[1]:

            loyalty[1] = (
                " "
                + str(loyalty[1])
                + " "
            )



    elif corruption == "uppercase":

        if loyalty[3]:

            loyalty[3] = (
                str(loyalty[3])
                .upper()
            )


    return loyalty




def _create_loyalty_dataframe(
    records
):
    """
    Convert loyalty records
    into pandas dataframe.
    """

    df = pd.DataFrame(
        records,
        columns=LOYALTY_COLUMNS
    )


    return df

def generate_loyalty(
    customer_ids,
    valid_count,
    invalid_count
):
    """
    Generate loyalty records.

    Args:
        customer_ids:
            Customer IDs generated from customers.csv.

        valid_count:
            Number of valid loyalty records.

        invalid_count:
            Number of invalid loyalty records.

    Returns:
        pandas.DataFrame
    """

    loyalty_records = []


    # Store generated records
    # for duplicate testing

    existing_records = []



    # Generate valid loyalty records

    for customer_id in customer_ids[:valid_count]:

        loyalty = _generate_valid_loyalty(
            customer_id
        )

        loyalty_records.append(
            loyalty
        )

        existing_records.append(
            loyalty
        )



    # Generate invalid loyalty records

    for i in range(
        invalid_count
    ):


        # Pick a valid customer sometimes
        # and sometimes generate invalid reference

        customer_id = random.choice(
            customer_ids
        )


        loyalty = _generate_invalid_loyalty(
            customer_id,
            existing_records
        )


        loyalty = _add_loyalty_corruption(
            loyalty
        )


        loyalty_records.append(
            loyalty
        )



    # Mix records

    random.shuffle(
        loyalty_records
    )



    df = _create_loyalty_dataframe(
        loyalty_records
    )


    # Keep flexible types because
    # invalid records may contain None/string values

    df = df.astype(
        {
            "customer_id": "string",
            "membership_type": "string",
            "loyalty_tier": "string"
        }
    )


    return df




if __name__ == "__main__":


    total_records = int(
        input(
            "Enter number of loyalty records: "
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



    df = generate_loyalty(
        demo_customer_ids,
        valid_count,
        invalid_count
    )


    df.to_csv(
        "loyalty.csv",
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