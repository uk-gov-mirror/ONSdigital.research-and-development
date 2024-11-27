import logging
import pandas as pd

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
def pnp_weight(df:pd.Dataframe) -> pd.DataFrame:

    """Add a class column to the PNP data.
    Args:
        df (pd.DataFrame): the main dataset to add the class column to        
    Returns:
        pd.DataFrame: dataframe with the class column updated
    """
    # Add a class column to the PNP data
    df["a weight"] = 1
    return  


# Add a column for headcount
def pnp_headcount_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add a headcount column to the PNP data.    
    Args:
        df (pd.DataFrame): the main dataset to add the headcount column to        
    Returns:
        pd.DataFrame: dataframe with the headcount column updated
    """
    # Add a headcount column to the PNP data
    df["headcount"] = 50
    return
