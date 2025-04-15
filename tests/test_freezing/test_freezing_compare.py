"""Tests for freezing_compare.py."""

import pandas as pd
from pandas.testing import assert_frame_equal
import logging
import numpy as np

from src.freezing.freezing_compare import get_amendments, get_additions_deletions
from src.freezing.freezing_compare import bring_together_split_cases

# create a test logger to pass to functions
test_logger = logging.getLogger(__name__)


class TestGetAmendments:
    """Tests for get_amendments()."""

    # Create test frozen df
    def create_test_frozen_df(self) -> pd.DataFrame:
        """Create a test frozen df."""
        input_cols = ["reference", "period", "instance", "202", "203", "200", "201", "601", "604", "status"]
        data = [
            ["A", 202412, 2.0, 1.0, 2.0, "A", "Yes", None, "Yes", "clear"],
            ["B", 202412, None, None, 1.0, "B", "Yes", "C", "Yes", "form sent out"],
            ["C", 202412, 0.0, 1.0, 2.0, "A", "Yes", "B", "Yes", "clear"],
            ["D", 202412, 1.0, 2.0, 3.0, "C", "Yes", "D", "Yes", "clear"],
            ["E", 202412, None, 4.0, 5.0, "E", "Yes", "F", "No", "form sent out"],
            ["R", 202412, None, 14.0, 14.0, "E", "Yes", "F", "No", "form sent out"],
            ["X", 202412, 8.0, 2.0, 2.0, "E", "Yes", "F", "Yes", "check needed"],
        ]
        input_frozen_df = pd.DataFrame(data=data, columns=input_cols)
        return input_frozen_df

    # Create test amendments df
    def create_test_amendments_df(self) -> pd.DataFrame:
        """Create a test amendments df."""
        input_cols = ["reference", "period", "instance", "202", "203", "200", "201", "601", "604", "status"]
        data = [
            ["A", 202412, 2.0, 1.0, 2.0, "A", "Yes", None, "Yes", "clear"], # No diffs
            ["B", 202412, None, None, 1.0, "A", "Yes", "B", "Yes", "form sent out"], # 200 diff "A"
            ["C", 202412, 0.0, 2.0, 2.0, "A", "Yes", "B", "No", "clear"], # 202 diff by 1, 604 to "No"
            ["D", 202412, 1.0, 2.0, 3.0, "E", "Yes", "D", "Yes", "clear"],  # 200 & 601 diff "E", "D"
            ["E", 202412, None, 10.0, 1.0, "E", "Yes", "F", "Yes", "form sent out"], # 202 & 203 by 6, -4, , 604 to "Yes"
            ["R", 202412, None, 6.0, 6.0, "E", "Yes", "F", "No", "form sent out"], # 202 & 203 by -8, -8
            ["X", 202412, 8.0, 2.0, 2.0, "E", "Yes", "F", "Yes", "clear"], # status changed to "clear"
        ]
        input_amendments_df = pd.DataFrame(data=data, columns=input_cols)
        return input_amendments_df

    # Create expected outcome df
    def create_test_expected_outcome_df(self) -> pd.DataFrame:
        """Create a test expected_outcome df."""
        input_cols = ["reference", "period", "instance", "202", "203", "200", "201", "601", "604", "status", "202_diff", "203_diff", "200_diff", "201_diff", "601_diff", "604_diff", "status_diff", "accept_changes", "frozen_data_file"]
        data = [
            ["A", 202412, 2.0, 1.0, 2.0, "A", "Yes", None, "Yes", "clear", 0.0, 0.0, None, None, None, None, None, False, "frozen_data_v123.csv"],
            ["B", 202412, None, None, 1.0, "A", "Yes", "B", "Yes", "form sent out", None, 0.0, "A", None,  "B", None, None, False, "frozen_data_v123.csv"],
            ["C", 202412, 0.0, 2.0, 2.0, "A", "Yes", "B", "No", "clear", 1.0, 0.0, None, None, None, "No", None, False, "frozen_data_v123.csv"],
            ["D", 202412, 1.0, 2.0, 3.0, "E", "Yes", "D", "Yes", "clear", 0.0, 0.0, "E", None, None, None, None, False, "frozen_data_v123.csv"],
            ["E", 202412, None, 10.0, 1.0, "E", "Yes", "F", "Yes", "form sent out", 6.0, -4.0, None, None, None, "Yes", None, False, "frozen_data_v123.csv"],
            ["R", 202412, None, 6.0, 6.0, "E", "Yes", "F", "No", "form sent out", -8.0, -8.0, None, None, None, None, None, False, "frozen_data_v123.csv"],
            ["X", 202412, 8.0, 2.0, 2.0, "E", "Yes", "F", "Yes", "clear", 0.0, 0.0, None, None, None, None, "clear", False, "frozen_data_v123.csv"],
        ]
        input_expected_outcome_df = pd.DataFrame(data=data, columns=input_cols)
        return input_expected_outcome_df

    # Create config for test
    def create_config(self) -> dict:
        """Create a test config."""
        config = {
            "consistency_checks": {
                "2xx_totals": {
                    "purchases_split": [],
                    "sal_oth_expend": [],
                    "research_expend": [],
                    "capex": [203],
                    "intram": [202],
                    "funding": [],
                    "ownership": [],
                    "equality": [],
                    "expenditure": []
                },
                "3xx_totals": {
                    "purchases": []
                },
                "4xx_totals": {
                    "emp_civil": [],
                    "emp_defence": []
                },
                "5xx_totals": {
                    "headcount_tot_m": [],
                    "headcount_tot_f": []
                },
                "6xx_totals": {
                    "business_tot_in_workplace": []
                },
                "7xx_a_totals": {
                    "sf_expend": [],
                    "sf_purchases": [],
                },
                "7xx_b_totals": {
                    "sf_fte": [],
                    "sf_headcount": []
                }
            },
            "freezing_paths": {
                "frozen_data_staged_path": "berd/freezing/frozen_data_v123.csv"
            }
        }

        return config

    def test_get_amendments(self):
        """Test for get_amendments()."""
        # Create test dataframes
        input_frozen_df = self.create_test_frozen_df()
        input_amendments_df = self.create_test_amendments_df()
        expected_outcome_df = self.create_test_expected_outcome_df()
        config = self.create_config()

        # Run the function
        result = get_amendments(
            input_frozen_df, input_amendments_df, config
        )

        # Check the output
        assert_frame_equal(
            expected_outcome_df, result
        )


