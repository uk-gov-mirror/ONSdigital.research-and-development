import pandas as pd
import numpy as np
import pytest

from src.outputs.PNP_NA_output import add_subtract_cols

class TestAddSubtractCols:
    """Tests for add_subtract_cols."""

    @pytest.fixture(scope="function")
    def create_output_df_schema(self):
        """Test schema for create_output_df."""
        schema = {
            "col_1": {"old_name": "old_col_1"},
            "col_2": {"old_name": "old_col_2", "add_col": "col_1"},  # col_2 = col_2 + col_1
            "col_3": {"old_name": "old_col_3", "subtract_col": "col_1"},  # col_3 = col_3 - col_1
            "col_4": {"old_name": "old_col_4", "add_col": "col_2"},  # col_4 = col_4 + col_2 which was already updated
        }
        return schema

    def input_df(self):
        """Input dataframe for add_subtract_cols tests."""
        cols = ["col_1", "col_2", "col_3", "col_4"]
        data = [
            [1, 2, np.nan, 4],
            [5, 6, 7, 8],
            [9, np.nan, 11, 12]
        ]

        return pd.DataFrame(data=data, columns=cols)

    def test_add_subtract_cols(self, create_output_df_schema):
        """Test the add_subtract_cols function."""
        df = self.input_df()
        output_df = add_subtract_cols(df, create_output_df_schema)

        # Expected results:
        expected_cols = ["col_1", "col_2", "col_3", "col_4"]
        expected_data = [
            [1, 3, -1, 7],
            [5, 11, 2, 19],
            [9, 9, 2, 21]
        ]
        expected_df = pd.DataFrame(data=expected_data, columns=expected_cols)

        pd.testing.assert_frame_equal(output_df, expected_df, check_dtype=False)


def test_add_subtract_cols_missing_keys():
    # Test that missing add_col or subtract_col keys do not raise errors
    df = pd.DataFrame({
        "A": [1, 2],
        "B": [3, 4]
    })
    output_schema = {
        "A": {},  # No add_col or subtract_col
        "B": {}
    }
    result = add_subtract_cols(df, output_schema)
    pd.testing.assert_frame_equal(result, df)
