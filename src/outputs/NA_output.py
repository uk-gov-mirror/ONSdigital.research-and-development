"""National Accounts Output for PNP"""

import logging
import pandas as pd
from src.staging.validation import load_schema
from src.utils.helpers import filename_amender
from src.utils.breakdown_validation import get_all_wanted_columns

OutputMainLogger = logging.getLogger(__name__)


def output_na(df: pd.DataFrame, config: dict, write_csv: callable):
    """Creates a National Accounts output for PNP only, mapping back to the original
    questions. Selects and adds columns where needed for back-compatibility, to output
    a CSV file of the appropriate format.

    Args:
        df (pd.DataFrame): The complete data.
        config (dict): The configuration settings.
        write_csv (callable): Function to write to a csv file.

    Returns:
        None

    """
    output_path = config["outputs_paths"]["outputs_master"]

    # Get columns from config
    cols = get_all_wanted_columns(config, "imputation")

    # Select only the columns we need
    div_df = df.copy()
    div_df = div_df[cols]

    # Divide by 1000
    div_df = divide_by_1000(div_df, config)

    # Replace cols in df with the new values
    df[cols] = div_df[cols]

    # Add columns for back-compatibility
    # TO DO: Check whether the cols_to_add are civil or defence q's
    df = cols_to_add(df)

    # Filter civil and defence data into seperate dataframes
    civil_df = df[df["200"] == "C"]
    defence_df = df[df["200"] == "D"]

    # Add "C" or "D" to the columns of the corresponding dataframes
    civil_df.columns = civil_df.columns + "_C"
    defence_df.columns = defence_df.columns + "_D"

    # Concatenate the dataframes
    df = concat_df(civil_df, defence_df)

    # Remove duplicate columns
    df = remove_duplicate_columns(df)

    # Add empty columns
    # df = empty_columns(df)

    # Create output dataframe with required columns from schema
    schema_path = config["schema_paths"]["national_accounts_schema"]
    schema_dict = load_schema(schema_path)
    output = create_na_output(df, schema_dict)

    # Outputting the CSV file
    filename = filename_amender("output_national_accounts", config)
    write_csv(f"{output_path}/output_national_accounts/{filename}", output)


def divide_by_1000(df, config):
    """Values in columns starting 2xxx or 3xxx are divided by 1000"""
    # Get cols from config
    cols = get_all_wanted_columns(config, "imputation")

    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x / 1000 if x > 0 else x)

    return df


def cols_to_add(df: pd.DataFrame):
    """Adds columns for back-compatibility."""
    cols_to_add = ["q0303", "q0319", "q0320", "q0323", "q0324" "q0208"]

    for col in cols_to_add:
        if col not in df.columns:
            df[col] = 0

    return df


def empty_columns(df: pd.DataFrame):
    """Adds empty columns to the dataframe for NA purposes."""
    empty_cols = ["q0701", "q0702", "q0703", "q0704", "q0705", "q0706"]

    for col in empty_cols:
        if col not in df.columns:
            df[col] = 0


def concat_df(civil_df: pd.DataFrame, defence_df: pd.DataFrame):
    """Concatenates the civil and defence dataframes to one datdframe.

    Args:
        df(pd.DataFrame): The filtered and reformatted civil dataframe.
        df(pd.DataFrame): The filtered and reformatted defence dataframe.
    Return:
        df(pd.DataFrame): The joined dataframe, ready for output.

    """
    df = pd.concat([civil_df, defence_df], ignore_index=True, axis=0)

    return df


def remove_duplicate_columns(df: pd.DataFrame):
    """Removes duplicate columns that are from the dataframe who are not divided
    by civil or defence."""

    # From the df get cols that start with headcount
    cols = []
    for col in df.columns:
        if col.startswith("headcount"):
            cols.append(col)

    # Drop all columns that have come from the defence_df "_D"
    cols_to_drop = []
    for col in cols:
        if col.endswith("_D"):
            cols_to_drop.append(col)

    df = df.drop(cols_to_drop, axis=1)

    # Remove the "_C" from cols
    col_c = []
    for col in cols:
        if col.endswith("_C"):
            col_c.append(col)
            for col in col_c:
                df = df.rename(columns={col: col[:-2]})

    return df


def create_na_output(df: pd.DataFrame, output_schema: dict) -> pd.DataFrame:
    """Creates the dataframe for outputs with
    the required columns. The naming of the columns comes
    from the schema provided.

    Args:
        df (pd.DataFrame): Dataframe containing all columns
        output_schema (str): Toml schema containing the old and new
        column names for the outputs

    Returns:
        (pd.DataFrame): A dataframe consisting of only the
        required short form output data
    """

    # Create dict of current and required column names
    colname_schema_dict = {
        output_schema[column_nm]["R_and_D_Type"]: column_nm
        for column_nm in output_schema.keys()
    }

    # Check if colname_schema_dict is empty
    if not colname_schema_dict:
        raise ValueError("colname_schema_dict is empty. Please check the schema.")

    # Check if all keys in colname_schema_dict are in df.columns
    missing_cols = [col for col in colname_schema_dict.keys() if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Create subset dataframe with only the required outputs
    output_df = df[colname_schema_dict.keys()].copy()

    # Rename columns to match the output specification
    output_df.rename(columns=colname_schema_dict, inplace=True)

    # Rearrange to match user defined output order
    output_df = output_df[colname_schema_dict.values()]

    headers = [output_schema[col]["name"] for col in colname_schema_dict.values()]

    # Create a DataFrame for headers and subheaders
    header_df = pd.DataFrame([headers], columns=output_df.columns)

    # Concatenate the header DataFrame with the output DataFrame
    output_df = pd.concat([header_df, output_df], ignore_index=True)

    # Reset the index
    output_df = output_df.reset_index(drop=True)

    return output_df
