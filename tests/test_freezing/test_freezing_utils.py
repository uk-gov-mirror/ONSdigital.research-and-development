"""Tests for freezing_utils.py."""

from datetime import datetime

import pandas as pd
import pytest

from src.freezing.freezing_utils import _add_last_frozen_column, validate_any_refinst_in_frozen

class TestAddLastFrozenColumn(object):
    """Tests for _add_last_frozen_column."""

    def create_expected_last_frozen(self, run_id: int) -> str:
        """Create an expected output from _add_last_frozen_column."""
        today = datetime.today().strftime("%y-%m-%d")
        expected_frozen = f"{today}_v{str(run_id)}"
        return expected_frozen

    def test__add_last_frozen_column(self):
        """General tests for _add_last_frozen_column."""
        # create dummy df with one row
        dummy_df = pd.DataFrame(
            {"test": [0]}
        )
        # add last_frozen_column
        last_frozen_df = _add_last_frozen_column(dummy_df, {"filename_items": {"run_id": "7000"}})
        exp_last_frozen = self.create_expected_last_frozen(7000)
        assert len(last_frozen_df.last_frozen.unique()) == 1, (
            "_add_last_frozen_column has added multiple different values."
        )
        assert last_frozen_df.last_frozen.unique()[0] == exp_last_frozen, (
            "_add_last_frozen_column not behaving as expected."
        )


def create_refinst_df(data: list) -> pd.DataFrame:
    """Create a dataframe with reference/instance columns.

    Args:
        data (list): The data for the dataframe

    Returns:
        pd.DataFrame: The created dataframe.
    """
    columns = ["reference", "instance", "value"]
    df = pd.DataFrame(columns=columns, data=data)
    return df


@pytest.fixture(scope="function")
def dummy_refinst_df() -> pd.DataFrame:
    """A dummy dataframe containing reference+instance."""
    data = [
        [0, 1, True],
        [0, 2, False],
        [1, 1, False],
        [2, 0, True],
        [3, 1, False],
    ]
    df = create_refinst_df(data)
    return df


class TestValidateAnyRefinstInFrozen(object):
    """Tests for validate_any_refinst_in_frozen."""

    def test_validate_any_refinst_in_frozen_true(self, dummy_refinst_df):
        """A test for validate_any_refinst_in_frozen returning 'True'."""
        df2 = create_refinst_df(data=[
                [0, 1, True], # present
                [5, 1, True], # not present
            ]
        )
        result = validate_any_refinst_in_frozen(dummy_refinst_df, df2)
        assert result == True, (
            "validate_any_refinst_in_frozen (true) not behaving as expected."
            )


    def test_validate_any_refinst_in_frozen_false(self, dummy_refinst_df):
        """A test for validate_any_refinst_in_frozen returning 'False'."""
        df2 = create_refinst_df(data=[
                [0, 3, True], # not present
                [5, 1, True], # not present
            ]
        )
        result = validate_any_refinst_in_frozen(dummy_refinst_df, df2)
        assert result == False, (
            "validate_any_refinst_in_frozen (False) not behaving as expected."
            )
