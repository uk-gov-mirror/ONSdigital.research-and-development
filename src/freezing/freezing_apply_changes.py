import logging
from typing import Callable, Dict

import pandas as pd

from src.freezing.freezing_utils import _add_last_frozen_column
from src.utils.breakdown_validation import get_all_wanted_columns


def apply_freezing(
    main_df: pd.DataFrame,
    config: Dict,
    check_file_exists: Callable,
    read_csv: Callable,
    FreezingLogger: logging.Logger,
) -> pd.DataFrame:
    """Read user-edited freezing files and apply them to the main snapshot.
    Args:
        main_df (pd.DataFrame): The main snapshot.
        config (dict): The pipeline configuration.
        check_file_exists (callable): Function to check if file exists. This will
            be the hdfs or network version depending on settings.
        read_csv (callable): Function to read a csv file. This will be the hdfs or
            network version depending on settings.
        FreezingLogger (logging.Logger): The logger to log to.

    Returns:
        constructed_df (pd.DataFrame): As main_df but with records amended and added
            from the freezing files.
    """
    # Prepare filepaths to read from
    platform = config["global"]["platform"]
    paths = config[f"{platform}_paths"]
    amendments_filepath = paths["freezing_amendments_path"]
    additions_filepath = paths["freezing_additions_path"]

    # Check if the freezing files exist
    amendments_exist = check_file_exists(amendments_filepath)
    additions_exist = check_file_exists(additions_filepath)

    # If each file exists, read it and call the function to apply them
    if not (amendments_exist or additions_exist):
        FreezingLogger.info("No amendments or additions to apply, skipping...")
        return main_df

    # apply amendments
    if amendments_exist:
        amendments_df = read_csv(amendments_filepath)
        if amendments_df.empty:
            FreezingLogger.warning(
                f"Amendments file ({amendments_filepath}) is empty, skipping..."
            )
        else:
            main_df = apply_amendments(
                main_df,
                amendments_df,
                config,
                FreezingLogger,
            )

    # apply additions
    if additions_exist:
        additions_df = read_csv(additions_filepath)
        if additions_df.empty:
            FreezingLogger.warning(
                f"Additions file {additions_filepath} is empty, skipping..."
            )
        else:
            additions_df["instance"] = additions_df["instance"].astype("Int64")
            main_df = apply_additions(main_df, additions_df, config, FreezingLogger)

    return main_df


def validate_any_refinst_in_frozen(
    frozen_df: pd.DataFrame,
    df2: pd.DataFrame,
) -> bool:
    """Validate that any of the ref/inst combinations from df2 are in the frozen df.

    Args:
        frozen_df (pd.DataFrame): The frozen csv df
        df2 (pd.DataFrame): A second dataframe.

    Returns:
        bool: Whether any ref/inst combs from df2 are in frozen_df.
    """
    frozen_copy = frozen_df.copy()
    df2_copy = df2.copy()
    frozen_copy["refinst"] = frozen_copy["reference"].astype(str) + frozen_copy[
        "instance"
    ].astype(str)
    df2_copy["refinst"] = df2_copy["reference"].astype(str) + df2_copy[
        "instance"
    ].astype(str)
    result = any([x in list(frozen_copy["refinst"]) for x in list(df2_copy["refinst"])])
    return result


def validate_additions_df(
    frozen_df: pd.DataFrame,
    additions_df: pd.DataFrame,
    FreezingLogger: logging.Logger,
) -> None:
    """Validate the additions df.

    Args:
        frozen_df (pd.DataFrame): The frozen csv df.
        additions_df (pd.DataFrame): The additions df.
        FreezingLogger (logging.Logger): The logger to log to.

    Returns:
        bool: Whether or not the additions df is valid.
    """
    # check that the ref/inst combos are not staged frozen data
    FreezingLogger.info(
        "Checking if any ref/inst in the additions df are in the frozen data..."
    )

    any_present = validate_any_refinst_in_frozen(frozen_df, additions_df)
    if any_present:
        FreezingLogger.info(
            "Some reference/instance combinations from the additions file are "
            "present in the frozen data."
        )
        return False
    return True


def apply_amendments(
    main_df: pd.DataFrame,
    amendments_df: pd.DataFrame,
    config: Dict,
    FreezingLogger: logging.Logger,
) -> pd.DataFrame:
    """Apply amendments to the main snapshot.

    Args:
        main_df (pd.DataFrame): The main snapshot.
        amendments_df (pd.DataFrame): The amendments to apply.
        config (dict): The pipeline configuration.
        FreezingLogger (logging.Logger): The logger.

    Returns:
        amended_df (pd.DataFrame): The main snapshot with amendments applied.
    """

    # Get references where accept_changes is True
    changes_refs = amendments_df[
        amendments_df.accept_changes.isin([True])
    ].reference.unique()

    # Filter amendments to only include those marked for inclusion
    accepted_amendments_df = amendments_df[amendments_df.reference.isin(changes_refs)]

    if accepted_amendments_df.shape[0] == 0:
        FreezingLogger.info("Amendments file contained no records marked for inclusion")
        return main_df

    # Drop the diff columns and accept_changes col
    accepted_amendments_df = accepted_amendments_df.drop(
        columns=[col for col in accepted_amendments_df.columns if col.endswith("_diff")]
    )

    accepted_amendments_df = accepted_amendments_df.drop("accept_changes", axis=1)

    # rename columns
    accepted_amendments_df.columns = [
        col.replace("_updated", "") for col in accepted_amendments_df.columns
    ]

    # update last_frozen column
    accepted_amendments_df = _add_last_frozen_column(accepted_amendments_df, config)

    # List of tuples with values to filter
    values_to_filter = (
        accepted_amendments_df[["reference", "instance"]].apply(tuple, axis=1).tolist()
    )

    # drop records to be amended from main df bassed on values_to_filter
    main_df = main_df[
        ~main_df[["reference", "instance"]].apply(tuple, axis=1).isin(values_to_filter)
    ]

    # add amended records to main df
    amended_df = pd.concat([main_df, accepted_amendments_df])

    FreezingLogger.info(
        f"{accepted_amendments_df.shape[0]} record(s) amended during freezing"
    )

    # Apply deletions for 604
    main_df = apply_deletions_604(main_df, accepted_amendments_df, config)

    return amended_df


