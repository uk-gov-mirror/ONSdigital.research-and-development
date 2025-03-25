"""Tests for National Accounts output."""

# Local Standard Library Imports
import pytest

# Third Party Imports
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

# Local Imports
from src.outputs.NA_output import (
    divide_by_1000,
    output_na
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

class TestOutputNa(object):
    """Tests for output_na."""

    def create_config(self) -> dict:
        """Create a test config."""
        config = {
        "outputs_paths": {
            "outputs_master": "dummy_output_path"
        },
        "output_schemas": {
                "national_accounts_schema": "config/output_schemas/national_accounts_schema.toml"
        },
        "consistency_checks": {
            "2xx_totals": {
                "imputation": ['200', '202', '204', '210'],
                "emp_defence": []
            }
        }
    }
        return config

    def input_data(self):
        """Input data for output_na tests."""
        columns =["ref", "200", "202", "204", "210"]
        data = ([1001, "C", 10700, 20000, 8000],
                [1001, "D", 300, 1500, 500],
                [1002, "C", 7800, 24000, 10000],
                [1002, "D", 1200, 2800, 200],
                [1003, "C", 4000, 38000, 2000],
                [1003, "D", 500, 4000, 100])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self):
        """Expected output data for output_na tests."""
        columns = ["RUReference", "Salaries and Wages- civil", "Salaries and Wages- defence", "Total non-capex- civil", "Total non-capex- defence", "Total Capex- civil", "Total Capex- defence"]
        data = ([1001, 11, 0, 20, 2, 8, 0],
                [1002, 8, 1, 24, 3, 10, 0],
                [1003, 4, 1, 38, 0, 2, 0])


        df = pd.DataFrame(data=data, columns=columns)
        return df


    def test_output_na(self):
        """General tests for output_na."""
        config = self.create_config()
        input_data = self.input_data()
        expected_output = self.expected_output()

        result_df = output_na(input_data, config, dummy_write_csv)

        assert_frame_equal(
            result_df.reset_index(drop=True),
            expected_output.reset_index(drop=True),
            check_dtype=False)
