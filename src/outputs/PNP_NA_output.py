"""National Accounts Output for PNP"""

import logging
import pandas as pd
import numpy as np
from src.staging.validation import load_schema
from src.utils.helpers import filename_amender
from src.utils.breakdown_validation import get_all_wanted_columns
from src.outputs.map_output_cols import create_cora_status_col

OutputMainLogger = logging.getLogger(__name__)


def divide_by_1000(df, config):
    """Values in columns starting 2xxx or 3xxx are divided by 1000"""
    # Get cols from config
    cols = get_all_wanted_columns(config, "imputation")

    for col in cols:
        df = df.copy()
        if col in df.columns:
            df[col] = df[col].apply(lambda x: round(x / 1000, 0) if x > 0 else x)

    return df


def add_headcount(df, config):
    """Add headcount columns for civil and defence together to get the 5XXX columns"""
    # Get cols from config
    cols = config["breakdowns"]["headcount_total"]

    # Add together the columns that are the same in both dataframes for headcount
    for col in cols:
        if f"{col}_C" in df.columns and f"{col}_D" in df.columns:
            df[col] = df[f"{col}_C"].fillna(0) + df[f"{col}_D"].fillna(0)

    return df


def output_pnp_na(df: pd.DataFrame, config: dict, write_csv: callable):
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

    # Divide by 1000
    df = divide_by_1000(df, config)

    # Get the columns that are required for the output
    wanted_cols = get_all_wanted_columns(config, "longform")

    #  Add "C" or "D" to the columns of the corresponding dataframes
    civil_df = df.rename(columns={col: col + "_C" for col in wanted_cols})
    defence_df = df.rename(columns={col: col + "_D" for col in wanted_cols})

    # Get columns consistent in both dataframes
    join_cols = ["reference", "201", "601"]

    # Merge the dataframes
    join_df = pd.merge(
        civil_df, defence_df, on=join_cols, how="outer", suffixes=("", "_drop")
    )

    # Drop the columns that are not needed
    join_df = join_df.loc[:, ~join_df.columns.str.endswith("_drop")]

    # Add together the columns that are the same in both dataframes for headcount
    df = add_headcount(join_df, config)

    # Map to the CORA statuses from the statusencoded column
    df = create_cora_status_col(df)

    # Create output dataframe with required columns from schema
    schema_path = config["schema_paths"]["pnp_national_accounts_schema"]
    schema_dict = load_schema(schema_path)
    output = create_na_output(df, schema_dict)

    # Outputting the CSV file
    filename = filename_amender("output_PNP_national_accounts", config)
    write_csv(f"{output_path}/output_PNP_national_accounts/{filename}", output)

    # Return the processed DataFrame for QA
    return output


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

    # If col is in schema but not in df, add it to the df
    for col in colname_schema_dict.keys():
        if col not in df.columns:
            df[col] = np.nan

    # Create subset dataframe with only the required outputs
    output_df = df[colname_schema_dict.keys()].copy()

    # Rename columns to match the output specification
    output_df.rename(columns=colname_schema_dict, inplace=True)

    # Rearrange to match user defined output order
    output_df = output_df[colname_schema_dict.values()]

    # Create a list of new column names using the "name" field from the schema
    new_column_names = []
    for col in colname_schema_dict.values():
        new_column_names.append(output_schema[col]["name"])

    # Create a DataFrame for the first row with the original column names
    first_row_values = list(colname_schema_dict.values())
    first_row_df = pd.DataFrame([first_row_values], columns=new_column_names)

    # Rename the columns of the output DataFrame to the new column names
    output_df.columns = new_column_names

    # Concatenate the first row DataFrame with the output DataFrame
    output_df = pd.concat([first_row_df, output_df], ignore_index=True)

    return output_df
