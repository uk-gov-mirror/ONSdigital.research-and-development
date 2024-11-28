import argparse
import os
import pandas as pd
import toml
import re
from src.imputation.apportionment import run_apportionment
from src.staging import postcode_validation as pcval

rootpath = "R:/BERD Results System Development 2023/DAP_emulation/2021_surveys/PNP/"


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
    key_businesses_df = pd.read_csv(os.path.join(rootpath, 'KEYS 2023.csv'))
    key_businesses_list = list(key_businesses_df["2023 KEYS"])

    df['pnp_key'] = df['reference'].apply(
        lambda x: 'Key0' if x in key_businesses_list else 'Key1'
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
    osmotherly_businesses_df = pd.read_csv(os.path.join(rootpath,
                                                        "Osmotherly PNP 2023.csv"))
    osmotherly_businesses_list = list(osmotherly_businesses_df["ruref"])

    df['osmotherly'] = df['reference'].apply(
        lambda x: True if x in osmotherly_businesses_list else False
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
    region_dict = {'HH': 'London',
                   'JG': 'South East',
                   'KJ': 'South West',
                   'GG': 'East of England',  # GG or GF
                   'FE': 'West Midlands',
                   'ED': 'East Midlands',
                   'DC': 'Yorkshire and The Humber',
                   'BB': 'North West',  # BA or BB
                   'AA': 'North East',
                   'XX': 'Scotland',
                   'WW': 'Wales',
                   'YY': 'Northern Ireland'
                   }

    df['ITL121NM'] = df['Region'].map(region_dict)

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


def create_201(df):
    """ Function to create the 201 column.

    Args:
        df (pd.DataFrame): The dataframe to create the 201 column.
    Return:
        df (pd.DataFrame): The dataframe with the created 201 column.
    """
    rusic_dict = {72190: 'AF',
                  62020: 'AE',
                  70229: 'AD',
                  71200: 'AD',
                  88100: 'AG',
                  88990: 'AG',
                  59120: 'AD',
                  94110: 'AG',
                  72200: 'AF',
                  94120: 'AG',
                  52220: 'AH',
                  91040: 'AG',
                  86102: 'AG',
                  94990: 'AG',
                  93199: 'AG',
                  71111: 'Z',
                  71122: 'AD',
                  71129: 'AB',
                  85590: 'AG',
                  86101: 'AG',
                  71121: 'AD',
                  94200: 'AG',
                  68201: 'AD',
                  82990: 'AD',
                  86900: 'AG',
                  61900: 'AC',
                  72110: 'AF',
                  2100: 'A',
                  73120: 'AD',
                  71112: 'AD',
                  73200: 'AD',
                  69202: 'AD',
                  96090: 'AG',
                  86210: 'AG',
                  88910: 'AG',
                  47799: 'AA',
                  74909: 'AF',
                  87900: "AG",
                  68209: "AD"}

    df['201'] = df['RUSICcur'].map(rusic_dict)

    return df


def prep_2021_backdata(backdata) -> pd.DataFrame:
    """Prepare the backdata for MoR imputation.
    Args:
        backdata (pd.DataFrame): Backdata for the current year.
    Returns:
        pd.DataFrame: Prepped backdata.
    """
    # Convert backdata column names from qXXX to XXX
    # Note that this is only applicable when using the backdata on the network
    p = re.compile(r"q\d{3}")
    cols = [col for col in list(backdata.columns) if p.match(col)]
    to_rename = {col: col[1:] for col in cols}
    backdata = backdata.rename(columns=to_rename)

    # Apply the postcode formatting to clean the postcodes in col 601 of the back data
    backdata["601"] = backdata["601"].apply(pcval.format_postcodes)

    return backdata


def remove_leading_zeros(df):
    """ Function to remove the leading zeros from the reference column.

    Args:
        df (pd.DataFrame): The dataframe to remove the leading zeros
        from select colums.
    Return:
        df (pd.DataFrame): The dataframe with the leading zeros removed
        select columns.
    """
    strip_zeros_dict = {"0001": "001",
                        "0002": "002",
                        "0003": "003",
                        "0203": "203",
                        "0205": "205",
                        "0207": "207",
                        "0209": "209",
                        "0211": "211",
                        "0213": "213",
                        "0215": "215",
                        "0217": "217",
                        "0219": "219",
                        "0223": "223",
                        "0225": "225",
                        "0227": "227",
                        "0229": "229",
                        "0302": "302",
                        "0304": "304",
                        "0306": "306",
                        "0308": "308",
                        "0310": "310",
                        "0312": "312",
                        "0314": "314",
                        "0316": "316",
                        "0318": "318",
                        "0319": "319",
                        "0320": "320",
                        "0322": "322",
                        "0324": "324",
                        "0326": "326",
                        "0327": "327",
                        "0328": "328",
                        "0330": "330",
                        "0331": "331",
                        "0332": "332",
                        "0333": "333",
                        "0334": "334",
                        "0335": "335",
                        "0336": "336",
                        "0337": "337",
                        "0338": "338",
                        "0339": "339",
                        "0340": "340",
                        "0341": "341",
                        "0342": "342",
                        "0343": "343",
                        "0344": "344",
                        "0345": "345",
                        "0346": "346",
                        "0603": "603",
                        "0703": "703",
                        "0704": "704",
                        "0705": "705",
                        "0706": "706",
                        "0901": "901",
                        "0903": "903",
                        "0905": "905",
                        "0907": "907",
                        "0909": "909"}

    df.rename(columns=strip_zeros_dict, inplace=True)

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

    df["226"] = None
    df["228"] = None
    df["237"] = None

    return df


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
                              'q0001',
                              'q0002',
                              'q0003',
                              'q0205',
                              'q0209',
                              'q0211',
                              'q0213',
                              'q0215',
                              'q0217',
                              'q0219',
                              'q0223',
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
                              'q0603',
                              'q0703',
                              'q0704',
                              'q0705',
                              'q0706',
                              'q0901',
                              'q0903',
                              'q0905',
                              'q0907',
                              'q0909']

    columns_to_rename_dict = {'IDBRPeriod': 'period',
                              'FormType': 'formtype',
                              'RUReference': 'reference',
                              'FormStatus': 'map cora status to column "status"',
                              'Employees': 'emp_total',
                              'Year': 'period_year',
                              'Instance': 'instance',
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
                              'q0226': '205',  # This is a duplicate of q0224?
                              'q0228': '206',
                              'q0230': '605',
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
                              'q0701': '708',
                              'q0702': '712',
                              'q0902': '302',
                              'q0904': '303',
                              'q0906': '304',
                              'q0908': '305'}

    # Rename wanted columns
    df = df.rename(columns=columns_to_rename_dict)

    # Remove unwanted columns
    df = df.drop(columns=columns_to_remove_list)

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

    # Create the 200 column
    df = create_200(df)

    # Create the 201 columns
    df = create_201(df)

    # Prepare the backdata for MoR imputation
    df = prep_2021_backdata(df)

    # Run the apportionment on the PNP backdata
    df = run_apportionment(df)

    # strip leading 0's from select columnns
    df = remove_leading_zeros(df)

    # add missing columns manually
    df = add_missing_columns(df)

    return df


def main(input_file, output_file):
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
    df = pd.read_csv(os.path.join(rootpath, input_file))

    # Clean the DataFrame
    pnp_backdata_df = create_pnp_backdata(df)

    # Save the cleaned DataFrame to the output CSV file
    pnp_backdata_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean PNP backdata.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to save the cleaned CSV file.")
    args = parser.parse_args()

    main(args.input_file, args.output_file)
