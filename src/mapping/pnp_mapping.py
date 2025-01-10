import pandas as pd
import logging


MappingLogger = logging.getLogger(__name__)


def add_area_column(df):
    """
    Add area columns to the dataframe bassed on ITL121NM column.
    Args:
        df (pd.DataFrame): The dataframe to add the area columns to.
    Returns:
        pd.DataFrame: The dataframe with the area columns added.
    """
    area_dict = {
        "JG": "area_se",
        "GF": "area_se",
        "GG": "area_se",
        "HH": "area_se",
        "FE": "area_oth",
        "WW": "area_oth",
        "AA": "area_oth",
        "ED": "area_oth",
        "DC": "area_oth",
        "XX": "area_oth",
        "KJ": "area_oth",
        "BA": "area_oth",
        "BB": "area_oth",
    }

    df["area"] = df["region"].map(area_dict)

    return df


def identify_key_business(df, config):
    """Function to identify the key business using reference column & key
    busineses lookup table.
    Args:
        df (pd.DataFrame): The dataframe to identify the key business columns.
    Return:
        df (pd.DataFrame): The dataframe with the identified key business columns.
    """
    # get key businesses
    path = config["mapping_paths"]["key_references"]
    key_businesses_df = pd.read_csv(path)
    key_businesses_list = list(key_businesses_df["keys"])

    df["pnp_key"] = df["reference"].apply(
        lambda x: "key0" if x in key_businesses_list else "key1"
    )
    return df


def identify_osmotherly_businesses(df, config):
    """Function to identify the osmotherly businesses using reference
    column & osmotherly busineses lookup table.
    Args:
        df (pd.DataFrame): The dataframe to identify the osmotherly business
        columns.
    Return:
        df (pd.DataFrame): The dataframe with the identified osmotherly business
        columns.
    """
    # get osmotherly businesses
    path = config["mapping_paths"]["osmotherly_references"]
    osmotherly_businesses_df = pd.read_csv(path)
    osmotherly_businesses_list = list(osmotherly_businesses_df["ruref"])

    df["osmotherly"] = df["reference"].apply(
        lambda x: "osTrue" if x in osmotherly_businesses_list else "osFalse"
    )

    return df
