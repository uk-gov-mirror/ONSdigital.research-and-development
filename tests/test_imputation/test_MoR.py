"""Tests for MoR.py."""

# Local Imports
import os

# Third Party Imports
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np

# Local Imports
from src.imputation.MoR import run_mor, is_lf_only, mor_preprocessing
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
            [1001, 2, "D", "6", "CF14 9XY", "Clear", "R"],
            [1002, 1, "C", "0006", np.nan, "Form sent out", "CF"],
            [1003, 1, "C", "0001", "NP10 2RT", "Clear", "MoR"],
            [1004, 1, "C", "6", np.nan, "Form sent out", "MoR"],
            [1004, 2, "D", "6.0", np.nan, "Form sent out", "MoR"],
            [1005, 0, "C", "0001", "SW5 2DW", "Check needed", "MoR"],
            [1005, 1, "D", "01.0", "SW5 2DW", "Check needed", "MoR"],
            [1006, 0, np.nan, "6", "CF48 9DU", "Clear - overidden", np.nan],
            [1006, 1, "C", "6.0", "CF48 9DU", "Clear", "R"],
            [1006, 2, "D", "6.0", "CF48 9DU", "Clear", "R"],
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
            [1007, 2, "D", "6", "SW52DW", "Clear", "R"],
            [1008, 1, "C", "0006", np.nan, "Form sent out", np.nan],
            [1008, 2, "D", "1.0", "NP10 2RT", "Clear", "MoR"],
            [1009, 1, "C", "6.0", np.nan, "Form sent out", "MoR"],
            [1010, 0, np.nan, "0006", "NP10 6RT", "Form sent out", "MoR"],
            [1010, 1, "C", "1", np.nan, "Check needed", np.nan],
            [1010, 2, "D", "0001", np.nan, "Check needed", np.nan],
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
            [1001, 2, "D", "0006", "CF14 9XY", "Clear", "R"],
            [1003, 1, "C", "0001", "NP10 2RT", "Clear", "MoR"],
            [1004, 2, "D", "0006", np.nan, "Form sent out", "MoR"],
            [1005, 1, "D", np.nan, "SW5 2DW", "Check needed", "MoR"],
            [1006, 0, np.nan, "0006", "CF48 9DU", "Clear - overidden", np.nan],
            [1006, 1, "C", "0006", "CF48 9DU", "Clear", "R"],
            [1006, 2, "D", "0006", "CF48 9DU", "Clear", "R"]
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
            [1007, 2, "D", "0006", "SW5  2DW", "Clear", "R"],
            [1008, 2, "D", "0001", "NP10 2RT", "Clear", "MoR"],
            [1009, 1, "C", "0006", np.nan, "Form sent out", "MoR"],
            [1010, 0, np.nan, "0006", "NP10 6RT", "Form sent out", "MoR"],
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
