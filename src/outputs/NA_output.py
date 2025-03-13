"""National Accounts Output for PNP"""

import logging
import pandas as pd
from src.staging.validation import load_schema
from src.utils.helpers import filename_amender
from src.utils.breakdown_validation import get_all_wanted_columns
from src.outputs.outputs_helpers import create_output_df

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

    # Columns 5xxx "_C" and "D", need to be combined as one total

    # Create output dataframe with required columns from schema
    schema_path = config["schema_paths"]["nation_accounts_schema"]
    schema_dict = load_schema(schema_path)
    output = create_output_df(df, schema_dict)

    # Reorder Columns
    output = output.sort_values(by=["Column_name"], ascending=True)
    output = create_output_df(df, schema_dict)

    # Outputting the CSV file
    filename = filename_amender("output_frozen_group", config)
    write_csv(f"{output_path}/output_frozen_group/{filename}", output)


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
