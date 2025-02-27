"""Tests for MoR.py."""

# Local Imports
import os

# Third Party Imports
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np

# Local Imports
from src.imputation.MoR import run_mor, is_lf_only, filter_for_links, mor_preprocessing, group_calc_link
from src.imputation.imputation_helpers import get_imputation_cols, create_imp_class_col

# pytestmark = pytest.mark.runwip

class TestIsLfOnly(object):
    """Tests for is_lf_only."""
    def test_pnp_survey(self):
        config = {
            "survey": {
                "survey_type": "PNP",
                "survey_year": 2021
            }
        }
        assert is_lf_only(config) == True

    def test_berd_2021_backdata(self):
        config = {
            "survey": {
                "survey_type": "BERD",
                "survey_year": 2022
            }
        }
        assert is_lf_only(config) == True

    def test_neither_condition(self):
        config = {
            "survey": {
                "survey_type": "BERD",
                "survey_year": 2021
            }
        }
        assert is_lf_only(config) == False


class TestMoRPreprocessing(object):
    """Tests for MoR preprocessing function."""

    def create_input_df(self) -> pd.DataFrame:
        input_columns = [
            "reference",
            "instance",
            "selectiontype",
            "formtype",
            "601",
            "status",
            "imp_marker"
        ]
        data = [
            [1001, 1, "C", "6.0", "CF14 9XY", "Clear", "R"],
            [1001, 2, "P", "6", "CF14 9XY", "Clear", "R"],
            [1002, 1, "C", "0006", np.nan, "Form sent out", "CF"],
            [1003, 1, "C", "0001", "NP10 2RT", "Clear", "MoR"],
            [1004, 1, "C", "6", np.nan, "Form sent out", "MoR"],
            [1004, 2, "P", "6.0", np.nan, "Form sent out", "MoR"],
            [1005, 0, "C", "0001", "SW5 2DW", "Check needed", "MoR"],
            [1005, 1, "P", "01.0", "SW5 2DW", "Check needed", "MoR"],
            [1006, 0, np.nan, "6", "CF48 9DU", "Clear - overidden", np.nan],
            [1006, 1, "C", "6.0", "CF48 9DU", "Clear", "R"],
            [1006, 2, "P", "6.0", "CF48 9DU", "Clear", "R"],
        ]
        input_df = pd.DataFrame(data=data, columns=input_columns)
        return input_df

    def config_dict(self) -> dict:
        """A dummy config for testing."""
        config = {
            "survey": {
                "survey_type": "BERD",
                "survey_year": 2023
            }
        }
        return config

    def create_backdata(self) -> pd.DataFrame:
        """A dummy backdata for testing."""
        backdata_columns = [
            "reference",
            "instance",
            "selectiontype",
            "formtype",
            "601",
            "status",
            "imp_marker"
        ]

        data = [
            [1007, 1, "C", "0006", "SW52DW", "Clear", "R"],
            [1007, 2, "P", "6", "SW52DW", "Clear", "R"],
            [1008, 1, "C", "0006", np.nan, "Form sent out", np.nan],
            [1008, 2, "P", "1.0", "NP10 2RT", "Clear", np.nan],
            [1009, 1, "C", "6.0", np.nan, "Form sent out", "no_imputation"],
            [1010, 0, np.nan, "0006", "NP10 6RT", "Form sent out", "no_imputation"],
            [1010, 1, "C", "1", np.nan, "Check needed", np.nan],
            [1010, 2, "P", "0001", np.nan, "Check needed", np.nan],
            [1011, 1, "C", "6", np.nan, "Clear - overidden", "R"],
            [1012, 0, np.nan, "0006", "CF489DU", "Clear", np.nan],
            [1012, 1, "C", "0006", "CF489DU", "Clear", np.nan],
        ]

        backdata_df = pd.DataFrame(data=data, columns=backdata_columns)
        return backdata_df

    def expected_to_impute_df(self) -> pd.DataFrame:
        """The expected to_impute_df output from the preprocessing function."""
        expected_columns = [
            "reference",
            "instance",
            "selectiontype",
            "formtype",
            "601",
            "status",
            "imp_marker",
        ]

        data = [
            [1002, 1, "C", "0006", np.nan, "Form sent out", "CF"],
            [1004, 1, "C", "0006", np.nan, "Form sent out", "MoR"],
            [1005, 0, "C", "0001", "SW5 2DW", "Check needed", "MoR"]
        ]

        expected_to_impute_df = pd.DataFrame(data=data, columns=expected_columns)
        return expected_to_impute_df

    def expected_remainder_df(self) -> pd.DataFrame:
        """The expected remainder_df output from the preprocessing function."""
        expected_columns = [
            "reference",
            "instance",
            "selectiontype",
            "formtype",
            "601",
            "status",
            "imp_marker"
            ]

        data = [
            [1001, 1, "C", "0006", "CF14 9XY", "Clear", "R"],
            [1001, 2, "P", "0006", "CF14 9XY", "Clear", "R"],
            [1003, 1, "C", "0001", "NP10 2RT", "Clear", "MoR"],
            [1004, 2, "P", "0006", np.nan, "Form sent out", "MoR"],
            [1005, 1, "P", np.nan, "SW5 2DW", "Check needed", "MoR"],
            [1006, 0, np.nan, "0006", "CF48 9DU", "Clear - overidden", np.nan],
            [1006, 1, "C", "0006", "CF48 9DU", "Clear", "R"],
            [1006, 2, "P", "0006", "CF48 9DU", "Clear", "R"]
        ]

        expected_remainder_df = pd.DataFrame(data=data, columns=expected_columns)
        return expected_remainder_df

    def expected_backdata_df(self) -> pd.DataFrame:
        """The expected backdata_df output from the preprocessing function."""
        expected_columns = [
            "reference",
            "instance",
            "selectiontype",
            "formtype",
            "601",
            "status",
            "imp_marker",
            ]

        data = [
            [1007, 1, "C", "0006", "SW5  2DW", "Clear", "R"],
            [1007, 2, "P", "0006", "SW5  2DW", "Clear", "R"],
            [1011, 1, "C", "0006", np.nan, "Clear - overidden", "R"],
        ]

        expected_backdata_df = pd.DataFrame(data=data, columns=expected_columns)
        return expected_backdata_df

    def test_mor_preprocessing(self):
        """Tests for the MoR preprocessing function."""
        input_df = self.create_input_df()
        config = self.config_dict()
        backdata_df = self.create_backdata()
        to_impute_df, remainder_df, backdata_df = mor_preprocessing(
            input_df, backdata_df, config
        )

        expected_to_impute_df = self.expected_to_impute_df()
        expected_remainder_df = self.expected_remainder_df()
        expected_backdata_df = self.expected_backdata_df()

        # Reset index and replace missing values for comparison
        df_list = [
            to_impute_df, expected_to_impute_df, remainder_df,
            expected_remainder_df, backdata_df, expected_backdata_df
        ]
        for df in df_list:
            df.reset_index(drop=True, inplace=True)
            df.replace({None: np.nan}, inplace=True)

        for result_df, expected_df, name in [
            (to_impute_df, expected_to_impute_df, "to_impute_df"),
            (remainder_df, expected_remainder_df, "remainder_df"),
            (backdata_df, expected_backdata_df, "backdata_df")
        ]:
            assert_frame_equal(
                result_df, expected_df, check_dtype=False, check_exact=False
            ), (
                f"{name} not as expected."
            )

