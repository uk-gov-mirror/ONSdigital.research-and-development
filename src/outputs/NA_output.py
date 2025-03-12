"""National Accounts Output for PNP"""

import logging
import pandas as pd

OutputMainLogger = logging.getLogger(__name__)


def divide_by_1000(df, config):
    """Values in columns starting 2xxx or 3xxx are divided by 1000"""
    # Get cols from config
    cols = (
        config["consistency_checks"]["2xx_totals"]["purchases_split"]
        + config["consistency_checks"]["2xx_totals"]["sal_oth_expend"]
        + config["consistency_checks"]["2xx_totals"]["research_expend"]
        + config["consistency_checks"]["2xx_totals"]["capex"]
        + config["consistency_checks"]["2xx_totals"]["intram"]
        + config["consistency_checks"]["2xx_totals"]["funding"]
        + config["consistency_checks"]["2xx_totals"]["ownership"]
        + config["consistency_checks"]["2xx_totals"]["equality"]
        + config["consistency_checks"]["2xx_totals"]["inequality"]
        + config["consistency_checks"]["3xx_totals"]["purchases"]
    )

    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x / 1000 if x > 0 else x)

            return df


def cols_to_add(df: pd.DataFrame):
    """Adds columns for back-compatibility."""
    cols_to_add = ["q303", "q327", "q319", "q323", "q208"]

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
        "405": "q0509",
        "407": "q0511",
        "409": "q0513",
        "411": "q0515",
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
        "405": "q0510",
        "407": "q0512",
        "409": "q0514",
        "411": "q0516",
    }

    for col in columns_to_revert:
        if col in df.columns:
            df[columns_to_revert[col]] = df[col]
            df.drop(columns=col, inplace=True)

    return df


def reformat_questions(df: pd.DataFrame):
    """Columns common to both civil and defence that names need to be reverted"""
    columns_to_revert = {
        "501": "q0501",
        "502": "q0502",
        "503": "q0503",
        "504": "q0504",
        "505": "q0505",
        "506": "q0506",
        "507": "q0507",
        "508": "q0508",
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
