"""Tests for National Accounts output."""

# Local Standard Library Imports
import pytest

# Third Party Imports
import pandas as pd
import numpy as np
from unittest.mock import patch
from pandas.testing import assert_frame_equal

# Local Imports
from src.outputs.NA_output import (
    divide_by_1000,
    expenditure_by_region,
    remove_C_D
    output_na,
)

class TestDivideBy1000(object):
    """Tests for divide_by_1000."""

    def create_config(self) -> dict:
        """Create a test config."""
        config = {
            "consistency_checks": {
                "2xx_totals": {
                    "imputation": ['212', '250', '247'],
                    "emp_defence": []
                }
            }
        }
        return config

    def input_data(self):
        """Input data for divide_by_1000 tests."""
        columns = ["212", "250", "247"]
        data = [[1, 500, 1000], [2, 1000, 2000], [3, 2000, 3000]]
        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self):
        """Expected output data for divide_by_1000 tests."""
        columns = ["212", "250", "247"]
        data = [[0, 0, 1], [0, 1, 2], [0, 2, 3]]
        df = pd.DataFrame(data=data, columns=columns)
        return df

    def test_divide_by_1000(self):
        """General tests for divide_by_1000."""
        config = self.create_config()
        input_data = self.input_data()
        expected_output = self.expected_output()

        result_df = divide_by_1000(input_data, config)

        assert_frame_equal(
            result_df.reset_index(drop=True),
            expected_output.reset_index(drop=True),
            check_dtype=False
        )

def dummy_write_csv(file_path, df):
    """Dummy write_csv function for testing."""
    print(f"Dummy write_csv called with file_path: {file_path}")

class TestExpentitureByRegion(object):
    """ Test to check the generation and calculation of expenditure by region col."""

    def input_data(self):
        """Create input data"""
        columns = ["ref", "211_C", "211_D", "602"]
        data = ([1001, 5000, 0, 60],
                [1001, 2000, 0, 40],
                [1002, pd.NA, 3000, 50],
                [1002, pd.NA, 3000, 50],
                [1003, 1000, 0, 100],
                [1004, pd.NA, 2000, 100])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self):
        """Create expected output data"""
        columns = ["ref", "211_C", "211_D", "602", "Expenditure by Region"]
        data = ([1001, 5000, pd.NA, 60, 3000.0],
                [1001, 2000, 0, 40, 800.0],
                [1002, 0, 3000, 50, 1500.0],
                [1002, pd.NA, 3000, 50, 1500.0],
                [1003, 1000, 0, 100, 1000.0],
                [1004, pd.NA, 2000, 100, 2000.0])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def test_expenditure_by_region(self):
        """Test for expenditure_by_region."""
        input_data = self.input_data()
        expected_output = self.expected_output()

        result_df = expenditure_by_region(input_data)

        assert_frame_equal(
            result_df.reset_index(drop=True),
            expected_output.reset_index(drop=True),
            check_dtype=False
        )

class TestRemoveC_D(object):
    """Test for remove_C_D from specific columns."""

    def input_data (self):
        """Create input data."""
        columns = ["ref_C", "211_C", "211_D", "601_C", "602_D"]
        data = ([1001, 5000, 0, 60],
                [1002, 3000, 50],
                [1003, 1000, 0, 100],
                [1004, pd.NA, 2000, 100],
                [1005, 0, 3000, 200],
                [1006, 0, 1500, 100])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self):
        """Create expected output data."""
        columns = ["ref", "211_C", "211_D", "601", "602"]
        data = ([1001, 5000, 0, 60],
                [1002, 3000, 50],
                [1003, 1000, 0, 100],
                [1004, pd.NA, 2000, 100],
                [1005, 0, 3000, 200],
                [1006, 0, 1500, 100])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def test_remove_C_D(self):
        """Test for remove_C_D."""
        input_data = self.input_data()
        expected_output = self.expected_output()

        result_df = remove_C_D(input_data)

        assert_frame_equal(
            result_df.reset_index(drop=True),
            expected_output.reset_index(drop=True),
            check_dtype=False
        )
class TestOutputNa(object):
    """Tests for output_na."""

    def create_config(self) -> dict:
        """Create a test config."""
        config = {
            "survey": {
                "survey_year": "2023",
                "survey_type": "PNP"},
            "filename_items": {
                "run_id": "dummy_run_id",
                "tdate": "dummy_tdate"},
            "outputs_paths": {
                "outputs_master": "dummy_output_path"},
            "schema_paths": {
                "national_accounts_schema": "dummy_schema"},
            "consistency_checks": {
                "2xx_totals": {
                "imputation": ['202', '204', '210', "211"],
            }
        }
    }
        return config

    def input_data(self):
        """Input data for output_na tests."""
        columns =["ref", "200", "202", "204", "210", "211", "602"]
        data = ([1001, "C", 10700, 20000, 8000, 7000, 70],
                [1001, "D", 300, 1500, 500, 3000, 30]
                [1002, "C", 7800, 24000, 10000, 1500, 50],
                [1002, "D", 1200, 2800, 200, 3000, 50],
                [1003, "C", 4000, 38000, 2000, 1000, 100],
                [1004, "D", 500, 4000, 100, 2000, 100])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self):
        """Expected output data for output_na tests."""
        columns = ["RUReference", "Salaries and Wages- civil", "Salaries and Wages- defence", "Total non-capex- civil", "Total non-capex- defence", "Total Capex- civil", "Total Capex- defence"]
        data = (["RUReference", "q0214", "q0215", "q0212", "q0213", "q0202", "q0203"],
                [1001, 11, np.NaN, 20, np.NaN, 8, np.NaN],
                [1002, 8, np.NaN, 24, np.NaN, 10, np.NaN],
                [1003, 4, np.NaN, 38, np.NaN, 2, np.NaN],
                [1001, np.NaN, 0, np.NaN, 2, np.NaN, 0],
                [1002, np.NaN, 1, np.NaN, 3, np.NaN, 0],
                [1003, np.NaN, 0, np.NaN, 4, np.NaN, 0])


        df = pd.DataFrame(data=data, columns=columns)
        return df

    # @patch("src.outputs.NA_output.load_schema")
    # def test_output_na(self, mock_load_schema):
    #     """General tests for output_na."""
    #     # Define the dummy schema
    #     dummy_schema = {
    #         "RUReference": {"old_name": "ref", "name": "RUReference", "R_and_D_Type": "ref"},
    #         "q0214": {"old_name": "202", "name": "Salaries and Wages- civil", "R_and_D_Type": "202_C"},
    #         "q0215": {"old_name": "202", "name": "Salaries and Wages- defence", "R_and_D_Type": "202_D"},
    #         "q0212": {"old_name": "204","name": "Total non-capex- civil", "R_and_D_Type": "204_C"},
    #         "q0213": {"old_name": "204","name": "Total non-capex- defence", "R_and_D_Type": "204_D"},
    #         "q0202": {"old_name": "210","name": "Total Capex- civil", "R_and_D_Type": "210_C"},
    #         "q0203": {"old_name": "210","name": "Total Capex- defence", "R_and_D_Type": "210_D"}
    #     }

    #     # Mock the load_schema function to return the dummy schema
    #     mock_load_schema.return_value = dummy_schema

    #     # Run the test
    #     config = self.create_config()
    #     input_data = self.input_data()
    #     expected_output = self.expected_output()

    #     result_df = output_na(input_data, config, dummy_write_csv)

    #     # Assert the result matches the expected output
    #     assert_frame_equal(
    #         result_df.reset_index(drop=True),
    #         expected_output.reset_index(drop=True),
    #         check_dtype=False
    #     )
