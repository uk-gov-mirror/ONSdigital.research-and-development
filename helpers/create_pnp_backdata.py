import pandas as pd
import numpy as np
import os
import toml

from pandas.testing import assert_frame_equal

from src.imputation.apportionment import run_apportionment
from src.staging import staging_helpers as stage_hlp
from src.staging.postcode_validation import format_postcodes
from src.imputation import imputation_helpers as hlp
from src.mapping.pg_conversion import pg_to_pg_mapper
from src.utils.config import config_setup
from src.utils.local_file_mods import rd_read_csv, rd_write_csv, rd_file_exists
import logging


MappingMainLogger = logging.getLogger(__name__)

root = "R:/BERD Results System Development 2023/DAP_emulation/2021_surveys/PNP/06_imputation/"  # noqa: E501
backdata_in_path = root + "backdata_prep/"

# Change to the project repository location
my_wd = os.getcwd()
my_repo = "research-and-development"
if not my_wd.endswith(my_repo):
    os.chdir(my_repo)

user_config_path = os.path.join(
    "src",
    "user_config.yaml"
)

dev_config_path = os.path.join(
    "src",
    "dev_config.yaml"
)

config = config_setup(
    user_config_path,
    dev_config_path
)


def convert_column_datatypes(df):
    """ Function to convert the column datatypes of a dataframe if they appear
    within backdata_schema.toml.

    Args:
        df (pd.DataFrame): The dataframe to convert the column datatypes.
    Return:
        DF (pd.DataFrame): The dataframe with the converted column datatypes.

    """
    with open('./config/backdata_schema.toml', 'r') as f:
        datatypes_config = toml.load(f)

    datatypes_dict = {}

    for column, datatype in datatypes_config.items():
        datatypes_dict.update({column: datatype["Deduced_Data_Type"]})

    for i in list(df.columns):
        if i in list(datatypes_dict.keys()):
            try:
                df[i] = df[i].astype(datatypes_dict[i])
            except:
                pass
        else:
            continue

    return df


def get_status_encoded(df):
    """ Function to populate the statusencoded column based on the mapping of the
    'map cora status to column "status"' column.

    Args:
        df (pd.DataFrame): The dataframe to populate the statusencoded column.
    Return:
        DF (pd.DataFrame): The dataframe with the populated statusencoded column.
    """
    cora_to_status_encoded_dict = {200: 100,
                                   100: 101,
                                   1000: 102,
                                   400: 200,
                                   500: 201,
                                   600: 210,
                                   800: 211,
                                   1200: 302,
                                   1300: 303,
                                   900: 304,
                                   1400: 309}

    df["statusencoded"] = df['map cora status to column "status"'].map(
        cora_to_status_encoded_dict
    )

    return df


def identify_key_business(df):
    """ Function to identify the key business using reference column & key
    busineses lookup table.

    Args:
        df (pd.DataFrame): The dataframe to identify the key business columns.
    Return:
        df (pd.DataFrame): The dataframe with the identified key business columns.
    """
    # get key businesses
    key_businesses_df = rd_read_csv(
        os.path.join(backdata_in_path,
                     "KEYS 2023.csv")
    )

    key_businesses_list = list(key_businesses_df["2023 KEYS"])

    df['pnp_key'] = df['reference'].apply(
        lambda x: 'key0' if x in key_businesses_list else 'key1'
    )

    return df


def identify_osmotherly_businesses(df):
    """ Function to identify the osmotherly businesses using reference
    column & osmotherly busineses lookup table.

    Args:
        df (pd.DataFrame): The dataframe to identify the osmotherly business
        columns.
    Return:
        df (pd.DataFrame): The dataframe with the identified osmotherly business
        columns.
    """
    # get osmotherly businesses
    osmotherly_businesses_df = rd_read_csv(
        os.path.join(backdata_in_path,
                     "Osmotherly PNP 2023.csv")
    )
    osmotherly_businesses_list = list(osmotherly_businesses_df["ruref"])

    df['osmotherly'] = df['reference'].apply(
        lambda x: "osTrue" if x in osmotherly_businesses_list else "osFalse"
    )

    return df


