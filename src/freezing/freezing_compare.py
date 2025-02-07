import logging
import os
import pandas as pd
from typing import Callable, Tuple
from src.utils.helpers import filename_amender


def get_amendments(
    frozen_csv: pd.DataFrame,
    updated_snapshot: pd.DataFrame,
    FreezingLogger: logging.Logger,
) -> pd.DataFrame:
    """Get amended records from updated snapshot.

    Get all records that are present in both the frozen_csv and the updated
    snapshot, and have matching keys.

    Args:
        frozen_csv (pd.DataFrame): The staged and validated frozen data.
        updated_snapshot (pd.DataFrame): The staged and validated updated
            snapshot data.
        FreezingLogger (logging.Logger): The logger to log to.

    Returns:
        amendments_df (pd.DataFrame): The records that have changed.
    """
    FreezingLogger.info(
        "Looking for records that have changed in the updated snapshot."
    )
    key_cols = ["reference", "period", "instance"]
    numeric_cols = [
        "202",
        "203",
        "204",
        "205",
        "206",
        "207",
        "209",
        "210",
        "211",
        "212",
        "214",
        "216",
        "218",
        "219",
        "220",
        "221",
        "222",
        "223",
        "225",
        "226",
        "227",
        "228",
        "229",
        "237",
        "242",
        "243",
        "244",
        "245",
        "246",
        "247",
        "248",
        "249",
        "250",
        "405",
        "406",
        "407",
        "408",
        "409",
        "410",
        "411",
        "412",
        "501",
        "502",
        "503",
        "504",
        "505",
        "506",
        "507",
        "508",
        "602",
        "701",
        "702",
        "703",
        "704",
        "705",
        "706",
        "707",
        "709",
        "711",
    ]

    non_numeric_cols = ["200", "201", "601"]
    # numeric_cols_new = [f"{i}_updated" for i in numeric_cols]
    # numeric_cols_diff = [f"{i}_diff" for i in numeric_cols]
    # non_numeric_cols_new = [f"{i}_updated" for i in non_numeric_cols]
    # non_numeric_cols_diff = [f"{i}_diff" for i in non_numeric_cols]

    # Inner join on keys to select only records present in both snapshots
    amendments_df = pd.merge(
        frozen_csv,
        updated_snapshot,
        on=key_cols,
        how="inner",
        suffixes=("_original", "_updated"),
    )

    if amendments_df.shape[0] > 0:

        metadata_cols = [
            col
            for col in updated_snapshot.columns
            if col not in numeric_cols + non_numeric_cols
        ]

        def column_processing(df, type):
            """Function to split original & updated data and sort to make uniform."""
            select_cols = [
                "reference",
                "period",
                "instance",
                *[col for col in df.columns if col.endswith(type)],
            ]
            df = df[select_cols]

            df.columns = df.columns.str.replace("_original", "").str.replace(
                "_updated", ""
            )

            df = df.sort_values(by=["reference", "instance", "period"])

            return df

        frozen_df = column_processing(amendments_df, "original")
        updated_snapshot_df = column_processing(amendments_df, "updated")

        # Create a True False boolian mask for differences between frozen and SPP data.
        # Numeric differences
        numeric_differences_mask = (
            frozen_df[numeric_cols] != updated_snapshot_df[numeric_cols]
        )
        numeric_differences_df = (
            frozen_df[numeric_cols] - updated_snapshot_df[numeric_cols]
        )
        numeric_differences_masked_df = numeric_differences_df[numeric_differences_mask]

        # Non-numeric differences
        non_numeric_differences_mask = (
            frozen_df[non_numeric_cols] != updated_snapshot_df[non_numeric_cols]
        )
        non_numeric_differences_masked_df = updated_snapshot_df[non_numeric_cols][
            non_numeric_differences_mask
        ]

        # Concatenate the froxen metadata, numeric and non-numeric differences
        amendments_df = pd.concat(
            [
                updated_snapshot[metadata_cols],
                numeric_differences_masked_df,
                non_numeric_differences_masked_df,
            ],
            axis=1,
        )

        # drop rows that have no amendments performed
        def is_string_or_float(value):
            return isinstance(value, (str, float))

        # Apply the function to the specified columns and create a boolean mask
        mask = (
            amendments_df[numeric_cols + non_numeric_cols]
            .applymap(is_string_or_float)
            .all(axis=1)
        )

        # Filter the DataFrame to keep only rows where the mask is True
        amendments_df = amendments_df[mask]

        # Add markers
        amendments_df["accept_changes"] = False

        return amendments_df
    else:
        FreezingLogger.info("No amendments found.")
        return None


