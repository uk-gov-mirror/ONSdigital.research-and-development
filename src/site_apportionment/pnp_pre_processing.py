import logging
import pandas as pd
import src.pipeline as src


from src.imputation.apportionment import run_apportionment
from src.imputation.imputation_helpers import imputation_marker

def pnp_pre_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Pre-process the PNP data.
    Args:
        df (pd.DataFrame): the main dataset to pre-process
    Returns:
        pd.DataFrame: pre-processed dataframe
    """
    df = run_apportionment(df)
    # Add a column for imputation marker
    df = imputation_marker(df)
    # Add a column for a weight
    df["a_weight"] = 1.0
    
    return df