class TestGetAdditions:
    """Tests for get_additions_deletions()."""

    # Create config for test
    def create_config(self) -> dict:
        """Create a test config."""
        config = {
            "survey": {
                "survey_type": "BERD"
            },
            "freezing_paths": {
                "frozen_data_staged_path": "berd/freezing/frozen_data_v123.csv"
            }
        }

        return config

    # Create test frozen df
    def create_test_frozen_df(self) -> pd.DataFrame:
        """Create a test frozen df"""
        input_cols = ["reference", "period", "instance", "other", "legalstatus"]
        data = [
            ["A", 202412, 2.0, 1.0, "4"],
            ["B", 202412, None, None, "4"],
            ["C", 202412, 0.0, 1.0, "4"],
            ["D", 202412, 1.0, 2.0, "4"],
            ["E", 202412, None, 4.0, "4"],
            ["E", 202412, 1.0, 5.0, "4"],
            ["E", 202412, 2.0, 6.0, "4"],
        ]
        input_frozen_df = pd.DataFrame(data=data, columns=input_cols)
        return input_frozen_df

    # Create test additions df
    def create_test_additions_df(self) -> pd.DataFrame:
        """Create a test additions df."""
        input_cols = ["reference", "period", "instance", "other", "legalstatus"]
        data = [
            ["A", 202412, 2.0, 1.0, "4"],
            ["B", 202412, None, None, "4"],
            ["C", 202412, 0.0, 1.0, "4"],
            ["D", 202412, 1.0, 2.0, "4"],
            ["E", 202412, None, None, "4"],
            ["F", 202412, 1.0, 4.0, "4"],
            ["G", 202412, None, 4.0, "4"],
            ["H", 202412, 1.0, None, "4"],
            ["X", 202412, 1.0, None, "7"],
            ["Y", 202412, 1.0, None, "7"],
            ["Z", 202412, 1.0, None, "7"],
        ]
        input_additions_df = pd.DataFrame(data=data, columns=input_cols)
        return input_additions_df

    def create_exp_additions_df(self) -> pd.DataFrame:
        """Create a test expected_outcome df for additions."""
        input_cols = ["reference", "period", "instance", "other", "legalstatus", "accept_changes", "frozen_data_file"]
        data = [
            ["F", 202412, 1.0, 4.0, "4", False, "frozen_data_v123.csv"],
            ["G", 202412, None, 4.0, "4", False, "frozen_data_v123.csv"],
            ["H", 202412, 1.0, None, "4", False, "frozen_data_v123.csv"]
        ]
        input_expected_outcome_df = pd.DataFrame(data=data, columns=input_cols)
        return input_expected_outcome_df

    def create_exp_deletions_df(self) -> pd.DataFrame:
        """Create a test expected_outcome df for deletions."""
        input_cols = ["reference", "period", "instance", "other", "legalstatus", "accept_changes", "frozen_data_file"]
        data = [
            ["E", 202412, 1.0, 5.0, "4", False, "frozen_data_v123.csv"],
            ["E", 202412, 2.0, 6.0, "4", False, "frozen_data_v123.csv"],
        ]
        input_expected_outcome_df = pd.DataFrame(data=data, columns=input_cols)
        return input_expected_outcome_df

    def test_get_additions_deletions(self):
        """Test for get_additions_deletions()."""
        # Create test dataframes
        input_frozen_df = self.create_test_frozen_df()
        input_additions_df = self.create_test_additions_df()
        expected_additions_df = self.create_exp_additions_df()
        expected_deletions_df = self.create_exp_deletions_df()

        config = self.create_config()

        result_additions, result_deletions = get_additions_deletions(
            input_frozen_df, input_additions_df, config
        )

        assert_frame_equal(
            expected_additions_df, result_additions.reset_index(drop=True)
        )

        assert_frame_equal(
            expected_deletions_df, result_deletions.reset_index(drop=True)
        )