def get_additions(
    frozen_csv: pd.DataFrame,
    updated_snapshot: pd.DataFrame,
    FreezingLogger: logging.Logger,
) -> pd.DataFrame:
    """Get added records from the updated snapshot.

    Get all records that are present in the updated snapshot but not the main

    Args:
        frozen_csv (pd.DataFrame): The staged and validated frozen data.
        updated_snapshot (pd.DataFrame): The staged and validated updated snapshot data.
        FreezingLogger (logging.Logger): The logger to log to.

    Returns:
        additions_df (pd.DataFrame): The new records identified in
            the updated snapshot data.
    """
    FreezingLogger.info("Looking for new records in the updated snapshot.")
    key_cols = ["reference", "period", "instance"]

    # To do a right anti-join, we need to do a full outer join first, then
    # take only rows that were marked as right-only by the indicator. After
    # that, there will be copies of every column in both, but for the
    # right-only rows the columns from the left df will be null, so they're
    # all dropped afterwards.
    outer_join = pd.merge(
        frozen_csv,
        updated_snapshot,
        on=key_cols,
        how="outer",
        suffixes=("_old", ""),
        indicator=True,
    )
    additions_df = outer_join[(outer_join._merge == "right_only")].drop(
        "_merge", axis=1
    )
    additions_df = additions_df[
        additions_df.columns[~additions_df.columns.str.endswith("_old")]
    ]

    if additions_df.shape[0] > 0:
        additions_df["accept_changes"] = False
        return additions_df
    else:
        FreezingLogger.info("No additions found.")
        return None


def output_freezing_files(
    amendments_df: pd.DataFrame,
    additions_df: pd.DataFrame,
    config: dict,
    write_csv: Callable,
    FreezingLogger: logging.Logger,
) -> bool:
    """Save CSVs of amendments and additions for user approval.

    Args:
        amendments_df (pd.DataFrame): The records that have changed.
        additions_df (pd.DataFrame): The records that have been added.
        config (dict): The pipeline configuration
        write_csv (callable): Function to write to a csv file. This will be the
            hdfs or network version depending on settings.
        FreezingLogger (logging.Logger): The logger to log to.

    Returns:
        bool: True if the files were written successfully.
    """

    freezing_changes_to_review_path = config["freezing_paths"][
        "freezing_changes_to_review_path"
    ]
    FreezingLogger.info("Outputting changes to review file(s).")

    # Check if the dataframes are empty before writing
    if amendments_df is not None:
        filename = filename_amender("freezing_amendments_to_review", config)
        write_csv(
            os.path.join(freezing_changes_to_review_path, filename), amendments_df
        )

    if additions_df is not None:
        filename = filename_amender("freezing_additions_to_review", config)
        write_csv(os.path.join(freezing_changes_to_review_path, filename), additions_df)

    if amendments_df is None and additions_df is None:
        FreezingLogger.info("No changes to review found.")
        return False
    else:
        FreezingLogger.info("File(s) to review output sucessfully.")
        return True


def bring_together_split_cases(
    additions_df: pd.DataFrame,
    amendments_df: pd.DataFrame,
    FreezingLogger: logging.Logger,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Checks for references in both the additions and amendments.
    If a reference is found in both: move all the relevant rows into
    amendments and remove from additions.

    Args:
        additions_df (pd.DataFrame): The records that have been added.
        amendments_df (pd.DataFrame): The records that have changed.
        FreezingLogger (logging.Logger): The logger to log to.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: The updated additions and amendments
            dataframes.
    """
    if additions_df is not None and amendments_df is not None:
        split_cases = additions_df[
            additions_df["reference"].isin(amendments_df["reference"])
        ]
        if not split_cases.empty:
            FreezingLogger.info("Split cases found and being brought together...")
            additions_df = additions_df[
                ~additions_df.reference.isin(split_cases.reference)
            ]
            amendments_df = amendments_df.append(split_cases, ignore_index=True)
            return additions_df, amendments_df
    return additions_df, amendments_df


def run_comparison(
    frozen_data_for_comparison: pd.DataFrame,
    updated_snapshot: pd.DataFrame,
    config: dict,
    write_csv: Callable,
    FreezingLogger: logging.Logger,
) -> None:
    """Main function to run comparison of frozen data and updated snapshot.
    Function outputs two csv files, one for additions and one for amendments.

    Args:
        frozen_data_for_comparison (pd.DataFrame): The staged and validated frozen data.
        updated_snapshot (pd.DataFrame): The staged and validated updated snapshot data.
        config (dict): The pipeline configuration
        write_csv (callable): Function to write to a csv file.
        FreezingLogger (logging.Logger): The logger to log to.

    Returns:
        None
    """
    additions_df = get_additions(
        frozen_data_for_comparison, updated_snapshot, FreezingLogger
    )
    amendments_df = get_amendments(
        frozen_data_for_comparison, updated_snapshot, FreezingLogger
    )
    additions_df, amendments_df = bring_together_split_cases(
        additions_df, amendments_df, FreezingLogger
    )
    output_freezing_files(
        amendments_df, additions_df, config, write_csv, FreezingLogger
    )
