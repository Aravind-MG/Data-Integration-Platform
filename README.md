# Customer360 Data Integration Platform

## 1. Project Overview

The **Customer360 Data Integration Platform** is a Python-based data integration and data-quality pipeline developed for an airline organization.

The objective is to combine customer information from multiple independent source systems into a single, customer-level **360-degree view**.

The platform integrates:

* Customer profile information
* Flight booking information
* Spending behavior
* Loyalty information
* Customer support history

The pipeline generates source data, validates and cleans it, removes duplicates, aggregates customer-level metrics, joins the datasets, performs final validation, and generates the final Customer360 output.

---

# 2. Business Problem

The airline organization maintains customer information across multiple independent systems.

Customer, booking, loyalty, and support information are stored separately.

This creates several problems:

* Customer information is fragmented.
* Business teams cannot easily understand complete customer behavior.
* Reporting requires combining multiple datasets manually.
* Invalid and inconsistent source records can affect analysis.
* Duplicate customer records can produce incorrect metrics.
* Missing and malformed values reduce data quality.

The Customer360 platform solves this problem by integrating the information into one standardized customer-level dataset.

---

# 3. Business Objective

The objective is to provide a consolidated view that allows business users to understand:

* Who the customer is.
* How frequently the customer books flights.
* How much the customer spends.
* Their completed and cancelled bookings.
* Their loyalty information.
* Their support interaction history.

The final dataset provides one consolidated record per customer.

---

# 4. Solution Overview

The project follows an **ETL-style data integration pipeline**.

### Pipeline Flow

```text
Generate Source Data
        ↓
Read Source Data
        ↓
Validate Source Data
        ↓
Clean Source Data
        ↓
Aggregate Data
        ↓
Join Customer Data
        ↓
Final Validation
        ↓
Write Customer360 Output
```

The pipeline is designed with small, reusable modules so that each processing responsibility is separated.

---

# 5. Source Systems

The platform contains four source systems.

## 5.1 Customer System

### Purpose

Stores customer profile and contact information.

### File

```text
customers.csv
```

### Generator

```text
data/customers.py
```

### Fields

```text
customer_id
first_name
last_name
email
phone
country
```

---

## 5.2 Booking System

### Purpose

Stores flight booking and transaction information.

### File

```text
bookings.csv
```

### Generator

```text
data/bookings.py
```

### Fields

```text
booking_id
customer_id
flight
booking_date
amount
status
```

### Business information

The booking data is used to calculate:

* Total bookings
* Completed bookings
* Cancelled bookings
* Total spending
* Average booking value
* Last booking date

---

## 5.3 Loyalty System

### Purpose

Stores customer loyalty and membership information.

### File

```text
loyalty.csv
```

### Generator

```text
data/loyalty.py
```

### Fields

```text
customer_id
membership_type
loyalty_points
loyalty_tier
```

---

## 5.4 Support System

### Purpose

Stores customer support interactions and tickets.

### File

```text
support_tickets.csv
```

### Generator

```text
data/support_tickets.py
```

### Fields

```text
ticket_id
customer_id
issue_type
created_date
status
```

The support data is used to calculate:

* Total support tickets
* Open support tickets
* Closed support tickets

---

# 6. Random Source Data Generation

The project generates source data dynamically whenever the pipeline is executed.

The main controller is:

```text
data/generate_source_data.py
```

The user specifies the number of records:

```text
Enter number of records to generate: 50
```

The generator then creates:

* 80% valid records
* 20% invalid records

For example:

```text
Total Records   : 50
Valid Records   : 40
Invalid Records : 10
```

These details are written to the pipeline log rather than displayed as detailed terminal output.

## Generated Source Structure

Each execution creates a unique timestamped batch:

```text
data/
└── generated_data/
    └── batch_2026-08-24_15-49-05/
        ├── customers.csv
        ├── bookings.csv
        ├── loyalty.csv
        └── support_tickets.csv
```

This prevents source files from different executions from being mixed.

---

# 7. Batch Processing

Each pipeline execution works with a single source-data batch.

The batch naming convention is:

```text
batch_YYYY-MM-DD_HH-MM-SS
```

Example:

```text
batch_2026-08-24_15-49-05
```

The batch contains all four source CSV files.

This provides:

* Execution isolation
* Traceability
* Reproducibility
* Easier debugging
* Historical source-data retention

The latest batch can be automatically selected when a batch ID is not explicitly supplied.

---

# 8. Output and Log Batch Structure

The pipeline maintains separate batch folders for generated source data, output files, and logs.

