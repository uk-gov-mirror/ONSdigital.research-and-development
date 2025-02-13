"""Tests for MoR.py."""

# Local Imports
import os

# Third Party Imports
import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

# Local Imports
from src.imputation.MoR import run_mor, is_lf_only, calculate_growth_rates
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

class Test_calculate_growth_rates(object):
    """Tests for calculate_growth_rates."""

    @pytest.fixture(scope="function")
    def target_vars_list(self):
        """A simple fixture that returns a list."""
        return ["211", "emp_researcher", "emp_technician"]

    @pytest.fixture(scope="function")
    def create_test_CGR_current_df(self):
            """Create an test_CGR_current dataframe for the test."""
            columns = [
            "reference",
            "instance",
            "period_year",
            "200",
            "201",
            "211",
            "212",
            "emp_researcher",
            "emp_technician",
            "cellnumber",
            "601",
            "602",
            "604",
            "emp_total",
            "formtype",
            "status",
            "postcodes_harmonised",
            "imp_marker",
            "imp_class",
            "selectiontype",
        ]

            data = [
                [1031, 0, 2022, np.nan, "AA", 0, np.nan, 0, 0, 286, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "CF14 7UB", "R", "<NA>_AA", "C"],
                [1031, 0, 2022, np.nan, "AA", 0, np.nan, 0, 0, 286, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "CF14 7UB", "R", "<NA>_AA", "C"],
                [1031, 0, 2022, np.nan, "AA", 0, np.nan, 0, 0, 286, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "CF14 7UB", "R", "<NA>_AA", "C"],
                [1031, 1, 2022, "C", "AA", 0, np.nan, 10, 0, 286, np.nan, np.nan, np.nan, 10.0, "0001", "Clear", "CF14 7UB", "R", "C_AA", "C"],
                [1031, 1, 2022, "C", "AA", 0, np.nan, 10, 0, 286, np.nan, np.nan, np.nan, 10.0, "0001", "Clear", "CF14 7UB", "R", "C_AA", "C"],
                [1031, 1, 2022, "C", "AA", 0, np.nan, 10, 0, 286, np.nan, np.nan, np.nan, 10.0, "0001", "Clear", "CF14 7UB", "R", "C_AA", "C"],
                [1031, 2, 2022, "D", "AA", 0, np.nan, 0, 0, 286, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "CF14 7UB", "R", "D_AA", "C"],
                [1031, 2, 2022, "D", "AA", 0, np.nan, 0, 0, 286, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "CF14 7UB", "R", "D_AA", "C"],
                [1031, 2, 2022, "D", "AA", 0, np.nan, 0, 0, 286, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "CF14 7UB", "R", "D_AA", "C"],
                [1032, 0, 2022, np.nan, "L", 12000, 12000.0, 0, 0, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Clear", "CV34 6UX", "R", "<NA>_L", "C"],
                [1032, 0, 2022, np.nan, "L", 12000, 12000.0, 0, 0, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Clear", "CV34 6UX", "R", "<NA>_L", "C"],
                [1032, 1, 2022, np.nan, "L", 0, np.nan, 0, 0, 41, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "CV34 6UX", "R", "<NA>_L", "C"],
                [1032, 1, 2022, np.nan, "L", 0, np.nan, 0, 0, 41, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "CV34 6UX", "R", "<NA>_L", "C"],
                [1033, 0, 2022, np.nan, "AB", 0, np.nan, 0, 0, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "NY56 9DV", "R", "<NA>_AB", "C"],
                [1033, 0, 2022, np.nan, "AB", 0, np.nan, 0, 0, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "NY56 9DV", "R", "<NA>_AB", "C"],
                [1033, 1, 2022, "C", "AB", 0, np.nan, 0, 0, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "NY56 9DV", "R", "C_AB", "C"],
                [1033, 1, 2022, "C", "AB", 0, np.nan, 0, 0, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "NY56 9DV", "R", "C_AB", "C"],
                [1040, 1, 2022, "D", "G", 86000, 86000.0, 0, 0, 60, np.nan, np.nan, np.nan, np.nan, "0006", "Clear", "UB6 OHE", "R", "D_AB", "C"],
                [1042, 1, 2022, "D", "P", 9000, 9000.0, 0, 0, 82, np.nan, np.nan, np.nan, np.nan, "0006", "Clear", "AB10 1BL", "R", "D_AB", "C"],
                [1045, 0, 2022, np.nan, "AH", 0, np.nan, 0, 0, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "<NA>_AH", "C"],
                [1045, 0, 2022, np.nan, "AH", 0, np.nan, 0, 0, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "<NA>_AH", "C"],
                [1045, 0, 2022, np.nan, "AH", 0, np.nan, 0, 0, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "<NA>_AH", "C"],
                [1045, 1, 2022, "C", "AH", 0, np.nan, 0, 10, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "C_AH", "C"],
                [1045, 1, 2022, "C", "AH", 0, np.nan, 0, 10, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "C_AH", "C"],
                [1045, 1, 2022, "C", "AH", 0, np.nan, 0, 10, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "C_AH", "C"],
                [1045, 2, 2022, "D", "AH", 0, np.nan, 0, 10, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "D_AH", "C"],
                [1045, 2, 2022, "D", "AH", 0, np.nan, 0, 10, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "D_AH", "C"],
                [1045, 2, 2022, "D", "AH", 0, np.nan, 0, 10, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "WA3 6AE", "R", "D_AH", "C"],
                [1046, 0, 2022, np.nan, "AD", 84100, 84100.0, 0, 0, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "<NA>_AD", "C"],
                [1046, 0, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "<NA>_AD", "C"],
                [1046, 0, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "<NA>_AD", "C"],
                [1046, 0, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "<NA>_AD", "C"],
                [1046, 0, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "<NA>_AD", "C"],
                [1046, 1, 2022, "D", "AD", 80500, np.nan, 0, 0, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "D_AD", "C"],
                [1046, 1, 2022, "D", "AD", 80500, np.nan, 0, 0, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "D_AD", "C"],
                [1046, 1, 2022, "D", "AD", 80500, np.nan, 0, 0, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "D_AD", "C"],
                [1046, 1, 2022, "D", "AD", 80500, np.nan, 0, 0, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "D_AD", "C"],
                [1046, 1, 2022, "D", "AD", 80500, np.nan, 0, 0, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Clear", "GJ73 3GB", "R", "D_AD", "C"],
                [1046, 2, 2022, "C", "AD", 36000, np.nan, 0, 0, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Clear", "PL6 8BX", "R", "C_AD", "C"],
                [1046, 2, 2022, "C", "AD", 36000, np.nan, 0, 0, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Clear", "PL6 8BX", "R", "C_AD", "C"],
                [1046, 2, 2022, "C", "AD", 36000, np.nan, 0, 0, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Clear", "PL6 8BX", "R", "C_AD", "C"],
                [1046, 2, 2022, "C", "AD", 36000, np.nan, 0, 0, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Clear", "PL6 8BX", "R", "C_AD", "C"],
                [1046, 3, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Clear", "RG7 2PQ", "R", "<NA>_AD", "C"],
                [1046, 3, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Clear", "RG7 2PQ", "R", "<NA>_AD", "C"],
                [1046, 3, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Clear", "RG7 2PQ", "R", "<NA>_AD", "C"],
                [1046, 3, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Clear", "RG7 2PQ", "R", "<NA>_AD", "C"],
                [1046, 4, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Clear", "GU16 7HF", "R", "<NA>_AD", "C"],
                [1046, 4, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Clear", "GU16 7HF", "R", "<NA>_AD", "C"],
                [1046, 4, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Clear", "GU16 7HF", "R", "<NA>_AD", "C"],
                [1046, 4, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Clear", "GU16 7HF", "R", "<NA>_AD", "C"],
                [1046, 4, 2022, np.nan, "AD", 0, np.nan, 0, 0, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Clear", "GU16 7HF", "R", "<NA>_AD", "C"],
                [1047, 0, 2022, np.nan, "BC", 600, np.nan, 0, 0, 262, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "TY85 1ND", "R", "<NA>_BC", "C"],
                [1047, 1, 2022, "C", "BC", 400, np.nan, 0, 0, 262, "TY85 1ND", np.nan, "Yes", np.nan, "0001", "Clear", "TY85 1ND", "R", "C_BC", "C"],
                [1047, 2, 2022, "D", "BC", 200, np.nan, 0, 0, 262, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "TY85 1ND", "R", "D_BC", "C"],
            ]

            test_CGR_current_df = pd.DataFrame(data=data, columns=columns)
            test_CGR_current_df = test_CGR_current_df.astype({"reference": "Int64", "instance": "Int64"})
            return test_CGR_current_df

    @pytest.fixture(scope="function")
    def create_test_CGR_backdata_df(self):
        """Create an test_CGR_backdata dataframe for the test."""
        test_CGR_backdata_columns = [
        "reference",
        "instance",
        "period_year",
        "200",
        "201",
        "211",
        "212",
        "emp_researcher",
        "emp_technician",
        "601",
        "602",
        "604",
        "emp_total",
        "formtype",
        "status",
        "imp_marker",
        "imp_class",
        "selectiontype",
    ]

        data = [
        [1031, 0, 2021, np.nan, "AA", 6000.0, np.nan, np.nan, np.nan, "CF14 7UB", np.nan, "Yes", np.nan, "0001", "Clear", "R", "nan_AA", "C"],
        [1031, 1, 2021, "C", "AA", np.nan, np.nan, 10.0, np.nan, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "R", "C_AA", "C"],
        [1031, 2, 2021, "D", "AA", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "R", "D_AA", "C"],
        [1032, 0, 2021, np.nan, "L", 11000.0, 11000.0, np.nan, np.nan, "CV34 6UX", np.nan, np.nan, 10.0, "0001", "Clear", "R", "nan_L", "C"],
        [1032, 1, 2021, "C", "L", np.nan, np.nan, 0.0, 0.0, "CV34 6UX", np.nan, np.nan, 10.0, "0001", "Clear", "R", "C_L", "C"],
        [1040, 1, 2021, "D", "G", 87200.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, "0006", "Clear", "R", "D_G", "C"],
        [1042, 1, 2021, "D", "P", 8000.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, "0006", "Clear", "R", "D_P", "C"],
        [1045, 0, 2021, np.nan, "AH", 20000.0, np.nan, np.nan, np.nan, "WA3 6AE", np.nan, "Yes", np.nan, "0001", "Clear", "R", "nan_AH", "C"],
        [1045, 1, 2021, "C", "AH", 10000.0, np.nan, np.nan, 10.0, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "R", "C_AH", "C"],
        [1045, 2, 2021, "D", "AH", 10000.0, np.nan, np.nan, 10.0, np.nan, np.nan, "Yes", np.nan, "0001", "Clear", "R", "D_AH", "C"],
        [1047, 0, 2021, np.nan, "BC", 600.0, 600.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "R", "nan_BC", "C"],
        [1047, 1, 2021, "C", "BC", 400.0, np.nan, np.nan, np.nan, "TY85 1ND", np.nan, "Yes", np.nan, "0001", "Clear", "R", "C_BC", "C"],
        [1047, 2, 2021, "D", "BC", 200.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, "0001", "Clear", "R", "D_BC", "C"],
    ]

        test_CGR_backdata_df = pd.DataFrame(data=data, columns=test_CGR_backdata_columns)
        return test_CGR_backdata_df

    @pytest.fixture(scope="function")
    def create_test_CGR_expected_df(self):
        """Create an test_CGR_expected dataframe for the test."""
        test_CGR_expected_columns = [
        "reference",
        "imp_class",
        "211",
        "emp_researcher",
        "emp_technician",
        "211_prev",
        "emp_researcher_prev",
        "emp_technician_prev",
        "211_gr",
        "emp_researcher_gr",
        "emp_technician_gr",
    ]

        data = [
        [1031, "C_AA", 0, 30, 0, 0.0, 10.0, 0.0, np.nan, 3.0, np.nan],
        [1031, "D_AA", 0, 0, 0, 0.0, 0.0, 0.0, np.nan, np.nan, np.nan],
        [1045, "C_AH", 0, 0, 30, 10000.0, 0.0, 10.0, np.nan, np.nan, 3.0],
        [1045, "D_AH", 0, 0, 30, 10000.0, 0.0, 10.0, np.nan, np.nan, 3.0],
        [1047, "C_BC", 400, 0, 0, 400.0, 0.0, 0.0, 1.0, np.nan, np.nan],
        [1047, "D_BC", 200, 0, 0, 200.0, 0.0, 0.0, 1.0, np.nan, np.nan],
    ]

        test_CGR_expected_df = pd.DataFrame(data=data, columns=test_CGR_expected_columns)
        return test_CGR_expected_df


    def test_calculate_growth_rates(
        self,
        create_test_CGR_current_df,
        create_test_CGR_backdata_df,
        create_test_CGR_expected_df,
        target_vars_list

    ):
        """Test the calculate_growth_rates function."""
        current_df = create_test_CGR_current_df
        backdata_df = create_test_CGR_backdata_df
        expected_df = create_test_CGR_expected_df
        target_vars = target_vars_list

        result_df = calculate_growth_rates(current_df, backdata_df, target_vars)

        assert_frame_equal(result_df, expected_df, check_dtype=False, check_exact=False), (
            "calculate_growth_rates() did not return the expected dataframe."
        )
