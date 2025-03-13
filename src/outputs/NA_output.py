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
    df = cols_to_add(df)

    # Filter civil and defence data into seperate dataframes
    civil_df = df[df["200"] == "C"]
    defence_df = df[df["200"] == "D"]

    # Add "C" or "D" to the columns of the corresponding dataframes
    civil_df.columns = civil_df.columns + "_C"
    defence_df.columns = defence_df.columns + "_D"

    # Concatenate the dataframes
    df = concat_df(civil_df, defence_df)

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
    cols_to_add = ["q0303", "q0327", "q0319", "q0323", "q0208"]

    for col in cols_to_add:
        if col not in df.columns:
            df[col] = 0

    return df


def map_to_prev_civil(df: pd.DataFrame):
    """Maps the columns to the orginal questions for civil data."""
    columns_to_revert = {
        "210": "q0202",
        "219": "q0204",
        "220": "q0206",
        "221": "q0210",
        "204": "q0212",
        "202": "q0214",
        "222": "q0216",
        "223": "q0218",
        "211": "q0222",
        "205": "q0224",
        "206": "q0226",
        "208": "q0228",
        "212": "q0301",
        "216": "q0305",
        "242": "q0307",
        "243": "q0309",
        "244": "q0311",
        "245": "q0313",
        "246": "q0315",
        "247": "q0317",
        "248": "q0321",
        "218": "q0325",
        "214": "q0327",
        "250": "q0329",
        "405": "q0509",  # FTE Researchers - civil
        "407": "q0511",  # FTE Technicians - civil
        "409": "q0513",  # FTE Other - civil
        "411": "q0515",  # FTE Total - civil
    }

    for col in columns_to_revert:
        if col in df.columns:
            df[columns_to_revert[col]] = df[col]
            df.drop(columns=col, inplace=True)

    return df


def map_to_prev_defence(df: pd.DataFrame):
    """Maps columns to orginal questions for defence data."""
    columns_to_revert = {
        "210": "q0203",
        "219": "q0205",
        "220": "q0207",
        "221": "q0211",
        "204": "q0213",
        "202": "q0215",
        "222": "q0217",
        "223": "q0219",
        "211": "q0223",
        "205": "q0225",
        "206": "q0227",
        "207": "q0229",
        "212": "q0302",
        "216": "q0306",
        "242": "q0308",
        "243": "q0310",
        "244": "q0312",
        "245": "q0314",
        "246": "q0316",
        "247": "q0318",
        "248": "q0322",
        "218": "q0326",
        "214": "q0328",
        "250": "q0330",
        "405": "q0510",  # FTE Researchers- defence
        "407": "q0512",  # FTE Technicians- defence
        "409": "q0514",  # FTE Other - defence
        "411": "q0516",  # FTE Total - defence
    }

    for col in columns_to_revert:
        if col in df.columns:
            df[columns_to_revert[col]] = df[col]
            df.drop(columns=col, inplace=True)

    return df


def reformat_questions(df: pd.DataFrame):
    """Columns common to both civil and defence that names need to be reverted"""
    columns_to_revert = {
        "headcount_res_m": "q0501",
        "headcount_res_f": "q0502",
        "headcount_tec_m": "q0503",
        "headcount_tec_f": "q0504",
        "headcount_oth_m": "q0505",
        "headcount_oth_f": "q0506",
        "headcount_tot_m": "q0507",
        "headcount_tot_f": "q0508",
        "601": "q0601",
        "602": "q0602",
    }

    for col in columns_to_revert:
        if col in df.columns:
            df[columns_to_revert[col]] = df[col]
            df.drop(columns=col, inplace=True)

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
