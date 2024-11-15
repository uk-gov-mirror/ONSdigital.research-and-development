"""Utility functions for the freezing module."""
from datetime import datetime
from typing import Tuple, Dict

import pandas as pd

from src.utils.defence import type_defence


def _add_last_frozen_column(frozen_df: pd.DataFrame,
                            config: dict) -> pd.DataFrame:
    """Add the last_frozen column to staged data.

    Args:
        frozen_df (pd.DataFrame): The frozen data.
        config (Dict[str, Any]): The pipeline configuration.

    Returns:
        pd.DataFrame: A dataframe containing the updated last_frozen column.
    """
    type_defence(frozen_df, "frozen_df", pd.DataFrame)
    type_defence(config, "run_id", Dict)
    todays_date = datetime.today().strftime("%y-%m-%d")
    run_id = config["filename_items"]["run_id"]
    last_frozen = f"{todays_date}_v{str(run_id)}"
    frozen_df["last_frozen"] = last_frozen
    return frozen_df
