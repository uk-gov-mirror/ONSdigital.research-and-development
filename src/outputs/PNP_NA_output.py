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

    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: round(x / 1000, 0) if x > 0 else x)

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

    df = df.copy()

    # Divide by 1000
    df = divide_by_1000(df, config)

    # Map to the CORA statuses from the statusencoded column
    df = create_cora_status_col(df)

    # Create output dataframe with required columns from schema
    schema_path = config["schema_paths"]["pnp_national_accounts_schema"]
    schema_dict = load_schema(schema_path)
    output = create_output_df(df, schema_dict)
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
    output_df = df.copy()

    # Create dict of current and required column names
    description_schema_dict = {
        output_schema[column_nm]["name"]: column_nm
        for column_nm in output_schema.keys()
    }

    # Create a list of descriptions for column headers
    description_row = list(description_schema_dict.keys())

    # Create a DataFrame for the first row with the original column names
    first_row_values = list(description_schema_dict.values())
    first_row_df = pd.DataFrame([first_row_values], columns=description_row)

    # Rename the columns of the output DataFrame to the new column names
    output_df.columns = description_row

    # Concatenate the first row DataFrame with the output DataFrame
    output_df = pd.concat([first_row_df, output_df], ignore_index=True)

    return output_df