class TestFilterForLinks(object):
    """Tests to check the function is fitering correctly"""

    def create_input_df(self) -> pd.DataFrame:
        """A dummy dataframe used for testing filter_for_links function."""
        columns = ("reference", "instance", "imp_marker", "imp_class", "selectiontype")
        data = [
            [1001, 0, "R", "nan_A", "P"],  # instance 0 and "nan"
            [1001, 1, "R", "C_A", "P"],
            [1002, 1, "R", "D_A", "P"],
            [1003, 1, "TMI", "C_B", "C"],  # not "R"
            [1004, 1, "R", "C_C", "C"],
            [1005, 1, "MoR", "nan_D", "C"],  # "nan" imp_class
            [1005, 2, "MoR", "C_D", "C"],  # not "R"

        ]
        input_df = pd.DataFrame(data, columns=columns)
        return input_df

    def expected_output_false(self) -> pd.DataFrame:
        """Expected dataframe if 'is_current' is set to false.
       Returns filtered data of both previous and current period data"""
        columns = ("reference", "instance", "imp_marker", "imp_class", "selectiontype")
        data = [
            [1001, 1, "R", "C_A", "P"],
            [1002, 1, "R", "D_A", "P"],
            [1004, 1, "R", "C_C", "C"],

        ]
        exp_df_false = pd.DataFrame(data, columns=columns)
        return exp_df_false

    def expected_output_true(self) -> pd.DataFrame:
        """ Expected dataframe if 'is_current' is set to true.
        Only returns filtered data of current period data"""
        columns = ("reference", "instance", "imp_marker", "imp_class", "selectiontype")
        data = [[1004, 1, "R", "C_C", "C"]]
        exp_df_true = pd.DataFrame(data, columns=columns)
        return exp_df_true

    def test_filter_for_links(self):
        # Create the input and expected output dataframes
        input_df = self.create_input_df()
        exp_df_false = self.expected_output_false()
        exp_df_true = self.expected_output_true()

        # Run the function
        result_false = filter_for_links(input_df, is_current=False)
        result_true = filter_for_links(input_df, is_current=True)

        # Reset index for comparison
        df_list = [exp_df_false, exp_df_true, result_false, result_true]

        for df in df_list:
            df.reset_index(drop=True, inplace=True)

        # Compare the results
        assert_frame_equal(result_false, exp_df_false, check_dtype=False, check_exact=False), (
            "filter_for_links() not filtering data as expected."
        )
        assert_frame_equal(result_true, exp_df_true, check_dtype=False, check_exact=False), (
            "filter_for_links() not filtering data as expected."
        )

