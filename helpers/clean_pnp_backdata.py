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
            print(f"Converting column {i} to {datatypes_dict[i]}")
            try:
                df[i] = df[i].astype(datatypes_dict[i])
            except:
                pass
        else:
            print(f"Column {i} not found in backdata_schema.toml")

    return df


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

    # convert column datatypes
    df = convert_column_datatypes(df)

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
    df_cleaned = clean_pnp_backdata(df)

    # Save the cleaned DataFrame to the output CSV file
    df_cleaned.to_csv(output_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean PNP backdata.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to save the cleaned CSV file.")
    args = parser.parse_args()

    main(args.input_file, args.output_file)
