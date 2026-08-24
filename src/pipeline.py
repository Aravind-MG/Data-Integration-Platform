"""
Customer360 - Pipeline Orchestrator

Pipeline flow:

    Read
      ↓
    Validate
      ↓
    Clean
      ↓
    Aggregate
      ↓
    Join
      ↓
    Final Validate
      ↓
    Write Output

One batch is processed from start to finish.
Detailed execution information is written to the
batch-specific pipeline log.
"""

from src.logger import (
    initialize_logger,
    get_logger,
    log_pipeline_end,
    log_pipeline_error,
)

from src.read_data import (
    get_latest_batch,
    read_source_data,
)

from src.validate_data import (
    validate_source_data,
)

from src.clean_data import (
    clean_source_data,
)

from src.aggregate_data import (
    aggregate_data,
)

from src.join_data import (
    join_customer_data,
)

from src.final_validate import (
    validate_final_data,
)

from src.write_output import (
    write_output,
)


# ============================================================
# RUN PIPELINE
# ============================================================

def run_pipeline(batch_id=None):
    """
    Run one complete Customer360 pipeline.

    Args:
        batch_id:
            Existing source batch to process.

            If None, the latest source batch is selected.

    Returns:
        dict:
            Pipeline output information including:
                - output files
                - log file
    """

    # --------------------------------------------------------
    # Select batch
    # --------------------------------------------------------

    if batch_id is None:
        batch_id = get_latest_batch()

    # --------------------------------------------------------
    # Initialize batch-specific logger
    # --------------------------------------------------------

    log_file = initialize_logger(
        batch_id
    )

    logger = get_logger()

    try:

        logger.info(
            "=" * 70
        )

        logger.info(
            "PIPELINE EXECUTION STARTED"
        )

        logger.info(
            "Batch: %s",
            batch_id,
        )

        logger.info(
            "=" * 70
        )

        # ====================================================
        # 1. READ
        # ====================================================

        logger.info(
            "STEP 1/7 | Reading source data"
        )

        source_data = read_source_data(
            batch_id
        )

        # ====================================================
        # 2. VALIDATE
        # ====================================================

        logger.info(
            "STEP 2/7 | Validating source data"
        )

        valid_data = validate_source_data(
            source_data
        )

        # ====================================================
        # 3. CLEAN
        # ====================================================

        logger.info(
            "STEP 3/7 | Cleaning source data"
        )

        cleaned_data = clean_source_data(
            valid_data
        )

        # ====================================================
        # 4. AGGREGATE
        # ====================================================

        logger.info(
            "STEP 4/7 | Aggregating customer data"
        )

        aggregated_data = aggregate_data(
            cleaned_data
        )

        # ====================================================
        # 5. JOIN
        # ====================================================

        logger.info(
            "STEP 5/7 | Joining customer data"
        )

        joined_data = join_customer_data(
            {
                **cleaned_data,
                **aggregated_data,
            }
        )

        # ====================================================
        # 6. FINAL VALIDATION
        # ====================================================

        logger.info(
            "STEP 6/7 | Final Customer360 validation"
        )

        customer360 = validate_final_data(
            joined_data["customer360"]
        )

        joined_data["customer360"] = (
            customer360
        )

        # ====================================================
        # 7. WRITE OUTPUT
        # ====================================================

        logger.info(
            "STEP 7/7 | Writing output files"
        )

        output = write_output(
            joined_data
        )

        # ====================================================
        # COMPLETION
        # ====================================================

        invalid_count = len(
            joined_data["invalid_records"]
        )

        log_pipeline_end(
            batch_id,
            len(customer360),
            invalid_count,
        )

        logger.info(
            "Pipeline completed successfully."
        )

        logger.info(
            "Log file: %s",
            log_file,
        )

        logger.info(
            "=" * 70
        )

        # ----------------------------------------------------
        # Return everything needed by main.py
        # ----------------------------------------------------

        if output is None:
            output = {}

        if not isinstance(output, dict):
            output = {
                "output": output
            }

        output["log_file"] = log_file

        return output

    except Exception as error:

        log_pipeline_error(
            error
        )

        raise


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_pipeline()