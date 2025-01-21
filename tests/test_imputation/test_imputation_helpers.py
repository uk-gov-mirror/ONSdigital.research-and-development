import pandas as pd
import numpy as np
from pandas import DataFrame as pandasDF
from pandas._testing import assert_series_equal, assert_frame_equal

from src.imputation.imputation_helpers import (
    copy_first_to_group,
    fix_604_error,
    create_r_and_d_instance,
    check_604_fix,
    calculate_totals,
    create_imp_class_col,
    imputation_marker,
    get_imputation_cols
)


class TestCopyFirstToGroup:
    """Unit tests for copy_first_to_group function."""

    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "instance",
            "200",
            "604",
        ]

        data = [
            [1001, 0, None, "No"],
            [1001, 1, "C", None],
            [1001, 2, "C", None],
            [1001, 3, "D", None],
            [2002, 0, None, "Yes"],
            [3003, 0, None, None],
            [3003, 1, "C", None],
            [3003, 2, "C", "Haha"],
            [3003, 3, "D", None],
            [4004, 0, None, None],
        ]

        input_df = pandasDF(data=data, columns=input_cols)
        return input_df

    def test_copy_first_to_group(self):
        """Test for function copy_first_to_group."""
        input_df = self.create_input_df()

        expected_output = pd.Series(
            [
                "No",
                "No",
                "No",
                "No",
                "Yes",
                "Haha",
                "Haha",
                "Haha",
                "Haha",
                None,
            ],
            name="604",
        )

        result_df = copy_first_to_group(input_df, "604")
        assert_series_equal(result_df, expected_output)


class TestFix604Error:
    """Unit tests for fix_604_error function."""

    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "instance",
            "200",
            "604",
            "formtype",
        ]

        data = [
            [1001, 0, None, "No", "0001"],
            [1001, 1, "C", np.nan, "0001"],
            [1001, 2, "C", np.nan, "0001"],
            [1001, 3, "D", np.nan, "0001"],
            [2002, 0, None, "Yes", "0001"],
            [3003, 0, None, np.nan, "0001"],
            [3003, 1, "C", np.nan, "0001"],
            [3003, 2, "C", "Haha", "0001"],
            [3003, 3, "D", np.nan, "0001"],
            [4004, 0, None, None, "0001"],
        ]

        input_df = pandasDF(data=data, columns=input_cols)
        return input_df

    def create_expected_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "instance",
            "200",
            "604",
            "formtype",
        ]

        filtered_data = [
            [1001, 0, None, "No", "0001"],
            [2002, 0, None, "Yes", "0001"],
            [3003, 0, None, "Haha", "0001"],
            [3003, 1, "C", "Haha", "0001"],
            [3003, 2, "C", "Haha", "0001"],
            [3003, 3, "D", "Haha", "0001"],
            [4004, 0, None, None, "0001"],
        ]

        qa_data = [
            [1001, 0, None, "No", "0001"],
            [1001, 1, "C", "No", "0001"],
            [1001, 2, "C", "No", "0001"],
            [1001, 3, "D", "No", "0001"],
        ]
        expected_filtered_df = pandasDF(data=filtered_data, columns=input_cols)
        expected_qa_df = pandasDF(data=qa_data, columns=input_cols)

        return expected_filtered_df, expected_qa_df

    def test_fix_604_error(self):
        """Test for function fix_604_error."""
        input_df = self.create_input_df()
        expected_filtered_df, expected_qa_df = self.create_expected_df()

        result_df, qa_df = fix_604_error(input_df)
        assert_frame_equal(result_df.reset_index(drop=True), expected_filtered_df)
        assert_frame_equal(qa_df.reset_index(drop=True), expected_qa_df)

    def test_check_604_fix(self):
        """Test for function check 604 fix"""
        # Create an input dataframe for the test
        input_cols = [
            "reference",
            "instance",
            "200",
            "604",
            "formtype",
        ]
        input_data = [
            [1001, 0, None, "No", "0001"],
            [2002, 0, None, "Yes", "0001"],
            [3003, 0, None, "No", "0001"],
            [3003, 1, "C", "No", "0001"],
            [3003, 1, "C", "No", "0001"],
            [4004, 0, None, None, "0001"],
        ]

        exp_data = [
            [1001, 0, None, "No", "0001"],
            [2002, 0, None, "Yes", "0001"],
            [3003, 0, None, "No", "0001"],
            [3003, 1, "C", "No", "0001"],
            [4004, 0, None, None, "0001"],
        ]

        expected_check_cols = ["reference", "instance", "ref_count"]
        expected_check_data = [
            [3003, 1, 2],
            [3003, 1, 2],
        ]

        input_df = pandasDF(data=input_data, columns=input_cols)
        expected_df = pandasDF(data=exp_data, columns=input_cols)
        exp_check_df = pandasDF(data=expected_check_data, columns=expected_check_cols)

        result_df, check_df = check_604_fix(input_df)

        assert_frame_equal(result_df.reset_index(drop=True), expected_df)
        assert_frame_equal(check_df.reset_index(drop=True), exp_check_df)


