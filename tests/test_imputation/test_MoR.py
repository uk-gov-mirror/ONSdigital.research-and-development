"""Tests for MoR.py."""

# Local Imports
import os

# Third Party Imports
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

# Local Imports
from src.imputation.MoR import run_mor, is_lf_only, filter_for_links
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

class TestRunMoRLongForm(object):
    """Tests for run_mor."""

    @pytest.fixture(scope="function")
    def input_lf_mor_df(self) -> pd.DataFrame:
        """A dummy dataframe used for testing MoR imputation."""
        fpath = os.path.join("tests/data/imputation/lf_mor_input_anon.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        df["referencepostcode"] = pd.NA
        df = create_imp_class_col(df, ["200", "201"])
        return df

    @pytest.fixture(scope="function")
    def dummy_lf_mor_backdata(self) -> pd.DataFrame:
        """Dummy backdata used for testing MoR imputation."""
        fpath = os.path.join("tests/data/imputation/lf_mor_backdata_anon.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df

    @pytest.fixture(scope="function")
    def expected_lf_mor_output(self) -> pd.DataFrame:
        """The expected output from run_mor."""
        fpath = os.path.join("tests/data/imputation/lf_mor_expected.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        # order by reference and then instance
        df = df.sort_values(["reference", "instance"]).reset_index(drop=True)
        return df

    def test_run_mor_long_form(
        self,
        input_lf_mor_df,
        dummy_lf_mor_backdata,
        expected_lf_mor_output,
        imputation_config
    ):
        """General tests for run_mor."""
        impute_vars = get_imputation_cols(imputation_config)
        result_df, qa = run_mor(
            df=input_lf_mor_df,
            backdata=dummy_lf_mor_backdata,
            config=imputation_config
        )
        # select only the required columns for the result and the expected output
        wanted_cols = ["reference", "instance", "imp_class", "211_link", "211_imputed", "emp_researcher_imputed", "emp_technician_imputed", "212_imputed", "214_imputed", "216_imputed"]

        result_filter = (result_df.instance != 0) & (result_df.formtype == "0001") & (result_df["200"].notnull()) & (result_df.imp_marker.isin(["CF","MoR"]))
        result_df = result_df.loc[result_filter][wanted_cols].round(4)
        result_df["211_link"] = result_df["211_link"].fillna(1)
        result_df = result_df.sort_values(["reference", "instance"]).reset_index(drop=True)

        # round the expected output to 4 decimal places
        # Apply rounding only to the floating-point columns in the expected output
        float_cols = expected_lf_mor_output.select_dtypes(include='float').columns
        expected_lf_mor_output[float_cols] = expected_lf_mor_output[float_cols].round(4)
        expected_lf_mor_output = expected_lf_mor_output[wanted_cols]

        assert_frame_equal(result_df, expected_lf_mor_output, check_dtype=False, check_exact=False), (
            "run_mor() not imputing data as expected."
        )


class TestRunMoRShortForm(object):
    """Tests for run_mor in the short form case."""

    @pytest.fixture(scope="function")
    def input_sf_mor_df(self) -> pd.DataFrame:
        """A dummy dataframe used for testing MoR imputation."""
        fpath = os.path.join("tests/data/imputation/sf_mor_input_anon.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        df["referencepostcode"] = pd.NA
        df = create_imp_class_col(df, ["200", "201"])
        return df

    @pytest.fixture(scope="function")
    def sf_mor_backdata(self) -> pd.DataFrame:
        """Dummy backdata used for testing MoR imputation."""
        fpath = os.path.join("tests/data/imputation/sf_mor_backdata_anon.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df

    @pytest.fixture(scope="function")
    def expected_sf_mor_output(self) -> pd.DataFrame:
        """The expected output from run_mor."""
        fpath = os.path.join("tests/data/imputation/sf_mor_expected.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        # order by reference and then instance
        df = df.sort_values(["reference", "instance"]).reset_index(drop=True)
        return df

    def test_run_mor_short_form(
        self,
        input_sf_mor_df,
        sf_mor_backdata,
        expected_sf_mor_output,
        imputation_config
        ):
        """General tests for run_mor."""
        impute_vars = get_imputation_cols(imputation_config)
        result_df, qa = run_mor(
            df=input_sf_mor_df,
            backdata=sf_mor_backdata,
            config=imputation_config
        )
        # select only the required columns for the result and the expected output
        wanted_cols = ["reference", "instance", "imp_class", "211_link", "211_imputed","212_imputed", "214_imputed", "216_imputed"]

        result_filter = (result_df.instance != 0) & (result_df.formtype == "0006") & (result_df["200"].notnull()) & (result_df.imp_marker.isin(["CF","MoR"]))
        result_df = result_df.loc[result_filter][wanted_cols].round(4)
        result_df = result_df.sort_values(["reference", "instance"]).reset_index(drop=True)

        # round the expected output to 4 decimal places
        # Apply rounding only to the floating-point columns in the expected output
        float_cols = expected_sf_mor_output.select_dtypes(include='float').columns
        expected_sf_mor_output[float_cols] = expected_sf_mor_output[float_cols].round(4)
        expected_sf_mor_output = expected_sf_mor_output[wanted_cols]

        assert_frame_equal(result_df, expected_sf_mor_output, check_dtype=False, check_exact=False), (
            "run_mor() not imputing data as expected."
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