```text
Customer360_simplified_pipeline/
│
├── data/
│   └── generated_data/
│       └── batch_2026-08-24_15-49-05/
│           ├── customers.csv
│           ├── bookings.csv
│           ├── loyalty.csv
│           └── support_tickets.csv
│
├── logs/
│   └── batch_2026-08-24_15-49-05/
│       └── pipeline_2026-08-24_15-49-05.log
│
└── output/
    └── batch_2026-08-24_15-49-05/
        ├── customer360.csv
        └── invalid_records.csv
```

The same execution timestamp is used to associate the source data, output, and log information.

---

# 9. Technologies Used

| Technology | Purpose                              |
| ---------- | ------------------------------------ |
| Python     | Application and pipeline development |
| Pandas     | Data processing and transformation   |
| Faker      | Random source-data generation        |
| CSV        | Source and output data format        |
| pathlib    | Cross-platform path handling         |
| logging    | Pipeline execution monitoring        |

---

# 10. Project Structure

```text
Customer360_simplified_pipeline/
│
├── data/
│   ├── __init__.py
│   ├── generate_source_data.py
│   ├── customers.py
│   ├── bookings.py
│   ├── loyalty.py
│   ├── support_tickets.py
│   │
│   └── generated_data/
│       └── batch_YYYY-MM-DD_HH-MM-SS/
│           ├── customers.csv
│           ├── bookings.csv
│           ├── loyalty.csv
│           └── support_tickets.csv
│
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── read_data.py
│   ├── validate_data.py
│   ├── clean_data.py
│   ├── aggregate_data.py
│   ├── join_data.py
│   ├── final_validate.py
│   ├── write_output.py
│   └── pipeline.py
│
├── output/
│   └── batch_YYYY-MM-DD_HH-MM-SS/
│       ├── customer360.csv
│       └── invalid_records.csv
│
├── logs/
│   └── batch_YYYY-MM-DD_HH-MM-SS/
│       └── pipeline_YYYY-MM-DD_HH-MM-SS.log
│
├── main.py
├── requirements.txt
└── README.md
```

---

# 11. Configuration

Central configuration is maintained in:

```text
src/config.py
```

It contains shared configuration for:

* Project directories
* Generated source-data directory
* CSV encoding
* CSV processing settings
* Source filenames
* Output filenames
* Logging format
* Customer schema
* Booking metrics
* Loyalty metrics
* Support metrics
* Final Customer360 schema
* Invalid-record schema

The generated source-data directory is:

```python
GENERATED_DATA_DIR = DATA_DIR / "generated_data"
```

This ensures source batches are stored under:

```text
data/generated_data/
```

---

# 12. Reading Source Data

Source-data reading is handled by:

```text
src/read_data.py
```

Responsibilities include:

* Finding the latest batch.
* Selecting a specified batch when provided.
* Checking that the batch exists.
* Checking that all required CSV files exist.
* Reading CSV files using Pandas.
* Logging source-file information.
* Returning the source DataFrames.

The reader does **not** perform validation or cleaning.

Those responsibilities belong to later pipeline stages.

---

# 13. Data Validation

Source validation is handled by:

```text
src/validate_data.py
```

The validation process checks source records against defined business rules.

Validation covers areas such as:

* Customer IDs
* Names
* Email addresses
* Phone numbers
* Country
* Booking IDs
* Booking customer references
* Booking status
* Booking amount
* Loyalty customer references
* Loyalty membership information
* Loyalty points
* Loyalty tier
* Support customer references
* Support ticket IDs
* Support issue types
* Support dates
* Support status

Invalid records are captured rather than allowing one invalid record to terminate the complete pipeline.

---

# 14. Data Cleaning

Data cleaning is handled by:

```text
src/clean_data.py
```

The cleaning stage prepares validated source data for downstream processing.

It handles:

* Missing values
* Standardization
* Duplicate removal
* Data-type consistency
* Invalid field replacement
* Record-level cleanup

Duplicate removal is applied across the source tables rather than only the customer table.

This is important because duplicate booking, loyalty, or support records can otherwise inflate Customer360 metrics.

---

# 15. Duplicate Handling

Duplicate records are handled during the data-cleaning process.

The goal is to prevent duplicate source records from producing incorrect customer metrics.

Examples of potential duplicate problems:

```text
Customer duplicate
        ↓
Incorrect customer count

Booking duplicate
        ↓
Incorrect booking count
        ↓
Incorrect spending

Support duplicate
        ↓
Incorrect ticket count
```

