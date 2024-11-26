import pandas as pd
import numpy as np

# function to import a function from the tests of this repo, generate a
# test dataframe and write it to a csv
import os
import sys
sys.path.append(os.path.abspath(""))

from tests.test_site_apportionment.test_site_apportionment import (
    TestSplitSitesDf,
    TestDeduplicateCodeValues
)

def get_df_from_test(test_class, test_method):
    """Get the dataframe from the test method."""
    test_instance = test_class()
    test_method = getattr(test_instance, test_method)
    df = test_method()
    return df

def create_input_df():
    """Create an input dataframe for the beginning of the site apportionment module."""
    input_columns = [
        "reference",
        "instance",
        "period",
        "200",
        "201",
        "pg_numeric",
        "formtype",
        "211",
        "250",
        "601",
        "602",
        "status",
        "imp_marker",
        "postcodes_harmonised",
        "itl"
    ]

    data = [
        [1, 0, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [1, 1, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [1, 2, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [2, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP20 6YY", "cym"],
        [2, 1, "2020", "C", "A", 40, "0001", 100, "yes", "CB1 3NF", 60.0, "Clear", "R", "CB1 3NF", "cym"],
        [2, 2, "2020", "C", "A", 40, "0001", 100, "yes", "BA1 5DA", 40.0, "Clear", "R", "BA1 5DA", "cym"],
        [3, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Check needed", "TMI", "NP30 7ZZ", "cym"],
        [3, 1, "2020", "C", "A", 40, "0001", 100, "yes", "DE72 3AU", np.nan, "Check needed", "TMI", "DE72 3AU", "cym"],
        [3, 2, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "No mean found", "NP30 7ZZ", "cym"],
        [4, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "TMI", "CF10 BZZ", "cym"],
        [5, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "No mean found", "SA50 5BE", "cym"],
        [6, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        [6, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        [6, 2, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        [7, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym"],
        [7, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym"],
        [7, 2, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym"],
    ]

    input_df = pd.DataFrame(data=data, columns=input_columns)
    return input_df

# function to write the test data to a csv
def write_test_data_to_csv(filename):
    """Write the input data to a CSV file."""
    df = get_df_from_test(TestSplitSitesDf, "create_exp_remaining_output")

    file_path = csv_path + filename
    df.to_csv(file_path, index=False)
    print(f"Data written to {file_path}")



# Save the DataFrame to a CSV file
csv_path = "D:/coding_projects/randd_test_data/"

filename = "expected_remaining_output.csv"


if __name__ == "__main__":
    write_test_data_to_csv(filename)
