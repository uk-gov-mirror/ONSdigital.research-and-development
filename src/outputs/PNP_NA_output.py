"""National Accounts Output for PNP"""

import logging
import pandas as pd
from src.staging.validation import load_schema
from src.utils.helpers import filename_amender
from src.utils.breakdown_validation import get_all_wanted_columns
from src.outputs.map_output_cols import create_cora_status_col
from src.outputs.outputs_helpers import create_output_df


OutputMainLogger = logging.getLogger(__name__)


def divide_by_1000(df, config):
    """Values in columns starting 2xxx or 3xxx are divided by 1000"""
    # Get cols from config
    cols = get_all_wanted_columns(config, "imputation")

    # Ensure only columns that exist in the DataFrame are processed
    cols_to_process = [col for col in cols if col in df.columns]

    # Apply the transformation to all relevant columns
    df[cols_to_process] = df[cols_to_process].applymap(
        lambda x: round(x / 1000, 0) if x > 0 else x
    )

    return df


def create_na_output(df: pd.DataFrame, schema_dict: dict) -> pd.DataFrame:
    """Creates the dataframe for outputs with
    the required columns. The naming of the columns comes
    from the schema provided.

    Args:
        df (pd.DataFrame): Dataframe containing all columns
        schema_dict (dict): Toml schema containing the relevant
        column names for the outputs

    Returns:
        (pd.DataFrame): A dataframe consisting of only the
        required short form output data
    """
    output_df = df.copy()

    # Create a df with the original column names and the schema names
    first_row = pd.DataFrame(
        [output_df.columns],
        columns=[schema_dict[col]["name"] for col in output_df.columns],
    )

    # Ensure that the columns are the same on each dataframe
    output_df.columns = first_row.columns

    # Concatenate the first row with the output dataframe
    output_df = pd.concat([first_row, output_df], ignore_index=True)

    return output_df


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

    df = df.copy()

    # Divide by 1000
    df = divide_by_1000(df, config)

    # Map to the CORA statuses from the statusencoded column
    df = create_cora_status_col(df)

    # Add col 221 into 210 to make Total Capex Civil
    for col in ["210", "211"]:
        df[col] += df["221"]

    # Create output dataframe with required columns from schema
    schema_path = config["schema_paths"]["pnp_national_accounts_schema"]
    schema_dict = load_schema(schema_path)
    output = create_output_df(df, schema_dict)
    output = create_na_output(output, schema_dict)

    # Outputting the CSV file
    filename = filename_amender("output_PNP_national_accounts", config)
    write_csv(f"{output_path}/output_PNP_national_accounts/{filename}", output)

    # Return the processed DataFrame for QA
    return output
