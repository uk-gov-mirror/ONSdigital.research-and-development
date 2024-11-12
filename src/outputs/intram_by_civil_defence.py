"""The main file for the BERD Intram by Civil or Defence output."""
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Callable, Dict, Any

OutputMainLogger = logging.getLogger(__name__)


def output_intram_by_civil_defence(
    df: pd.DataFrame,
    config: Dict[str, Any],
    write_csv: Callable,
    run_id: int,    
):
    """Run the outputs module.

    Args:
        df (pd.DataFrame): The dataset main with weights not applied
        config (dict): The configuration settings.
        write_csv (Callable): Function to write to a csv file.
         This will be the hdfs or network version depending on settings.
        run_id (int): The current run id       


    """
    output_path = config["outputs_paths"]["outputs_master"]

    period = config["survey"]["survey_year"]
    period_str = str(period)

    # Group by civil/defence (200) and aggregate intram (211)
    key_col = "200"
    value_col = "211"

    df_agg = df.groupby([key_col]).agg({value_col: "sum"}).reset_index()

    # Replace C and D with Civil or Defence
    df_agg["200"] = df_agg["200"].replace({"C": "Civil", "D": "Defence"})

    # Rename Columns with dictionary
    columns = ({'200': 'Catergory', '211': 'Total Intramural Expenditure'}) df_for_output = df_agg.rename(columns=columns)

    df_for_output = df_agg.rename(columns=columns)

    # Outputting the CSV file with timestamp and run_id
    tdate = datetime.now().strftime("%y-%m-%d")
    survey_year = config["survey"]["survey_year"]
    filename = f"{survey_year}_output_intram_by_civil_defence{tdate}_v{run_id}.csv"
    write_csv(f"{output_path}/output_intram_by_civil_defence/{filename}", df_for_output)
