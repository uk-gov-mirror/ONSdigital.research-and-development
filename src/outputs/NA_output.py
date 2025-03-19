"""National Accounts Output for PNP"""

import logging
import pandas as pd
import numpy as np
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
    # df = cols_to_add(df, config)

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
    df = empty_columns(df, config)

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
            df[col] = df[col].apply(lambda x: round(x / 1000, 0) if x > 0 else x)

    return df


def cols_to_add(df, config):
    """Adds columns for back compatibility to the orginial questions"""
    # cols_to_add = ["q0303", "q0319", "q0320", "q0323", "q0324" "q0208"]

    return df


def empty_columns(df, config):
    """Adds columns empty cols for National Accounts"""
    cols = get_all_wanted_columns(config, "estimation")
    # Get the 7XXX cols
    seven_cols = []
    for col in cols:
        if col.startswith("7"):
            seven_cols.append(col)

    # Add the 7XXX cols to the dataframe
    for col in seven_cols:
        if col not in df.columns:
            df = df.copy()
            df[col] = np.nan

    # Adding not in the config.(q0331 TO q0346)
    for i in range(331, 347):
        col = str(i)
        if col not in df.columns:
            df = df.copy()
            df[col] = np.nan
    return df


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


def remove_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Removes duplicate columns from the dataframe that are not divided
    by civil or defence.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with duplicate columns removed.
    """
    # From the df get cols that start with headcount
    cols = []
    for col in df.columns:
        if col.startswith("headcount"):
            cols.append(col)

    # Create a dictionary to map original columns to modified columns
    col_mapping = {}
    for col in cols:
        if col.endswith("_C"):
            col_mapping[col] = col[:-2]
        elif col.endswith("_D"):
            col_mapping[col] = col[:-2]
        else:
            col_mapping[col] = col

    # Apply the modified cols to the DataFrame
    df = df.rename(columns=col_mapping)

    # Aggregate the grouped columns by taking the first non-null value
    df = df.groupby(level=0, axis=1).first()

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

    # Create a list of new column names using the "name" field from the schema
    new_column_names = [
        output_schema[col]["name"] for col in colname_schema_dict.values()
    ]

    # Create a DataFrame for the first row with the original column names
    first_row_values = list(colname_schema_dict.values())
    first_row_df = pd.DataFrame([first_row_values], columns=new_column_names)

    # Rename the columns of the output DataFrame to the new column names
    output_df.columns = new_column_names

    # Concatenate the first row DataFrame with the output DataFrame
    output_df = pd.concat([first_row_df, output_df], ignore_index=True)

    return output_df