def apply_additions(
    main_df: pd.DataFrame,
    additions_df: pd.DataFrame,
    config: Dict,
    FreezingLogger: logging.Logger,
) -> pd.DataFrame:
    """Apply additions to the main snapshot.

    Args:
        main_df (pd.DataFrame): The main snapshot.
        additions_df (pd.DataFrame): The additions to apply.
        config (dict): The pipeline configuration.
        FreezingLogger (logging.Logger): The logger.

    Returns:
        added_df (pd.DataFrame): The main snapshot with additions applied.
    """
    if not validate_additions_df(main_df, additions_df, FreezingLogger):
        FreezingLogger.info("Skipping additions since the additions csv is invalid...")
        return main_df
    # Drop records where accept_changes is False and if any remain, add them to main df
    changes_refs = additions_df[
        additions_df.accept_changes.isin([True])
    ].reference.unique()

    accepted_additions_df = additions_df[additions_df.reference.isin(changes_refs)]

    # removes the old form sent out where we have a new clear response
    remove_status = [
        "Form sent out",
        "Ceased trading (NIL4)",
        "Out of scope (NIL3)",
        "Dormant (NIL5)",
    ]
    main_df = main_df[
        ~(
            (main_df.reference.isin(accepted_additions_df.reference))
            & (main_df.status.isin(remove_status))
        )
    ]

    accepted_additions_df = accepted_additions_df.drop("accept_changes", axis=1)
    if accepted_additions_df.shape[0] > 0:
        accepted_additions_df = _add_last_frozen_column(accepted_additions_df, config)
        added_df = pd.concat([main_df, accepted_additions_df], ignore_index=True)
        FreezingLogger.info(
            f"{accepted_additions_df.shape[0]} record(s) added during freezing"
        )
    else:
        FreezingLogger.info("Additions file contained no records marked for inclusion")
        return main_df
    return added_df


def apply_deletions_604(main_df, accepted_amendments_df, config):
    """Apply deletions for 604.

    Checks if accepted_amendments_df contains any rows where
    instance = 0 and 604 = No. If one or more rows meet this condition,
    accepted_amendments_df is filtered for conditions where instance = 0,
    and 604 = No creating flagged_df. The flagged references and periods
    are then used to filter main_df for rows where instance is greater than 0.

    Args:
        main_df (pd.DataFrame): The main DataFrame.
        accepted_amendments_df (pd.DataFrame): The accepted amendments DataFrame.

    Returns:
        pd.DataFrame: The main DataFrame with deletions applied
    """

    # Check if any row meets the condition of instance = 0 and 604 = No
    condition = (accepted_amendments_df["instance"] == 0) & (
        accepted_amendments_df["604"] == "No"
    )

    if condition.any():

        # Filter the accepted_amendments_df Dataframe based on for
        # instance =  0 and 604 = No
        flagged_df = accepted_amendments_df[condition]

        # Get pairs of values for columns "reference" and "period"
        # where instance = 0 and 604 = No.
        flagged_references = list(flagged_df["reference"])

        # Create a mask to identify rows where reference is in flagged_references
        # and instance is greater than 0
        reference_greater_0_mask = (main_df["reference"].isin(flagged_references)) & (
            main_df["instance"] > 0
        )

        # Filter the DataFrame using the mask
        main_df = main_df[~reference_greater_0_mask]

        # Create a mask to identify rows where reference is in flagged_references
        # and instance is  equal to 0
        reference_equal_0_mask = (main_df["reference"].isin(flagged_references)) & (
            main_df["instance"] == 0
        )

        # Replace the value in column '604' with 'No' when reference is in
        # flagged_references and instance is 0
        main_df.loc[
            reference_equal_0_mask,
            "604",
        ] = "No"

        # For rows where instance = 0 and 604 was changed from "Yes" to "No", ensure
        # columns 4xx's, 5xx's, and 7xx's are set to 0.0.

        # get columns to check
        check_list_604 = get_all_wanted_columns(config, "604_check")

        # for columns that are instance 0, and were identified as having 604 set from
        # Yes to No, set the value in columns in check_list_604 to 0.0.
        main_df.loc[reference_equal_0_mask, check_list_604] = 0.0

    return main_df
