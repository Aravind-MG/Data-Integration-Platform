"""
Customer360 - Application Entry Point

The main module provides a minimal terminal interface.

Detailed pipeline execution information is written
to the batch-specific pipeline log file.
"""

from data.generate_source_data import generate_source_data

from src.pipeline import run_pipeline

from src.config import BASE_DIR


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Generate one source-data batch and run the pipeline.

    Terminal output is intentionally kept minimal.
    Detailed execution information is available in the log.
    """

    try:
        # ----------------------------------------------------
        # Generate source data
        # ----------------------------------------------------

        batch_id = generate_source_data()

        # ----------------------------------------------------
        # Start pipeline
        # ----------------------------------------------------

        print("\nPipeline started...")

        result = run_pipeline(
            batch_id
        )

        # ----------------------------------------------------
        # Pipeline completed
        # ----------------------------------------------------

        print(
            "\nPipeline finished successfully."
        )

        # ----------------------------------------------------
        # Log information
        # ----------------------------------------------------

        if result and result.get("log_file"):

            log_file = result["log_file"]

            # Convert absolute path into a path that
            # includes the project folder name.
            #
            # Example:
            # Customer360_simplified_pipeline/
            #     logs/
            #         batch_2026-08-24_15-49-05/

            relative_log_directory = (
                log_file.parent.relative_to(
                    BASE_DIR.parent
                )
            )

            print(f"\nFor any information, contact the below given file and its directory")

            print(
                f"\nFile name: {log_file.name}"
            )

            print(
                f"File Directory name: "
                f"{relative_log_directory}\n"
            )

    except Exception as error:

        print("\nPipeline failed.")
        print(f"Error: {error}")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()