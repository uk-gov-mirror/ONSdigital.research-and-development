"""Define helper functions to be used throughout the pipeline.."""
import yaml
import toml
import pandas as pd
import numpy as np

from typing import Union

from src.utils.defence import type_defence
from src.mapping.itl_mapping import join_itl_regions

# Define paths
user_config_path = "config/userconfig.toml"


class ConfigSettings:
    """Get the config settings from the config file."""

    def __init__(self, config_path):
        self.config_file = config_path
        self.config_dict = self._get_config_settings()

    def _get_config_settings(self):
        """Get the config settings from the config file."""
        with open(self.config_file, "r") as file:
            config = yaml.safe_load(file)

        return config


def user_config_reader(configfile: str = user_config_path) -> dict:
    """Function to parse the userconfig.toml file

    Args:
        configfile (str, optional): _description_. Defaults to user_config_path.

    Returns:
        dict: A nested dictionary where the keys are section titles within the TOML
        file.
        If only one variable under the section title in the TOML file is given
        then it is passed directly as a dictionary value. If more than one
        variable is defined then they are parsed as a dictionary themselves.
        An example of what is returned is given below:

        {'title': 'TOML Example config', 'period': {'start_period':
        datetime.date(1990, 10, 10), 'end_period': datetime.date(2000, 10, 5)}}
    """
    toml_dict = toml.load(configfile)

    return toml_dict


def period_select() -> tuple:
    """Function returning the start and end date under consideration.


    Returns:
        tuple: A tuple containing two datetime.date objects. The first is the
        start date of the period under consideration, the second is the
        end date of that period.
        Example:
            (datetime.date(1990, 10, 10), datetime.date(2000, 10, 5))
    """

    period_dict = user_config_reader()["period"]

    return period_dict["start_period"], period_dict["end_period"]


def convert_formtype(formtype_value: str) -> str:
    """Convert the formtype to a standardised format.

    Args:
        formtype_value (str): The value to standardise.

    Returns:
        str: The standardised value for formtype.
    """
    if pd.notnull(formtype_value):
        formtype_value = str(formtype_value)
        if formtype_value == "1" or formtype_value == "1.0" or formtype_value == "0001":
            return "0001"
        elif (
            formtype_value == "6" or formtype_value == "6.0" or formtype_value == "0006"
        ):
            return "0006"
        else:
            return None
    else:
        return None


def values_in_column(
    df: pd.DataFrame, col_name: str, values: Union[list, pd.Series]
) -> bool:
    """Determine whether a list of values are all present in a dataframe column.

    Args:
        df (pd.DataFrame): The dataframe.
        col_name (str): The column name.
        values (Union[list, pd.Series]): The values to check.

    Returns:
        bool: Whether or values are in the column.
    """
    type_defence(df, "df", pd.DataFrame)
    type_defence(col_name, "col_name", str)
    type_defence(values, "values", (list, pd.Series))
    if isinstance(values, pd.Series):
        values = list(values)
    result = set(values).issubset(set(df[col_name]))
    return result


def validate_updated_postcodes(
    df: pd.DataFrame,
    postcode_mapper: pd.DataFrame,
    itl_mapper: pd.DataFrame,
    config: dict,
) -> pd.DataFrame:
    """Update the postcodes_harmonised column and re-map the itl columns.

    Args:
        df (pd.DataFrame): The full responses dataframe.
        postcode_mapper (pd.DataFrame): The postcode mapper dataframe mapping to itl.
        itl_mapper (pd.DataFrame): The ITL mapper dataframe mapping to ITL regions.
        config (dict): The pipeline configuration settings.

    Returns:
        pd.DataFrame: The updated full responses dataframe with the postcodes_harmonised
            column updated and the itl columns re-mapped.
    """
    # filter out records that have been constructed or imputed with backdata
    imp_marker_mask = df["imp_marker"].isin(["CF", "MoR", "constructed"])
    if "is_constructed" in df.columns:
        constructed_mask = df["is_constructed"].isin([True])
        mask = imp_marker_mask | constructed_mask
    else:
        mask = imp_marker_mask
    filtered_df = df.copy().loc[mask]

    # re-calculate the itl columns based on imputed and constructed columns
    geo_cols = config["mappers"]["geo_cols"]
    filtered_df = filtered_df.copy().drop(["itl"] + geo_cols, axis=1)
    filtered_df = join_itl_regions(
        filtered_df,
        postcode_mapper,
        itl_mapper,
        config,
        pc_col="postcodes_harmonised",
        warn_only=True,
    )

    filtered_df = filtered_df[list(df.columns)]

    df = pd.concat([df.loc[~mask], filtered_df])
    return df


