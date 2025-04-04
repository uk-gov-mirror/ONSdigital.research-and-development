"""Tests for National Accounts output."""

# Local Standard Library Imports
import pytest

# Third Party Imports
import pandas as pd
import numpy as np
from unittest.mock import patch
from pandas.testing import assert_frame_equal

# Local Imports
from src.outputs.PNP_NA_output import (
    divide_by_1000,
    create_na_output
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
        data = [[1, 500, 1000],
                [2, 1000, 2000],
                [3, 2000, 3000]]
        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self):
        """Expected output data for divide_by_1000 tests."""
        columns = ["212", "250", "247"]
        data = [[0, 0, 1],
                [0, 1, 2],
                [0, 2, 3]]
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


class TestCreateNAOutput(object):
    """Tests for create_na_output."""

    def input_data(self) -> pd.DataFrame:
        """Create input data."""
        columns = ["RUReference", "Addr1", "q0202", "q0210"]
        data = [
            [1, "A", 100, 200],
            [2, "B", 300, 400],
            [3, "C", 500, 600]
        ]
        df = pd.DataFrame(data=data, columns=columns)
        return df

    def create_schema(self) -> dict:
        """Create a test schema."""
        schema = {
            "RUReference": {
                "name": "",
                "old_name": "reference",
                "Deduced_Data_Type": "Int64"
            },
            "Addr1": {
                "name": "",
                "old_name": "Addr1",
                "Deduced_Data_Type": "str"
            },
            "q0202": {
                "name": "Total Capex- civil",
                "old_name": "210",
                "Deduced_Data_Type": "float64"
            },
            "q0210": {
                "name": "Computer software- civil",
                "old_name": "211",
                "Deduced_Data_Type": "float64"
            }
        }
        return schema

    def expected_output(self) -> pd.DataFrame:
        """Create expected output."""
        columns = ["", "", "Total Capex- civil", "Computer software- civil"]
        data = [
            ["RUReference", "Addr1", "q0202", "q0210"],
                [1, "A", 100, 200],
                [2, "B", 300, 400],
                [3, "C", 500, 600]]
        df = pd.DataFrame(data=data, columns=columns)
        return df

    def test_create_na_output(self):
        """Test create_na_output."""
        input_data = self.input_data()
        schema = self.create_schema()
        expected_output = self.expected_output()

        result_df = create_na_output(input_data, schema)

        assert_frame_equal(
            result_df.reset_index(drop=True),
            expected_output.reset_index(drop=True),
            check_dtype=False
        )
