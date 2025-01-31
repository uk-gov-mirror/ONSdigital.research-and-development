import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict


CalcWeights_Logger = logging.getLogger(__name__)


def create_estimation_filter(df: pd.DataFrame) -> pd.Series:
    """Return a boolean mask for the conditions needed to apply estimation."""
    sample_cond = df["selectiontype"] == "P"
    status_cond = df.status.isin(["Clear", "Clear - overridden"])
    formtype_cond = df["formtype"] == "0006"

    estimation_filter = formtype_cond & sample_cond & status_cond
    return estimation_filter


def calc_lower_n(df: pd.DataFrame, exp_col: str = "709") -> dict:
    """Calculates 'n' which is a number of
    unique RU references in the filtered dataset.

    Args:
        df (pd.DatatFrame): The input dataframe which contains survey data,
            including expenditure data
        exp_col (str): An appropriate column to count n

    Returns:
        int: The number of unique references.
    """

    # Check if any of the key cols are missing
    cols = set(df.columns)
    if not ("reference" in cols) & (exp_col in cols):
        raise ValueError(f"'reference' or {exp_col} missing.")

    # Count the records
    n = df["reference"].nunique()

    return n


def outlier_round(x):
    """Calculates the rounding threshold for outliers.
    Outliers are rounded up if the decimal is 0.5 or greater.

    The use of 'x % 1' is to get the decimal part of the number.
    Therefore anywhere the value has a decimal of 0.5 or greater the function
    will round up and anything else it will round down.
    """
    if x % 1 == 0.5:
        return np.ceil(x)
    elif x % 1 < 0.5:
        return np.floor(x)
    else:
        return np.ceil(x)


def calc_lower_s(df: pd.DataFrame, config: Dict[str, float]) -> dict:
    """Calculates 's' which identifies the number of outliers for a cell group

    Args:
        df (pd.DataFrame): The input dataframe which contains survey data.
        config (Dict[str, float]): The configuration settings.
    Returns:
        int: Calculated value of s.
    """

    # Retrieve percent from config upper_clip outlier threshold.
    outlier_thresh = config.get("global", {}).get("upper_clip")

    # Check if there is a value in the config.
    if outlier_thresh is None:
        raise KeyError("The config must include 'upper_clip' threshold.")

    # Check if any key cols are missing
    cols = set(df.columns)
    if "711" not in cols:
        raise ValueError("employment column is missing.")

    # Multiply total employment by upper_clip to calculate number of outliers per cell.
    num_of_outliers = df["711"] * outlier_thresh

    # Apply outlier rounding
    s = num_of_outliers.apply(outlier_round)

    return s


def calculate_weighting_factor(
    df: pd.DataFrame, exp_col: str = "709"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Calculate the weighting factor 'a' for each cell in the survery data

    Note: A 'cell' is a group of businesses.

    Args:
        df (pd.DataFrame): The input df containing survey data
        cellno_dict (dict): Dictionary of cellnumbers and UNI_counts
        exp_col (str, optional): The column that is used to calculate n.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
        1) Returns the full dataframe with the added
        new column "a_weight".
        2) Returns a QA dataframe of all variables used in the calculation
    """
    cols = set(df.columns)
    if not ("outlier" in cols):
        raise ValueError("The column essential 'outlier' is missing.")
    df["outlier"] = df["outlier"].fillna(False)

    # Convert 709 column to numeric
    df["709"] = pd.to_numeric(df["709"], errors="coerce")

    # Default a_weight = 1 for all entries
    df["a_weight"] = 1.0

    grouped_by_cell = df.groupby("cellnumber", group_keys=False).apply(calc_a_weight)

    # Create a QA dataframe
    qa_frame = create_a_weight_qa_df(grouped_by_cell)
    grouped_by_cell = grouped_by_cell.drop(columns=["N", "n", "o"])
    return grouped_by_cell, qa_frame


def calc_a_weight(cell_group: pd.DataFrame) -> pd.DataFrame:
    """Calculate the 'a' weighting factor for a cell group.

    The calculation here is:

    a = (N-o) / (n-o)

    Where:
        - N is the total number of businesses in the cell
        - n is the number of businesses in sample for that cell
        - o is the number of outliers in the cell

    'o' is calculated in this function by summing all the `True` values
        because `True` == 1

    Args:
        cell_group (pd.DataFrame): The dataframe grouped by cellnumber.

    Returns:
        pd.DataFrame: The dataframe with the 'a' weighting factor calculated.
    """
    N = cell_group["uni_count"].iloc[0]

    estimation_filter = create_estimation_filter(cell_group)
    a_weight_filter = (cell_group["instance"] == 0) & cell_group["709"].notnull()
    filtered_group = cell_group.loc[estimation_filter & a_weight_filter]

    n = calc_lower_n(filtered_group)

    # Count the outliers for this group (will count all the `True` values)
    outlier_count = filtered_group["outlier"].sum()

    # Calculate 'a' for this group
    if n > 0:
        a_weight = (N - outlier_count) / (n - outlier_count)
    else:
        a_weight = 1.0

    cell_group["N"] = N
    cell_group["n"] = n
    cell_group["o"] = outlier_count
    cell_group.loc[estimation_filter, "a_weight"] = a_weight

    return cell_group


def create_a_weight_qa_df(df: pd.DataFrame) -> pd.DataFrame:
    """Create a QA dataframe for the a_weight calculation.

    Args:
        df (pd.DataFrame): The dataframe containing the a_weight column.

    Returns:
        pd.DataFrame: The QA dataframe.
    """
    est_filter = create_estimation_filter(df)

    qa_cols_list = ["cellnumber", "N", "n", "o", "a_weight"]
    qa_frame = df[qa_cols_list].loc[est_filter].groupby("cellnumber").first()
    qa_frame = qa_frame.reset_index()
    qa_frame = qa_frame.rename(
        columns={
            "cellnumber": "Cell Number",
            "N": "N - uni_count",
            "n": "n - num clear records in cell",
            "o": "o - num outliers in cell",
        }
    )

    return qa_frame


def outlier_weights(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate weights for outliers.

    If a reference has been flagged as an outlier,
    the 'a weight' value is set to 1.0

    Args:
        df (pd.DataFrame): The dataframe weights are calculated for.

    Returns:
        pd.DataFrame: The dataframe with the a_weights set to 1.0 for outliers.
    """
    df.loc[df["outlier"], "a_weight"] = 1.0
    return df