The cleaned datasets are therefore used for aggregation and joining rather than the raw source data.

---

# 16. Data Aggregation

Aggregation is handled by:

```text
src/aggregate_data.py
```

The aggregation stage converts transaction-level information into customer-level metrics.

## Booking Metrics

For each customer:

```text
total_bookings
completed_bookings
cancelled_bookings
total_spend
average_booking_value
last_booking_date
```

### Example

If a customer has:

```text
Booking 1 → Completed → ₹50,000
Booking 2 → Completed → ₹30,000
Booking 3 → Cancelled → ₹20,000
```

the Customer360 metrics can represent:

```text
total_bookings       = 3
completed_bookings   = 2
cancelled_bookings   = 1
total_spend          = 100000
average_booking_value = 33333.33
```

The final output formats count fields as whole numbers.

---

## Support Metrics

For each customer:

```text
total_support_tickets
open_support_tickets
closed_support_tickets
```

These are calculated from the support-ticket records.

---

## Loyalty Information

Customer-level loyalty information includes:

```text
loyalty_points
loyalty_tier
```

---

# 17. Customer Data Integration

Customer integration is handled by:

```text
src/join_data.py
```

The customer table acts as the primary customer dataset.

Aggregated booking, loyalty, and support information is joined using:

```text
customer_id
```

The objective is to create one customer-level record.

Foreign-key relationships are checked so that records referencing non-existing customers do not incorrectly enter the final Customer360 dataset.

---

# 18. Final Customer360 Schema

The final Customer360 dataset contains the following fields.

## Customer Information

```text
customer_id
first_name
last_name
email
phone
country
```

## Booking Metrics

```text
total_bookings
completed_bookings
cancelled_bookings
total_spend
average_booking_value
last_booking_date
```

## Loyalty Information

```text
loyalty_points
loyalty_tier
```

## Support Metrics

```text
total_support_tickets
open_support_tickets
closed_support_tickets
```

### Complete Schema

```text
customer_id
first_name
last_name
email
phone
country
total_bookings
completed_bookings
cancelled_bookings
total_spend
average_booking_value
last_booking_date
loyalty_points
loyalty_tier
total_support_tickets
open_support_tickets
closed_support_tickets
```

---

# 19. Final Output Formatting

The final Customer360 preparation ensures that output values are business-friendly.

### Count fields

Count-based fields are stored as whole numbers:

```text
total_bookings          → 3
completed_bookings      → 2
cancelled_bookings      → 1
loyalty_points          → 500
total_support_tickets   → 4
open_support_tickets    → 2
closed_support_tickets  → 2
```

They are not written as:

```text
3.0
2.0
1.0
```

### Average booking value

Average booking value retains decimal precision when required:

```text
76895.5
53003.0
71332.83
```

### Last booking date

Only the date is written.

Correct:

```text
2026-03-25
```

Not:

```text
2026-03-25 00:00:00
```

---

# 20. NULL Handling

Missing or invalid fields are represented as:

```text
NULL
```

in the generated CSV output where a value cannot be safely populated.

The pipeline does not invent values for missing customer information.

For example:

```text
customer_id,first_name,last_name,email,phone,country
C001,John,NULL,john@gmail.com,NULL,India
```

This preserves the distinction between:

* Valid available data
* Missing data
* Invalid data that was intentionally replaced

---

# 21. Invalid Records

Invalid source records are collected into:

```text
invalid_records.csv
```

The invalid-record structure is:

```text
source_system
customer_id
record_id
field
invalid_value
reason
action
```

Example:

```text
Customer System,C034,C034,first_name,NULL,
Missing or invalid name,Replaced with NULL
```

Another example:

```text
Booking System,NULL,B033,customer_id,NULL,
Missing customer_id,Record rejected
```

This provides traceability for data-quality issues.

---

# 22. Data Quality Handling

The pipeline is designed to handle invalid data without crashing the complete processing workflow.

Examples include:

* Missing mandatory fields
* Invalid customer IDs
* Duplicate records
* Missing names
* Invalid email addresses
* Invalid phone numbers
* Invalid booking status
* Missing or negative amounts
* Invalid loyalty points
* Invalid loyalty tiers
* Invalid support statuses
* Invalid dates
* Invalid customer references

Depending on the rule, the record is either:

```text
Record rejected
```

or:

```text
Replaced with NULL
```

The action is recorded in the invalid-record report.

---

# 23. Error Handling

The pipeline follows a fail-safe approach where possible.

Invalid source records do not automatically terminate the entire process.

Instead:

