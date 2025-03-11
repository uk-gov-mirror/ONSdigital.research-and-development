import pandas as pd
import logging


ManualImputationLogger = logging.getLogger(__name__)


def merge_manual_imputation(
    df: pd.DataFrame,
    manual_trim_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Loads a manual trimming file if it exists and adds a manual_trim column
    to the DataFrame.

    Args:
        config (Dict[str, Any]): The configuration dictionary.
        df (pd.DataFrame): The dataframe to be imputed.
        isfile_func (callable): The function to use to check if the file exists.
    Returns:
        pd.DataFrame: The DataFrame with the manual_trim column added.
    """
    if manual_trim_df is not None:
        if "manual_trim" in df.columns:
            df = df.drop(columns=["manual_trim"])
        manual_trim_df = manual_trim_df.astype({"instance": "float64"})

        df = df.merge(manual_trim_df, on=["reference", "instance"], how="left")
        df["manual_trim"] = df["manual_trim"].fillna(False).astype(bool)

        ManualImputationLogger.info(
            "manual imputation dataframe joined to responses dataframe"
        )
    else:
        if "manual_trim" not in df.columns:
            df["manual_trim"] = False
    return df