def tree_to_list(tree: dict, path_list: list = [], prefix: str = "") -> list:
    """
    Convert a dictionary of paths to a list.

    This function converts a directory tree that is provided as a dictionary to a
    list of full paths. This is done recursively, so the number of tiers is not
    pre-defined. Returns a list of absolute directory paths.
    Directory and subdirectory names must be the keys in the dictionary.
    Directory that has no sub-directories must point to an empty dictionary {}.

    Example
    Input data
    mydict = {
        "BERD": {
            "01":{},
            "02":{},
        },
        "PNP": {
            "03":{},
            "04":{"qa":{}},
        },
    }

    Usage: tree_to_list(mydict, prefix="R:/2023")

    Result:
    ['R:/2023/BERD', 'R:/2023/BERD/01', 'R:/2023/BERD/02', 'R:/2023/PNP',
    'R:/2023/PNP/03', 'R:/2023/PNP/04', 'R:/2023/PNP/04/qa']

    Args:
        tree (dict): The whole tree or its branch
        path_list (list): A list of full paths that is populated when the function
            runs. Must be empty when you call the function.
        prefix (str): The common prefix. It should start with the platform-
            specific root, such as "R:/dap_emulation" or "dapsen/workspace_zone_res_dev"
            followed by the year_surveys. Do not add a forward slash at the end.

    Returns:
        A list of all absolute paths

    """
    # Separator is hardcoded to avoid any errors.
    sep = "/"

    # Input must be a dictionary of dictionaries or an empty dictionary
    if isinstance(tree, dict):
        # The recursive iteration will proceed if the current tree is not empty.
        # The recursive iterations will stop once we reach the lowest level
        # indicated by an empty dictionary.
        if tree:
            # For a non-empty dictionary, iterating through all top-level keys.
            for key in tree:
                if prefix == "":
                    # If the prefix is empty, we don't want to start from slash. We
                    # just set the prefix to be the key, which is the directory name
                    mypref = key
                else:
                    # If the prefix is not empty, we add the separator and the
                    # directory name to it
                    mypref = prefix + sep + key

                # The updated prefix is appended to the path list
                path_list += [mypref]

                # Doing the same for the underlying sub-directory
                path_list = tree_to_list(tree[key], path_list, mypref)

        return path_list
    else:
        raise TypeError(f"Input must be a dictionary, but {type(tree)} is given")


def clean_pnp_backdata(df):
    """ Function to clean the PNP backdata.

    Steps taken inclide 1. removing unwamted columns, and 2. renaming wanted columns.

    Args:
        df (pd.DataFrame): The dataframe to clean.
    Return:
        pd.DataFrame: The cleaned dataframe.

    """
    columns_to_remove = ['InquiryIDBRCode',
                         'Upddate',
                         'Addr1',
                         'Addr2',
                         'Addr3',
                         'Addr4',
                         'Addr5',
                         'Name',
                         'Contact',
                         'Curr',
                         'Email',
                         'EmpsIDBR',
                         'Empt',
                         'Emptfro',
                         'Entref',
                         'Entgroup',
                         'VETs',
                         'DataSource',
                         'Formver',
                         'FTE',
                         'FTEfro',
                         'Updby',
                         'Legstatus',
                         'Lockdate',
                         'Lockby',
                         'MC',
                         'Month',
                         'NS',
                         'Nonresp',
                         'PC',
                         'ReceiptDate',
                         'RUSICcur',
                         'RUSICprev',
                         'CellSelection',
                         'SICcurfro',
                         'CurrentSIC',
                         'SICprevfro',
                         'SICprev',
                         'Tel',
                         'Turnover',
                         'TOfro',
                         'TOIDBR',
                         'q001',
                         'q002',
                         'q003',
                         'q203',
                         'q205',
                         'q207',
                         'q209',
                         'q211',
                         'q213',
                         'q215',
                         'q217',
                         'q219',
                         'q223',
                         'q225',
                         'q227',
                         'q229',
                         'q302',
                         'q304',
                         'q306',
                         'q308',
                         'q310',
                         'q312',
                         'q314',
                         'q316',
                         'q318',
                         'q319',
                         'q320',
                         'q322',
                         'q324',
                         'q326',
                         'q0327',
                         'q0328',
                         'q330',
                         'q510',
                         'q512',
                         'q514',
                         'q516',
                         'q603',
                         'q703',
                         'q704',
                         'q705',
                         'q706',
                         'q0901',
                         'q0903',
                         'q0905',
                         'q0907',
                         'q0909']

    columns_to_rename_dict = {'IDBRPeriod': 'period',
                              'FormType': 'formtype',
                              'RUReference': 'reference',
                              'FormStatus': 'map cora status to column "status"',
                              'Employees': 'employees',
                              'Region': np.nan,
                              'Year': 'period_year',
                              'Instance': 'instance',
                              'q101': '101',
                              'q102': '103',
                              'q103': '104',
                              'q201': '604',
                              'q202': '210',
                              'q204': '219',
                              'q206': '220',
                              'q208': '209',
                              'q210': '221',
                              'q212': '204',
                              'q214': '202',
                              'q216': '222',
                              'q218': '223',
                              'q222': '211',
                              'q224': '205',
                              'q226': '205',
                              'q228': '206',
                              'q230': '605',
                              'q301': '212',
                              'q303': '214',
                              'q305': '216',
                              'q307': '242',
                              'q309': '243',
                              'q311': '244',
                              'q313': '245',
                              'q315': '246',
                              'q317': '247',
                              'q321': '248',
                              'q323': '249',
                              'q325': '218',
                              'q329': '250',
                              'q501': '501',
                              'q502': '502',
                              'q503': '503',
                              'q504': '504',
                              'q505': '505',
                              'q506': '506',
                              'q507': '507',
                              'q508': '508',
                              'q509': '405',
                              'q511': '407',
                              'q513': '409',
                              'q515': '411',
                              'q601': '601',
                              'q602': '602',
                              'q701': '708',
                              'q702': '712',
                              'q0902': '302',
                              'q0904': '303',
                              'q0906': '304',
                              'q0908': '305'}

    # Remove unwanted columns
    df = df.drop(columns=columns_to_remove, errors="ignore")

    # Rename wanted columns
    df = df.rename(columns=columns_to_rename_dict)

    return df