```text
Invalid field
      ↓
Record-quality rule
      ↓
NULL replacement / rejection
      ↓
Invalid-record report
```

Unexpected application errors are logged by the centralized logger.

This allows technical errors to be investigated without losing the execution context.

---

# 24. Logging

Logging is centralized through:

```text
src/logger.py
```

A separate log is created for each pipeline execution.

The log naming convention is:

```text
pipeline_YYYY-MM-DD_HH-MM-SS.log
```

Example:

```text
pipeline_2026-08-24_15-49-05.log
```

Logs are stored inside the corresponding batch directory:

```text
logs/
└── batch_2026-08-24_15-49-05/
    └── pipeline_2026-08-24_15-49-05.log
```

## Log Information

The pipeline log contains detailed execution information including:

* Pipeline start
* Batch identification
* Source-data generation
* Source file reading
* Record counts
* Validation results
* Cleaning results
* Duplicate handling
* Aggregation
* Joining
* Final validation
* Output generation
* Errors and exceptions
* Pipeline completion

---

# 25. Terminal Output

The terminal intentionally provides only high-level execution information.

Example:

```text
Enter number of records to generate: 40

Pipeline started...

Pipeline finished successfully.

File name: pipeline_2026-08-24_15-49-05.log
Directory name: Customer360_simplified_pipeline\logs\batch_2026-08-24_15-49-05
```

Detailed execution information is available in the log file.

This keeps the command-line interface clean while preserving complete execution traceability.

---

# 26. Pipeline Modules

## `main.py`

Application entry point.

Responsibilities:

* Start source-data generation.
* Start the pipeline.
* Display minimal terminal status.
* Display the log filename and directory.
* Handle top-level pipeline errors.

---

## `pipeline.py`

Pipeline orchestrator.

Responsibilities:

* Coordinate all pipeline stages.
* Pass the current batch through each stage.
* Initialize batch-specific logging.
* Handle pipeline-level errors.
* Return pipeline output information.

---

## `read_data.py`

Responsible for reading source CSV files.

---

## `validate_data.py`

Responsible for source-level data validation.

---

## `clean_data.py`

Responsible for:

* Cleaning
* Standardization
* Duplicate removal
* Missing-value handling

---

## `aggregate_data.py`

Responsible for customer-level metrics.

---

## `join_data.py`

Responsible for integrating customer data with aggregated information.

---

## `final_validate.py`

Responsible for checking the final Customer360 dataset before output.

---

## `write_output.py`

Responsible for:

* Preparing output datasets
* Writing `customer360.csv`
* Writing `invalid_records.csv`
* Creating output directories

---

## `logger.py`

Responsible for centralized pipeline logging.

---

## `config.py`

Responsible for centralized configuration and schema definitions.

---

# 27. Running the Project

## Step 1: Create/activate virtual environment

On Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell execution policy prevents activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.\venv\Scripts\Activate.ps1
```

---

# 28. Install Dependencies

Install the project dependencies:

```bash
pip install -r requirements.txt
```

The primary dependencies are:

```text
pandas
faker
```

---

# 29. Run the Pipeline

From the project root:

```bash
python main.py
```

The application asks:

```text
Enter number of records to generate:
```

For example:

```text
Enter number of records to generate: 100
```

The system then:

1. Generates the source datasets.
2. Creates a timestamped source batch.
3. Reads the source data.
4. Validates the source data.
5. Cleans the data.
6. Removes duplicates.
7. Aggregates customer metrics.
8. Joins customer-level data.
9. Performs final validation.
10. Writes the final output.
11. Writes the invalid-record report.
12. Saves detailed execution information to the pipeline log.

---

# 30. Example Execution

Input:

```text
Enter number of records to generate: 50
```

Terminal:

```text
Pipeline started...

Pipeline finished successfully.

File name: pipeline_2026-08-24_15-49-05.log
Directory name: Customer360_simplified_pipeline\logs\batch_2026-08-24_15-49-05
```

Generated source data:

```text
data/
└── generated_data/
    └── batch_2026-08-24_15-49-05/
        ├── customers.csv
        ├── bookings.csv
        ├── loyalty.csv
        └── support_tickets.csv
```

Generated output:

```text
output/
└── batch_2026-08-24_15-49-05/
    ├── customer360.csv
    └── invalid_records.csv
```

Generated log:

```text
logs/
└── batch_2026-08-24_15-49-05/
    └── pipeline_2026-08-24_15-49-05.log
