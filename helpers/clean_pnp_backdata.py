import numpy as np
import pandas as pd
import argparse
import toml


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


def clean_pnp_backdata(df):
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
                              'q0510',
                              'q0512',
                              'q0514',
                              'q0516',
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
                              'Employees': 'employees',
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
                              'q0226': '205',
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
                              'q0511': '407',
                              'q0513': '409',
                              'q0515': '411',
                              'q0601': '601',
                              'q0602': '602',
                              'q0701': '708',
                              'q0702': '712',
                              'q0902': '302',
                              'q0904': '303',
                              'q0906': '304',
                              'q0908': '305'}

    # Remove unwanted columns
    df = df.drop(columns=columns_to_remove_list)

    # Rename wanted columns
    df = df.rename(columns=columns_to_rename_dict)

    # convert column datatypes
    df = convert_column_datatypes(df)

    # Populate the statusencoded column
    df = get_status_encoded(df)

    # Filter the DataFrame for rows where statusencoded is 210 or 211
    df = df[df['statusencoded'].isin([210, 211])]

    return df


def main(input_file, output_file):
    """ Main function to clean the PNP backdata.

    Read in csv file as a dataframe, clean with clean_pnp_backdata function,
    and save dataframe as a csv file.

    Example cmd executiion: python clean_pnp_backdata.py input.csv output.csv

    Args:
        input_file (str): The path to the input CSV file.
        output_file (str): The path to save the cleaned CSV file.
    Return:
        None
    """
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Clean the DataFrame
    cleaned_df = clean_pnp_backdata(df)

    # Save the cleaned DataFrame to the output CSV file
    cleaned_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean PNP backdata.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to save the cleaned CSV file.")
    args = parser.parse_args()

    main(args.input_file, args.output_file)