def get_status(df):
    """ Function to populate the status column based on the statusencoded column.

    Args:
        df (pd.DataFrame): The dataframe to populate the status column.
    Return:
        df (pd.DataFrame): The dataframe with the populated status column.
    """
    status_dict = {211: 'Clear - overridden',
                   210: 'Clear'}

    df['status'] = df['statusencoded'].map(status_dict)

    return df


def get_region(df):
    """ Function to populate ITL121NM columns bassed on Region.

    Mapping derived by analysis of raw data from CORA.

    Args:
        df (pd.DataFrame): The dataframe to populate the ITL121NM column.

    Return:
        df (pd.DataFrame): The dataframe with the populated ITL121NM column.
    """
    region_dict = {'HH': 'se',  # London
                   'JG': 'se',  # South East
                   'KJ': 'oth',  # South West
                   'GG': 'se',  # East of England
                   'GF': 'se',  # East of England
                   'FE': 'oth',  # West Midlands
                   'ED': 'oth',  # East Midlands
                   'DC': 'oth',  # Yorkshire and The Humber
                   'BA': 'oth',  # North West
                   'BB': 'oth',  # North West
                   'AA': 'oth',  # North East
                   'XX': 'oth',  # Scotland
                   'WW': 'oth',  # Wales
                   'YY': 'oth'  # Northern Ireland
                   }

    df['area'] = df['Region'].map(region_dict)

    return df


def map_to_yes_no(df):
    """
    Function to map integer values to Yes/No.

    Args:
        df (pd.DataFrame): The dataframe to map integer values to Yes/No.

    Return:
        df (pd.DataFrame): The dataframe with the integer values mapped to Yes/No.
    """
    mapper_dict = {1: "Yes", 2: "No", 3: np.nan}

    cols_to_map = ['101']

    for col in cols_to_map:
        df[col] = df[col].map(mapper_dict)

    df["604"] = "Yes"

    return df


def get_imp_marker(df):
    """ Function to populate the IMP_MARKER column based on the status column.

    Args:
        df (pd.DataFrame): The dataframe to populate the imp_marker column.
    Return:
        df (pd.DataFrame): The dataframe with the populated imp_marker column.
    """
    imp_marker_dict = {'Clear': 'R',
                       'Clear - overridden': 'R'}

    df['imp_marker'] = df['status'].map(imp_marker_dict)

    return df


def create_200(df):
    """ Function to create the 200 column.

    Args:
        df (pd.DataFrame): The dataframe to create the 200 column.
    Return:
        df (pd.DataFrame): The dataframe with the created 200 column.
    """
    df['200'] = "C"

    return df


def create_201(df, config, rd_file_exists, rd_read_csv):
    """ Function to create the 201 column.

    Args:
        df (pd.DataFrame): The dataframe to create the 201 column.
    Return:
        df (pd.DataFrame): The dataframe with the created 201 column.
    """
    # Load and validate the PG mappers
    pg_num_alpha = stage_hlp.load_validate_mapper(
        "pg_num_alpha_mapper_path",
        config,
        MappingMainLogger,
        rd_file_exists,
        rd_read_csv,
    )

    df = pg_to_pg_mapper(
        df,
        pg_num_alpha,
    )
    return df


def remove_leading_zeros(df):
    """ Function to remove the leading zeros from the reference column.

    Args:
        df (pd.DataFrame): The dataframe to remove the leading zeros
        from select colums.
    Return:
        df (pd.DataFrame): The dataframe with the leading zeros removed
        select columns.
    """
    df.columns = df.columns.str.replace(r'^0+', '', regex=True)

    return df


