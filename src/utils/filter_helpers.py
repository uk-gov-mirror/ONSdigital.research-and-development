import pandas as pd
from typing import List


def create_notnull_mask(df: pd.DataFrame, col: str) -> pd.Series:
    """Return a mask for string values in column col that are not null."""
    return df[col].str.len() > 0


def check_cols_in_df(df: pd.DataFrame, cols: List[str]) -> None:
    """CHeck that a col exists in a dataframe, if not raise an error.

    Args:
        df (pd.DataFRame): The dataframe
        cols List[str]: The names of the columns to be checked

    Raises:

    """
    msg = ""
    for col in cols:
        if col not in df.columns:
            msg += f"Column {col} does not exist in this dataframe. "
    if msg != "":
        raise ValueError(msg)


def get_clear_status_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["status"])
    return df["status"].isin(["Clear", "Clear - overridden"])


def get_bad_status_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["status"])
    return df["status"].isin(["Check needed", "Form sent out"])


def get_instance_zero_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["instance"])
    return df.instance == 0


def get_instance_nonzero_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["instance"])
    return df.instance > 0


def get_no_r_and_d_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["604"])
    return df["604"] == "No"


def get_postcode_only_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["211", "601"])
    return df["211"].isnull() & df["601"].notnull()


def get_excl_postcode_only_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["211", "601"])
    return ~(df["211"].isnull() & df["601"].notnull())


def get_exclude_nan_classes_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["imp_class"])
    return ~df["imp_class"].str.contains("nan", na=False)


def get_prn_only_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["selectiontype"])
    return df["selectiontype"] == "P"


def get_census_only_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["selectiontype"])
    return df["selectiontype"] == "C"


def get_longform_only_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["formtype"])
    return df["formtype"] == "0001"


def get_shortform_only_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["formtype"])
    return df["formtype"] == "0006"


def get_mor_imputed_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["imp_marker"])
    return df["imp_marker"].isin(["MoR", "CF"])


def get_not_mor_imputed_mask(df: pd.DataFrame) -> pd.Series:
    check_cols_in_df(df, ["imp_marker"])
    return ~df["imp_marker"].isin(["MoR", "CF"])


def get_mask(df: pd.DataFrame, option: str) -> pd.Series:
    """Return a mask based on the given option."""
    mask_functions = {
        "clear_status": get_clear_status_mask,
        "bad_status": get_bad_status_mask,
        "instance_zero": get_instance_zero_mask,
        "instance_nonzero": get_instance_nonzero_mask,
        "no_r_and_d": get_no_r_and_d_mask,
        "postcode_only": get_postcode_only_mask,
        "excl_postcode_only": get_excl_postcode_only_mask,
        "exclude_nan_classes": get_exclude_nan_classes_mask,
        "prn_only": get_prn_only_mask,
        "census_only": get_census_only_mask,
        "longform_only": get_longform_only_mask,
        "shortform_only": get_shortform_only_mask,
        "mor_imputed": get_mor_imputed_mask,
        "not_mor_imputed": get_not_mor_imputed_mask,
    }

    if option in mask_functions:
        return mask_functions[option](df)
    else:
        raise ValueError(f"Invalid option for creating a mask: {option}")


def create_mask(df: pd.DataFrame, options: List[str]) -> pd.Series:
    """Create a dataframe mask based on listed options - return Bool column.

    Options include:
        - 'clear_status': rows with one of the clear statuses
        - 'instance_zero': rows with instance = 0
        - 'instance_nonzero': rows with instance != 0
        - 'no_r_and_d': rows where q604 = 'No'
        - 'postcode_only': rows in which there are no numeric values, only postcodes.
        - 'excl_postcode_only': rows excluding those with only postcodes.
        - 'exclude_nan_classes': rows excluding those with "nan" in the imp_class col.
        - 'prn_only': PRN rows, ie, rows with selectiontype = 'P'
        - 'census_only': Census rows, ie, rows with selectiontype 'C'
        - 'longform_only': Longform rows, ie, rows with formtype = '0001'
        - 'shortform_only': Shortform rows, ie, rows with formtype = '0006'
        - 'bad_status': rows with a status that is not in the clear statuses
        - 'mor_imputed': rows with an imp_marker of 'MoR' or 'CF'
        - 'not_mor_imputed': rows without an imp_marker of 'MoR' or 'CF'

    Args:
        df (pd.DataFrame): The input dataframe.
        options (List[str]): List of options to create the mask.

    Returns:
        pd.Series: Boolean mask based on the options.
    """
    df = df.copy()  # Ensure the original DataFrame is not modified

    # Initialize the mask to True
    mask = pd.Series(True, index=df.index)

    # Apply the masks based on the options
    for option in options:
        mask &= get_mask(df, option)

    return mask
