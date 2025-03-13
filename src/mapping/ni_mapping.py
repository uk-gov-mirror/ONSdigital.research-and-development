import pandas as pd
import logging

from src.mapping.mapping_helpers import join_with_null_check

MappingLogger = logging.getLogger(__name__)


def join_itl_regions_ni(
    df: pd.DataFrame,
    itl_mapper: pd.DataFrame,
    config: dict,
    warn_only: bool = False,
) -> pd.DataFrame:
    """Joins the itl regions onto the NI dataframe using the mapper provided.

    Args:
        df (pd.DataFrame): The NI responses dataframes
        itl_mapper (pd.DataFrame): Mapper containing ITL regions
        config (dict): Pipeline configuration settings
        warn_only (bool, optional): Whether to warn only rather than error on nulls.

    Returns:
        pd.DataFrame: the responses dataframe with the ITL regions joined

    Unit Test:
        See [test_itl_mapping](./tests/mapping/test_itl_mapping.py)
    """
    # Instead of mapping itl from the postcodes, which we don't have for NI,
    # we fix the itl column to the value given in the config.
    df["itl"] = config["mappers"]["ni_itl"]

    # next join the itl mapper to add the region columns
    gb_itl_col = config["mappers"]["gb_itl"]
    geo_cols = [gb_itl_col] + config["mappers"]["geo_cols"]
    itl_mapper = itl_mapper[geo_cols].rename(columns={gb_itl_col: "itl"})

    df = join_with_null_check(df, itl_mapper, "itl mapper", "itl", warn=True)

    return df


def create_additional_ni_cols(ni_full_responses: pd.DataFrame) -> pd.DataFrame:
    """
    Create additional columns for Northern Ireland data.

    Args:
        df (pd.DataFrame): The NI responses DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with additional columns.
    """
    ni_full_responses["a_weight"] = 1
    ni_full_responses["g_weight"] = 1
    ni_full_responses["604"] = "Yes"
    ni_full_responses["form_status"] = 600
    ni_full_responses["602"] = 100.0
    ni_full_responses["formtype"] = "0003"

    return ni_full_responses
