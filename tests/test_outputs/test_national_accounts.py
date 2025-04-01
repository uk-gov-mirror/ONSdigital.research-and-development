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
    remove_C_D,
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


class TestRemoveC_D(object):
    """Test for remove_C_D from specific columns."""

    def input_data (self):
        """Create input data."""
        columns = ["ref_C", "211_C", "211_D", "601_C", "602_D"]
        data = ([1001, 5000, 0, 60, 100],
                [1002, 3000, 50, 0, 50],
                [1003, 1000, 0, 100, 50],
                [1004, pd.NA, 2000, 100, 100],
                [1005, 0, 3000, 200, 70],
                [1006, 0, 1500, 100, 30])

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self):
        """Create expected output data."""
        columns = ["ref", "211_C", "211_D", "601", "602"]
        data = ([1001, 5000, 0, 60, 100],
                [1002, 3000, 50, 0, 50],
                [1003, 1000, 0, 100, 50],
                [1004, pd.NA, 2000, 100, 100],
                [1005, 0, 3000, 200, 70],
                [1006, 0, 1500, 100, 30])

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