def add_missing_columns(df):
    """ Function that manually add missing column to PNP backdata.

    The reason for this function is current 2023 backdata contains quesitons that
    did not exists in the old 2021 survey. This function adds these missing columns
    and poopulated them with null values.

    Args:
        df (pd.DataFrame): The dataframe to add the missing columns.

    Return:
        df (pd.DataFrame): The dataframe with the added missing columns.
    """
    missing_list = ['226', '228', '237', '203', '225', '227', '229']
    for col in missing_list:
        if col not in df.columns:
            df[col] = np.nan

    return df


def clean_postcodes(df):
    """ Function to format the postcodes in the dataframe.

    Args:
        df (pd.DataFrame): The dataframe to format the postcodes.

    Return:
        df (pd.DataFrame): The dataframe with the formatted postcodes.
    """
    df["601"] = df["601"].str.replace("'", "")
    df["601"] = df["601"].apply(format_postcodes)


    return df


def populate_instance_1_columns(df, config):
    """ Function to populate instance 1 columns that begin with 3 or 2.

    Args:
        df (pd.DataFrame): The dataframe to populate the instance 1 columns.

    Return:
        df (pd.DataFrame): The dataframe with the populated instance 1 columns.
    """
    # a list of columns to be updated
    numcols = config["breakdowns"]["211"] + config["breakdowns"]["305"] + ["211", "305"]
    cols = [c for c in numcols if c in df.columns]

    # the rows which contain the data use for the updates
    source_df = df[df["instance"] == 0].copy()[["reference"]  + cols]
    # the dataframe to be used for the update
    update_df = source_df.copy()
    update_df["instance"] = 1

    # add extra rows with instance 1 to the original dataframe if a reference does not
    # have an istance = 1 row
    refs_with_ins_1 = df[df["instance"] == 1]["reference"].unique()
    refs_without_ins_1 = set(source_df["reference"].unique()) - set(refs_with_ins_1)

    extra_rows_df = df[df["reference"].isin(refs_without_ins_1)].copy()
    extra_rows_df["instance"] = 1

    df = pd.concat([df, extra_rows_df], ignore_index=True)

    merged_df = pd.merge(df, update_df, on=["reference", "instance"], how="left", suffixes=("", "_y"))

    # replace all values in the columns with the values from the update_df
    for col in cols:
        merged_df.loc[merged_df["instance"] == 1, col] = merged_df[col + "_y"]
        merged_df.loc[merged_df["instance"] == 0, col] = 0
        merged_df.drop(columns=[col + "_y"], inplace=True)

    return merged_df


def test_populate_instance_1_columns():
    """Test populate_instance_1_columns function."""

    # Example input DataFrame
    data = {
        "reference": [1, 1, 2, 2, 3, 3, 4],
        "instance": [0, 1, 0, 1, 0, 1, 0],
        "211": [10, 0, 20, 5, 30, 0, 40],
        "305": [30, 0, 40, 10, 50, 0, 60],
        "202": [100, 200, 300, 400, 500, 600, 700],
        "301": [100, 200, 300, 400, 500, 600, 700],
        "oth": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    }
    df = pd.DataFrame(data)

    # Example config
    config = {
        "breakdowns": {
            "211": ["202"],
            "305": ["301"]
        }
    }

    # Define the expected output DataFrame
    expected_data = {
        "reference": [1, 1, 2, 2, 3, 3, 4, 4],
        "instance": [0, 1, 0, 1, 0, 1, 0, 1],
        "211": [0, 10, 0, 20, 0, 30, 0, 40],
        "305": [0, 30, 0, 40, 0, 50, 0, 60],
        "202": [0, 100, 0, 300, 0, 500, 0, 700],
        "301": [0, 100, 0, 300, 0, 500, 0, 700],
        "oth": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.0]
    }
    expected_df = pd.DataFrame(expected_data)

    # Call the function
    result_df = populate_instance_1_columns(df, config)

    # Assert that the result DataFrame is equal to the expected DataFrame
    assert_frame_equal(result_df, expected_df, check_dtype=False)