class TestBringTogetherSplitCases:
    """Tests for bring_together_split_cases()."""

    def create_test_additions_df(self) -> pd.DataFrame:
        """Create a test additions df."""
        input_cols = ["reference", "period", "instance", "other"]
        data = [
            ["A", 202412, 2.0, 1.0],
            ["B", 202412, None, None],
            ["C", 202412, 0.0, 1.0],
            ["D", 202412, 1.0, 2.0],
            ["E", 202412, None, 4.0],
        ]
        input_additions_df = pd.DataFrame(data=data, columns=input_cols)
        return input_additions_df

    def create_test_amendments_df(self) -> pd.DataFrame:
        """Create a test amendments df."""
        input_cols = ["reference", "period", "instance", "other"]
        data = [
            ["C", 202412, 0.0, 1.0],
            ["D", 202412, 1.0, 2.0],
            ["F", 202412, None, 4.0],
        ]
        input_amendments_df = pd.DataFrame(data=data, columns=input_cols)
        return input_amendments_df

    def create_expected_additions_df(self) -> pd.DataFrame:
        """Create the expected additions df after split cases are handled."""
        input_cols = ["reference", "period", "instance", "other"]
        data = [
            ["A", 202412, 2.0, 1.0],
            ["B", 202412, None, None],
            ["E", 202412, None, 4.0],
        ]
        expected_additions_df = pd.DataFrame(data=data, columns=input_cols)
        return expected_additions_df

    def create_expected_amendments_df(self) -> pd.DataFrame:
        """Create the expected amendments df after split cases are handled."""
        input_cols = ["reference", "period", "instance", "other"]
        data = [
            ["C", 202412, 0.0, 1.0],
            ["D", 202412, 1.0, 2.0],
            ["F", 202412, None, 4.0],
            ["C", 202412, 0.0, 1.0],
            ["D", 202412, 1.0, 2.0],
        ]
        expected_amendments_df = pd.DataFrame(data=data, columns=input_cols)
        return expected_amendments_df

    def test_bring_together_split_cases(self):
        """Test for bring_together_split_cases()."""
        # Create test dataframes
        input_additions_df = self.create_test_additions_df()
        input_amendments_df = self.create_test_amendments_df()
        input_deletions_df = pd.DataFrame()  # Empty DataFrame for deletions
        expected_additions_df = self.create_expected_additions_df()
        expected_amendments_df = self.create_expected_amendments_df()
        expected_deletions_df = pd.DataFrame()

        # Run the function
        result_amendments_df, result_additions_df, result_deletions_df = bring_together_split_cases(
            input_amendments_df, input_additions_df, input_deletions_df
        )

        # Check the output
        assert_frame_equal(
            expected_additions_df, result_additions_df.reset_index(drop=True)
        )

        assert_frame_equal(
            expected_amendments_df, result_amendments_df.reset_index(drop=True)
        )