class TestCreateRAndDInstance:
    """Unit tests for create_r_and_d_instance function."""

    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "instance",
            "200",
            "604",
            "formtype",
        ]

        data = [
            [1001, 0, None, "No", "0001"],
            [1001, 1, "C", np.nan, "0001"],
            [1001, 2, "C", np.nan, "0001"],
            [1001, 3, "D", np.nan, "0001"],
            [2002, 0, None, "Yes", "0001"],
            [2002, 1, "C", "Yes", "0001"],
            [3003, 0, None, "No", "0001"],
            [4004, 0, None, None, "0001"],
        ]

        input_df = pandasDF(data=data, columns=input_cols)
        return input_df

    def create_expected_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "instance",
            "200",
            "604",
            "formtype",
        ]

        data = [
            [1001, 0, None, "No", "0001"],
            [1001, 1, None, "No", "0001"],
            [2002, 0, None, "Yes", "0001"],
            [2002, 1, "C", "Yes", "0001"],
            [3003, 0, None, "No", "0001"],
            [3003, 1, None, "No", "0001"],
            [4004, 0, None, None, "0001"],
        ]

        expected_df = pandasDF(data=data, columns=input_cols)
        return expected_df

    def test_create_r_and_d_instance(self):
        """Test for function fix_604_error."""
        input_df = self.create_input_df()
        expected_df = self.create_expected_df()

        result_df, qa_df = create_r_and_d_instance(input_df)
        assert_frame_equal(result_df.reset_index(drop=True), expected_df)

class TestCalculateTotals:
    """Unit tests for calculate_totals function."""

    def test_calculate_totals(self):
        """Test for function calculate_totals."""
        # Create an input dataframe for the test
        input_cols = [
            "formtype",
            "emp_researcher_imputed",
            "emp_technician_imputed",
            "emp_other_imputed",
            "headcount_res_m_imputed",
            "headcount_tec_m_imputed",
            "headcount_oth_m_imputed",
            "headcount_res_f_imputed",
            "headcount_tec_f_imputed",
            "headcount_oth_f_imputed",
        ]

        data = [
            ["0001", 10, 5, 3, 20, 10, 5, 15, 8, 4],
            ["0001", 8, 4, 2, 15, 7, 3, 12, 6, 2],
            ["0006", 6, 3, 1, 10, 5, 2, 8, 4, 1],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)

        # Create an expected dataframe for the test
        expected_cols = [
            "formtype",
            "emp_researcher_imputed",
            "emp_technician_imputed",
            "emp_other_imputed",
            "headcount_res_m_imputed",
            "headcount_tec_m_imputed",
            "headcount_oth_m_imputed",
            "headcount_res_f_imputed",
            "headcount_tec_f_imputed",
            "headcount_oth_f_imputed",
            "emp_total_imputed",
            "headcount_tot_m_imputed",
            "headcount_tot_f_imputed",
            "headcount_total_imputed",
        ]

        expected_data = [
            ["0001", 10, 5, 3, 20, 10, 5, 15, 8, 4, 18, 35, 27, 62],
            ["0001", 8, 4, 2, 15, 7, 3, 12, 6, 2, 14, 25, 20, 45],
            ["0006", 6, 3, 1, 10, 5, 2, 8, 4, 1, np.nan, np.nan, np.nan, np.nan],
        ]

        expected_df = pd.DataFrame(data=expected_data, columns=expected_cols)

        # Apply the calculate_totals function to the input dataframe
        result_df = calculate_totals(input_df)

        # display the full dataframe without truncating columns
        pd.set_option("display.max_columns", None)

        # Assert that the result dataframe is equal to the expected dataframe
        pd.testing.assert_frame_equal(result_df, expected_df, check_dtype=False)


