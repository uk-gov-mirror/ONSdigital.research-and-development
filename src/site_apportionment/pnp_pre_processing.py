import logging
import pandas as pd
import src.pipeline as src


from src.imputation.apportionment import run_apportionment

def pnp_pre_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Pre-process the PNP data.
    Args:
        df (pd.DataFrame): the main dataset to pre-process
    Returns:
        pd.DataFrame: pre-processed dataframe
    """
    df = run_apportionment(df)
    # Add a column for imputation marker
    df = pnp_imputation_marker(df)
    # Add a column for a weight
    df = pnp_weight(df)

    return df


# Add a column for imputation marker
def pnp_imputation_marker(df: pd.DataFrame) -> pd.DataFrame:
    """Initialize 'imp_marker' column with 'R' for clear responders and 'no_imputation' for others.
    Args:
        df (pd.DataFrame): the main dataset to add the imp_marker column to    
    Returns:
        pd.DataFrame: dataframe with the imp_marker column updated
    """
    # Initialise imp_marker column with a value of 'R' for clear responders
    # and a default value "no_imputation" for all other rows for now.
    df = run_apportionment(df)

    clear_responders_mask = df.status.isin(["Clear", "Clear - overridden"])
    df.loc[clear_responders_mask, "imp_marker"] = "R"
    df.loc[~clear_responders_mask, "imp_marker"] = "no_imputation"

    return df


# Add a column for a weight
def pnp_weight(df: pd.DataFrame) -> pd.DataFrame:

    """Add a class column to the PNP data.
  Args:
        df (pd.DataFrame): The input DataFrame.
    Returns:
        pd.DataFrame: The DataFrame with the added weight column.
    """
    # Add a class column to the PNP data
    df["a_weight"] = 1.0

    return df