class TestGroupCalcLink(object):
    """Tests for the group_calc_links function."""
    def create_input_df(self) -> pd.DataFrame:
        """A dummy dataframe used for testing group_calc_links function."""
        columns = [
            "reference",
            "imp_class",
            "211",
            "emp_researcher",
            "211_gr",
            "emp_researcher_gr",
        ]
        data = [
            [1031, "C_AA", 20, 10, np.nan, 1.0],
            [1031, "C_AA", 10, 0, 1.0, np.nan],
            [1045, "C_AA", 80500, 20, 8.05, np.nan],
            [1045, "C_AA", 36000, 30, 3.6, 3.0],
            [1047, "C_AA", 400, 20, 1.0, 1.0],
            [1047, "C_AA", 200, 10, 1.0, 1.0]]

        input_df = pd.DataFrame(data=data, columns=columns)
        return input_df

    def dummy_config(self) -> dict:
        """A dummy config for testing."""
        config = {"imputation": {
            "mor_threshold": 3,
            "trim_threshold": 10,
            "lower_trim_perc": 15,
            "upper_trim_perc": 15,
            "target_vars": ["211","emp_researcher"]},
        }
        return config

    def expected_output_df(self) -> pd.DataFrame:
        """Expected dataframe after running group_calc_links function."""
        columns = [
            "reference",
            "imp_class",
            "211",
            "emp_researcher",
            "211_gr",
            "emp_researcher_gr",
            "211_gr_trim",
            "211_group_size",
            "211_link",
            "emp_researcher_gr_trim",
            "emp_researcher_group_size",
            "emp_researcher_link",
        ]
        data = [
            [1047, "C_AA", 400, 20, 1.0, 1.0, False, 5, 2.93, False, 4, 1.5],
            [1047, "C_AA", 200, 10, 1.0, 1.0, False, 5, 2.93, False, 4, 1.5],
            [1031, "C_AA", 20, 10, np.nan, 1.0, False, 5, 2.93, False, 4, 1.5],
            [1045, "C_AA", 36000, 30, 3.6, 3.0, False, 5, 2.93, False, 4, 1.5],
            [1031, "C_AA", 10, 0, 1.0, np.nan, False, 5, 2.93, False, 4, 1.5],
            [1045, "C_AA", 80500, 20, 8.05, np.nan, False, 5, 2.93, False, 4, 1.5],
            ]

        expected_output_df = pd.DataFrame(data=data, columns=columns)
        return expected_output_df


    def test_group_calc_link(self):
        # Create the input and expected output dataframes
        input_df = self.create_input_df()
        config = self.dummy_config()
        expected_output_df = self.expected_output_df()
        target_vars = config["imputation"]["target_vars"]

        # Run the function
        result_df = group_calc_link(input_df, target_vars, config)

        # Reset index for comparison
        df_list = [expected_output_df, result_df]

        for df in df_list:
            df.reset_index(drop=True, inplace=True)

        # Compare the results
        assert_frame_equal(result_df, expected_output_df, check_dtype=False, check_exact=False), (
            "group_calc_links() not calculating links as expected."
        )