class TestCreateImpClassCol:
    """Unit tests for create_imp_class_col function."""
    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_columns = [
            "reference",
            "instance",
            "200",
            "201",
            "211",
            "pg_numeric",
            "formtype",
            "cellnumber",
            "rusic",
        ]

        data = [
            [111, 1, "C", "AA", 600.0, 23.0, "0001", 45, 4445],
            [111, 2, "C", "AB", 700.0, 24.0, "0001", 45, 4445],
            [222, 1, "C", "AA", 55.0, 23.0, "0006", 35, 3335],
            [222, 2, "D", "DE", 21.0, 14.0, "0006", 35, 3335],
            [333, 1, "C", "E", 100.0, 25.0, "0001", 66, 5554],
            [333, 2, np.nan, np.nan, np.nan, np.nan, "0001", 66, 5554],
            [444, 1, "C", "AA", 200.0, 23.0, "0001", 817, 7777],
        ]

        input_df = pandasDF(data=data, columns=input_columns)
        return input_df


    def create_exp_output_df(self):
        """Create an exp_output dataframe for the test."""
        exp_output_columns = [
            "reference",
            "instance",
            "200",
            "201",
            "211",
            "pg_numeric",
            "formtype",
            "cellnumber",
            "rusic",
            "imp_class",
        ]

        data = [
            [111, 1, "C", "AA", 600.0, 23.0, "0001", 45, 4445, "C_AA"],
            [111, 2, "C", "AB", 700.0, 24.0, "0001", 45, 4445, "C_AB"],
            [222, 1, "C", "AA", 55.0, 23.0, "0006", 35, 3335, "C_AA"],
            [222, 2, "D", "DE", 21.0, 14.0, "0006", 35, 3335, "D_DE"],
            [333, 1, "C", "E", 100.0, 25.0, "0001", 66, 5554, "C_E"],
            [333, 2, np.nan, np.nan, np.nan, np.nan, "0001", 66, 5554, "nan_nan"],
            [444, 1, "C", "AA", 200.0, 23.0, "0001", 817, 7777, "C_AA_817"],
        ]

        exp_output_df = pandasDF(data=data, columns=exp_output_columns)
        return exp_output_df

    def test_create_imp_class_col(self):
        """Test for function create_imp_class_col."""
        input_df = self.create_input_df()
        exp_output_df = self.create_exp_output_df()

        result_df = create_imp_class_col(input_df, ["200", "201"])
        assert_frame_equal(result_df.reset_index(drop=True), exp_output_df)


    class TestImputationMarker:
        """Unit tests for imputation_marker function."""

        def create_input_df(self):
            """Create an input dataframe for the test."""
            input_cols = [
                "reference",
                "status"
            ]

            data = [
                [111, "Clear"],
                [222, "Clear - overridden"],
                [333, "Check needed"],
                [444, "Form sent out"],
                [555, "Clear"]
            ]
            input_df = pandasDF(data=data, columns=input_cols)
            return input_df

        def create_exp_output_df(self):
            """Create an exp_output dataframe for the test."""
            exp_output_cols = [
                "reference",
                "status",
                "imp_marker"
            ]

            data = [
                [111, "Clear", "R"],
                [222, "Clear - overridden", "R"],
                [333, "Check needed", "no_imputation"],
                [444, "Form sent out", "no_imputation"],
                [555, "Clear", "R"]
            ]

            exp_output_df = pandasDF(data=data, columns=exp_output_cols)
            return exp_output_df

        def test_imputation_marker(self):
            """Test for function imputation_marker."""
            input_df = self.create_input_df()
            exp_output_df = self.create_exp_output_df()

            result_df = imputation_marker(input_df)
            assert_frame_equal(result_df.reset_index(drop=True), exp_output_df)

class TestGetImputationCols:
    """Unit tests for get_imputation_cols function."""

    def create_input_dict(self):
        """Create an input dictionary for the test."""
        # config["breakdowns"] and config["imputation"] from dev_config.yaml
        input_config = {
            "breakdowns" : {"219" : {"202", "203", "204", "205", "206", "207", "209",
                                     "210", "212", "214", "216", "218", "219", "220",
                                     "221", "222", "223", "225", "226", "227", "228",
                                     "229", "237", "242", "243", "244", "245", "246",
                                     "247", "248", "249", "250", "305", "302", "399"},
                            "emp_total" : {"emp_researcher", "emp_technician", "emp_other"},
                            "headcount_total" : {"headcount_res_m", "headcount_res_f",
                                                 "headcount_tec_m", "headcount_tec_f",
                                                 "headcount_oth_x", "headcount_oth_y"}
                            },
            "imputation" : {"sum_cols": {"emp_total", "headcount_tot_x",
                                         "headcount_tot_y", "headcount_total"}
                            }
                  }
        return input_config

    def test_get_imputation_cols(self):
        """Test for function copy_first_to_group."""
        input_config = self.create_input_dict()

        expected_output = ["219", "305", "emp_total", "headcount_total",
                           "202", "203", "204", "205", "206", "207", "209",
                           "210", "212", "214", "216", "218", "219", "220",
                           "221", "222", "223", "225", "226", "227", "228",
                           "229", "237", "242", "243", "244", "245", "246",
                           "247", "248", "249", "250", "302", "399",
                           "emp_researcher", "emp_technician", "emp_other",
                           "headcount_res_m", "headcount_res_f", "headcount_tec_m",
                           "headcount_tec_f", "headcount_oth_x", "headcount_oth_y",
                           "headcount_tot_x", "headcount_tot_y"]

        result_list = get_imputation_cols(input_config)

        difference = {*expected_output} ^ {*result_list}
        assert not difference
