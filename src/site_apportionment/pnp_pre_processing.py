import logging
import pandas as pd
import src.pipeline as src


def pnp_pre_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Pre-process the PNP data.
    Args:
        df (pd.DataFrame): the main dataset to pre-process
    Returns:
        pd.DataFrame: pre-processed dataframe
    """
    # Add a column for imputation marker
    pnp_imputation_marker(df)
    # Add a column for a weight
    pnp_weight(df)
     # Add a column for pg_num_col
    pnp_pg_numeric(df)

    return df



# Add a column for imputation marker
def pnp_imputation_marker(df: pd.DataFrame) -> pd.DataFrame:
    """Initialise imp_marker column with a value of 'R' or 'no imputation' for all 
    responders to have the column to run outputs module.
    Args:
        df (pd.DataFrame): the main dataset to add the imp_marker column to        
    Returns:
        pd.DataFrame: dataframe with the imp_marker column updated
    """
    # Initialise imp_marker column with a value of 'R' for clear responders
    # and a default value "no_imputation" for all other rows for now.
    clear_responders_mask = df.status.isin(["Clear", "Clear - overridden"])
    df.loc[clear_responders_mask, "imp_marker"] = "R"
    df.loc[~clear_responders_mask, "imp_marker"] = "no_imputation"
    return


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


# Add a column for pg_numeric

def pnp_pg_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Add a pg_num_col column to the PNP data.    
    Args:
        df (pd.DataFrame): the main dataset to add the pg_num_col column to        
    Returns:
        pd.DataFrame: dataframe with the pg_num_col column updated
    """
    # Add a pg_num_col column to the PNP data
    df["pg_numeric"] = 10
    return df