def create_pnp_backdata(df):
    """ Function to clean the PNP backdata.

    Steps taken inclide 1. removing unwamted columns, and 2. renaming wanted columns.

    Args:
        df (pd.DataFrame): The dataframe to clean.
    Return:
        pd.DataFrame: The cleaned dataframe.
    """
    columns_to_remove_list = ['InquiryIDBRCode',
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
                              'ReceiptDate',
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
                              'CellSelection',
                              'CurrentSIC',
                              'Tel',
                              'Turnover',
                              'TOfro',
                              'TOIDBR',
                              'RUSICprev',
                              'SICcurfro',
                              'SICprevfro',
                              'SICprev',
                              'map cora status to column "status"',
                              'q0001',
                              'q0002',
                              'q0003',
                              'q0203',
                              'q0205',
                              'q0207',
                              'q0209',
                              'q0211',
                              'q0213',
                              'q0215',
                              'q0217',
                              'q0219',
                              'q0223',
                              'q0225',
                              'q0227',
                              'q0229',
                              'q0230',
                              'q0302',
                              'q0304',
                              'q0306',
                              'q0308',
                              'q0310',
                              'q0312',
                              'q0314',
                              'q0316',
                              'q0318',
                              'q0319',
                              'q0320',
                              'q0322',
                              'q0324',
                              'q0326',
                              'q0327',
                              'q0328',
                              'q0330',
                              'q0331',
                              'q0332',
                              'q0333',
                              'q0334',
                              'q0335',
                              'q0336',
                              'q0337',
                              'q0338',
                              'q0339',
                              'q0340',
                              'q0341',
                              'q0342',
                              'q0343',
                              'q0344',
                              'q0345',
                              'q0346',
                              'q0603',
                              'q0703',
                              'q0704',
                              'q0705',
                              'q0706',
                              'q0701',
                              'q0702',
                              'q0901',
                              'q0903',
                              'q0905',
                              'q0907',
                              'q0909',
                              'pnp_key',
                              'osmotherly',
                              'area',
                              ]

    columns_to_rename_dict = {'IDBRPeriod': 'period',
                              'FormType': 'formtype',
                              'RUReference': 'reference',
                              'FormStatus': 'map cora status to column "status"',
                              'Employees': 'emp_total',
                              'Year': 'period_year',
                              'Instance': 'instance',
                              'RUSICcur': '201',
                              'q0101': '101',
                              'q0102': '103',
                              'q0103': '104',
                              'q0201': '604',
                              'q0202': '210',
                              'q0204': '219',
                              'q0206': '220',
                              'q0208': '209',
                              'q0210': '221',
                              'q0212': '204',
                              'q0214': '202',
                              'q0216': '222',
                              'q0218': '223',
                              'q0222': '211',
                              'q0224': '205',
                              'q0226': '206',
                              'q0228': '207',
                              'q0301': '212',
                              'q0303': '214',
                              'q0305': '216',
                              'q0307': '242',
                              'q0309': '243',
                              'q0311': '244',
                              'q0313': '245',
                              'q0315': '246',
                              'q0317': '247',
                              'q0321': '248',
                              'q0323': '249',
                              'q0325': '218',
                              'q0329': '250',
                              'q0501': '501',
                              'q0502': '502',
                              'q0503': '503',
                              'q0504': '504',
                              'q0505': '505',
                              'q0506': '506',
                              'q0507': '507',
                              'q0508': '508',
                              'q0509': '405',
                              'q0510': '406',
                              'q0511': '407',
                              'q0512': '408',
                              'q0513': '409',
                              'q0514': '410',
                              'q0515': '411',
                              'q0516': '412',
                              'q0601': '601',
                              'q0602': '602',
                              'q0902': '302',
                              'q0904': '303',
                              'q0906': '304',
                              'q0908': '305'}

    new_column_order = ['period', 'reference', 'formtype', 'Region',
                        'period_year', 'instance', '101', '103', '104', '200', '201',
                        '202', '203', '204', '205', '206', '207', '209', '210',
                        '211', '212', '214', '216', '218', '219', '220', '221',
                        '222', '223', '225', '226', '227', '228', '229', '237',
                        '242', '243', '244', '245', '246', '247', '248', '249', '250',
                        '302', '303', '304', '305',
                        '405', '406', '407', '408', '409', '410', '411', '412',
                        '501', '502', '503', '504', '505', '506', '507', '508',
                        '601', '602', '604',
                        'statusencoded', 'status', 'imp_marker', 'imp_class',
                        'emp_researcher', 'emp_technician', 'emp_other', 'emp_total',
                        'headcount_res_m','headcount_res_f',
                        'headcount_tec_m', 'headcount_tec_f',
                        'headcount_oth_m', 'headcount_oth_f',
                        'headcount_tot_m','headcount_tot_f', 'headcount_total']

    # Rename wanted columns
    df = df.rename(columns=columns_to_rename_dict)

    # convert column datatypes
    df = convert_column_datatypes(df)

    # Populate the statusencoded column
    df = get_status_encoded(df)

    # Filter the DataFrame for rows where statusencoded is 210 or 211
    df = df[df['statusencoded'].isin([210, 211])]

    # Populate status column
    df = get_status(df)

    # Populate the imp_marker column
    df = get_imp_marker(df)

    # Identify the key business
    df = identify_key_business(df)

    # Identify the osmotherly business
    df = identify_osmotherly_businesses(df)

    # Region mapping
    df = get_region(df)

    # Map integer values to Yes/No
    df = map_to_yes_no(df)

    # Create the 200 column
    df = create_200(df)

    # Create the 201 columns
    df = create_201(
        df,
        config,
        rd_file_exists,
        rd_read_csv
    )

    # Create the imp_class column
    df = hlp.create_imp_class_col(
        df,
        ["pnp_key", "area"],
        use_osmotherly=True,
        use_cellno=False
    )

    # strip leading 0's from select columnns
    df = remove_leading_zeros(df)

    # add missing columns manually
    df = add_missing_columns(df)

    # clean postcodes
    df = clean_postcodes(df)

    # Test the populate_instance_1_columns function
    test_populate_instance_1_columns()

    # Populate instance 1 columns that begin with 3xx or 2xx.
    df = populate_instance_1_columns(df, config)

    # Run the apportionment on the PNP backdata
    df = run_apportionment(df)

    # Remove unwanted columns if the occur in the dataframe
    to_remove = [col for col in columns_to_remove_list if col in df.columns]
    df = df.drop(columns=to_remove)

    # Re-order columns to match BERD (for ease of comparrison)
    df = df[[c for c in new_column_order if c in df.columns]]
    # df = df[new_column_order]

    return df


def main():
    """ Main function to clean the PNP backdata.

    Read in csv file as a dataframe, clean with create_pnp_backdata function,
    and save dataframe as a csv file.

    Example cmd executiion: python create_pnp_backdata.py input.csv output.csv

    Args:
        input_file (str): The path to the input CSV file.
        output_file (str): The path to save the cleaned CSV file.
    Return:
        None
    """

    # Read the input CSV file into a DataFrame
    df = rd_read_csv(
        os.path.join(backdata_in_path,
                     "210_202112 Raw data from CORA.csv")
    )

    # Clean the DataFrame
    pnp_backdata_df = create_pnp_backdata(df)

    # Save the cleaned DataFrame to the output CSV file
    backdata_out_path = backdata_in_path

    rd_write_csv(
        os.path.join(
            backdata_out_path,
            "PNP_2021_backdata_for_checking.csv"),
        pnp_backdata_df
    )


if __name__ == "__main__":
    main()

# Example usage of the test function
# if __name__ == "__main__":
#     test_populate_instance_1_columns()
