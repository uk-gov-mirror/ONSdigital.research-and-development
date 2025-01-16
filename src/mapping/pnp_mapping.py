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