```

---

# 31. Design Principles

The implementation follows several design principles.

## Modular Design

Each pipeline responsibility is implemented in a separate module.

```text
Read
Validate
Clean
Aggregate
Join
Final Validate
Write
```

This makes individual components easier to understand and maintain.

## Reusable Functions

Processing logic is divided into small functions rather than one large pipeline function.

## Error Isolation

Invalid records are handled without unnecessarily terminating the entire pipeline.

## Centralized Configuration

Common paths, filenames, schemas, and processing settings are maintained in:

```text
src/config.py
```

## Centralized Logging

All pipeline modules use the same logging system.

## Batch Isolation

Each execution receives its own source, output, and logging context.

---

# 32. Assumptions

The implementation follows these assumptions:

* `customer_id` is the primary customer identifier.
* Customer records without a valid `customer_id` are rejected.
* Duplicate records are removed during the cleaning stage.
* Duplicate handling is applied across source tables.
* Foreign-key references must point to an existing customer.
* Invalid customer references are rejected.
* Invalid fields that can safely be removed are replaced with `NULL`.
* Missing values are not artificially generated during cleaning.
* Count-based Customer360 metrics are represented as whole numbers.
* `average_booking_value` may contain decimal values.
* `last_booking_date` is represented as a date only.
* Source datasets are generated dynamically for each execution.
* Each execution creates a new timestamped batch.
* Detailed technical information is stored in the pipeline log.
* The terminal is intentionally kept concise.

---

# 33. Data Lineage

The major data lineage is:

```text
customers.csv
      │
      ├──────────────┐
      │              │
      ▼              ▼
Validation        Cleaning
      │              │
      └──────┬───────┘
             │
             ▼
       Customer Master
             │
             ├───────────────┐
             │               │
             ▼               ▼
      Booking Data       Loyalty Data
             │               │
             ▼               │
      Booking Metrics        │
             │               │
             └───────┬───────┘
                     │
                     ▼
              Support Metrics
                     │
                     ▼
              Customer360 Join
                     │
                     ▼
              Final Validation
                     │
                     ▼
             customer360.csv
```

---

# 34. Output Example

A Customer360 record can contain:

```text
customer_id
first_name
last_name
email
phone
country
total_bookings
completed_bookings
cancelled_bookings
total_spend
average_booking_value
last_booking_date
loyalty_points
loyalty_tier
total_support_tickets
open_support_tickets
closed_support_tickets
```

Example:

```text
C015,Patrick,Mohanty,patrick.mohanty15@gmail.com,
NULL,Paraguay,2,2,0,153791,76895.5,
2026-02-18,0,NULL,0,0,0
```

---

# 35. Invalid Record Example

The invalid-record output provides both the problematic value and the action taken.

```text
source_system
customer_id
record_id
field
invalid_value
reason
action
```

Example:

```text
Customer System
C040
C040
email
test.gmail.com
Missing or invalid email
Replaced with NULL
```

This makes the data-quality process auditable.

---

# 36. Advantages of the Implementation

The simplified architecture provides:

* Clear separation of responsibilities
* Reusable processing functions
* Centralized configuration
* Centralized logging
* Batch-level traceability
* Duplicate handling across source tables
* Invalid-record tracking
* Consistent Customer360 schema
* Controlled missing-value handling
* Customer-level aggregation
* Clean terminal output
* Easier debugging and maintenance

---

# 37. Future Enhancements

Potential future improvements include:

* Apache Spark for large-scale data processing.
* AWS S3 or Azure Blob Storage for source and output storage.
* Apache Airflow for pipeline scheduling.
* Great Expectations or similar data-quality frameworks.
* Database integration.
* Data warehouse integration.
* Automated unit and integration testing.
* CI/CD using Jenkins or GitHub Actions.
* Docker containerization.
* Cloud deployment.
* Data-quality dashboards.
* Pipeline performance monitoring.
* Incremental processing instead of full-batch processing.

---

# 38. Conclusion

The **Customer360 Data Integration Platform** provides a modular ETL-style solution for consolidating fragmented airline customer data.

The platform:

```text
Generates
    ↓
Reads
    ↓
Validates
    ↓
Cleans
    ↓
Removes Duplicates
    ↓
Aggregates
    ↓
Joins
    ↓
Final Validates
    ↓
Outputs
```

The result is a standardized customer-level dataset that combines customer profile, booking, spending, loyalty, and support information into a single Customer360 view.

The batch-based source, output, and logging architecture also provides clear execution traceability and makes the system easier to maintain, debug, and extend.

---

# 39. Author

**Customer360 Data Integration Platform**

Developed as a **Data Engineering project**.
