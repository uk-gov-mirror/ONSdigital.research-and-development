"""The main file for the Apportionment to sites module."""
import logging
import pandas as pd
from typing import Callable, Dict, Any

from src.site_apportionment.site_apportionment import run_apportion_sites
from src.site_apportionment.output_status_filtered import (
    output_status_filtered,
    calc_weighted_intram_tot,
)
from src.utils.local_file_mods import filename_amender

SitesMainLogger = logging.getLogger(__name__)


def run_site_apportionment(
    df: pd.DataFrame,
    config: Dict[str, Any],
    write_csv: Callable,
    run_id: int,
) -> pd.DataFrame:
    """Run the apportionment to sites module.

    For short forms, the percentage is set to 100% on all instances.
    For long forms, the percentage is used to apportion the variables from
    instance 0 to all other instances.
    Same percentages are used for each product group.

    Args:
        df (pd.DataFrame): Main dataset before the outputs module.
        config (dict): The pipeline configuration
        intram_tot_dict (dict): Dictionary with the intramural totals.
        write_csv (Callable): Function to write to a csv file.
            This will be the hdfs or network version depending on settings.
        run_id (int): The current run id
    Returns:
        df_out (pd.DataFrame): Percentages filled in for short forms and applied
            to apportion  for long forms
    """
    # Create variable for output of QA apportionment file
    qa_path = config["apportionment_paths"]["qa_path"]

    imp_markers_to_keep: list = ["R", "TMI", "CF", "MoR", "constructed"]

    # Conditionally output the records to be removed
    if config["global"]["output_status_filtered"]:
        output_status_filtered(df, imp_markers_to_keep, config, write_csv, run_id)

    # Calculate the intramural totals before apportionment
    intram_tot_dict = {}
    intram_tot_dict = calc_weighted_intram_tot(df, imp_markers_to_keep, intram_tot_dict)

    SitesMainLogger.info("Starting apportionment to sites...")
    df_out = run_apportion_sites(df, imp_markers_to_keep, config, intram_tot_dict)

    # recaluculate the intermural totals after apportionment
    intram_tot_dict = calc_weighted_intram_tot(
        df_out, imp_markers_to_keep, intram_tot_dict
    )

    # Output QA files
    if config["global"]["output_apportionment_qa"]:
        SitesMainLogger.info("Outputting Apportionment files.")
        filename = "estimated_apportioned"
        filename = filename_amender(filename, config)
        write_csv(f"{qa_path}/{filename}", df_out)

    SitesMainLogger.info("Finished apportionment to sites.")
    return df_out, intram_tot_dict
