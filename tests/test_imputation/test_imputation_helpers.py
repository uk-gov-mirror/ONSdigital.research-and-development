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
    concat_with_bool,
    create_notnull_mask,
    get_imputation_cols,
    instance_fix,
    create_mask,
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
            "area",
        ]

        data = [
            [111, 1, "C", "AA", 600.0, 23.0, "0001", 45, 4445, "area_oth"],
            [111, 2, "C", "AB", 700.0, 24.0, "0001", 45, 4445, "area_oth"],
            [222, 1, "C", "AA", 55.0, 23.0, "0006", 35, 3335, "area_se"],
            [222, 2, "D", "DE", 21.0, 14.0, "0006", 35, 3335, "area_oth"],
            [333, 1, "C", "E", 100.0, 25.0, "0001", 66, 5554, "area_se"],
            [333, 2, np.nan, np.nan, np.nan, np.nan, "0001", 66, 5554, "area_se"],
            [444, 1, "C", "AA", 200.0, 23.0, "0001", 817, 7777, "area_oth"],
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
            "area",
            "imp_class",
        ]

        data = [
            [111, 1, "C", "AA", 600.0, 23.0, "0001", 45, 4445, "area_oth", "C_AA"],
            [111, 2, "C", "AB", 700.0, 24.0, "0001", 45, 4445, "area_oth", "C_AB"],
            [222, 1, "C", "AA", 55.0, 23.0, "0006", 35, 3335, "area_se", "C_AA"],
            [222, 2, "D", "DE", 21.0, 14.0, "0006", 35, 3335, "area_oth", "D_DE"],
            [333, 1, "C", "E", 100.0, 25.0, "0001", 66, 5554, "area_se", "C_E"],
            [333, 2, np.nan, np.nan, np.nan, np.nan, "0001", 66, 5554, "area_se", "nan_nan"],
            [444, 1, "C", "AA", 200.0, 23.0, "0001", 817, 7777, "area_oth", "C_AA_817"],
        ]

        exp_output_df = pandasDF(data=data, columns=exp_output_columns)
        return exp_output_df

    def create_exp_output_pnp_df(self):
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
            "area",
            "imp_class",
        ]

        data = [
            [111, 1, "C", "AA", 600.0, 23.0, "0001", 45, 4445, "area_oth", "area_oth"],
            [111, 2, "C", "AB", 700.0, 24.0, "0001", 45, 4445, "area_oth", "area_oth"],
            [222, 1, "C", "AA", 55.0, 23.0, "0006", 35, 3335, "area_se", "area_se"],
            [222, 2, "D", "DE", 21.0, 14.0, "0006", 35, 3335, "area_oth", "area_oth"],
            [333, 1, "C", "E", 100.0, 25.0, "0001", 66, 5554, "area_se", "area_se"],
            [333, 2, np.nan, np.nan, np.nan, np.nan, "0001", 66, 5554, "area_se", "area_se"],
            [444, 1, "C", "AA", 200.0, 23.0, "0001", 817, 7777, "area_oth", "area_oth"],
        ]

        exp_output_df = pandasDF(data=data, columns=exp_output_columns)
        return exp_output_df

    def test_create_imp_class_col(self):
        """Test for function create_imp_class_col."""
        input_df = self.create_input_df()
        exp_output_df = self.create_exp_output_df()

        result_df = create_imp_class_col(input_df, ["200", "201"])
        assert_frame_equal(result_df.reset_index(drop=True), exp_output_df)

    def test_create_imp_class_col_pnp(self):
        """Test for function create_imp_class_col."""
        input_df = self.create_input_df()
        exp_output_df = self.create_exp_output_pnp_df()

        result_df = create_imp_class_col(input_df, ["area"], use_cellno=False)
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

class TestConcatWithBool:
    """Unit tests for concat_with_bool function."""
    def input_dfs(self):
        """Define columns and values for the DataFrames"""
        columns1 = ['manual_trim', 'empty_pgsic_group', 'value']
        values1 = [
            [True, False, 1],
            [False, True, 2],
            [np.nan, np.nan, 3],
        ]

        columns2 = ['empty_pg_group', '305_trim', 'value']
        values2 = [
            [True, False, 4],
            [False, True, 5],
            [np.nan, np.nan, 6]
        ]

        columns3 = ['211_trim', 'value']
        values3 = [
            [True, 7],
            [False, 8],
            [np.nan, 9],
        ]

        # Create DataFrames from the lists of values
        df1 = pd.DataFrame(values1, columns=columns1)
        df2 = pd.DataFrame(values2, columns=columns2)
        df3 = pd.DataFrame(values3, columns=columns3)

        return df1, df2, df3

    def expected_output(self):
        """Define the expected output DataFrame"""
        columns = ['manual_trim', 'empty_pgsic_group', 'empty_pg_group', '305_trim', '211_trim', 'value']
        values = [
            [True, False, False, False, False, 1],
            [False, True, False, False, False, 2],
            [False, False, False, False, False, 3],
            [False, False, True, False, False, 4],
            [False, False, False, True, False, 5],
            [False, False, False, False, False, 6],
            [False, False, False, False, True, 7],
            [False, False, False, False, False, 8],
            [False, False, False, False, False, 9],
        ]

        df = pd.DataFrame(values, columns=columns)
        # ensure the datatype of the columns are bool where they should be
        for col in columns[:-1]:
            df[col] = df[col].astype('bool')

        return df

    def test_concat_with_bool(self):
        """Test for function concat_with_bool."""
        df1, df2, df3 = self.input_dfs()
        expected_df = self.expected_output()

        result_df = concat_with_bool([df1, df2, df3])
        # ignore the order of the columns
        assert_frame_equal(result_df.reset_index(drop=True), expected_df, check_like=True)

class TestCreateRAndDInstance:
    """ Unit test for check_r_and_d_instance function """
    def cre_input_df(self) -> pd.DataFrame:
        """Define columns and values for the DataFrame"""
        columns = ["reference", "instance", "604", "formtype"]
        values = [
            [1000, 0, "No", "0001"],
            [1001, 0, "Yes", "0001"],
            [1001, 1, "Yes", "0001"],
            [1001, 2, "Yes", "0001"],
            [1002, np.nan, np.nan, "0001"],
            [1003, 0, "No", "0001"],
            [1003, 1, "No", "0001"],
            [1004, 0, "Yes", "0006"],
            [1004, 1, "Yes", "0006"],
            [1004, 2, "Yes", "0006"],
            [1005, 0, np.nan, "0006"],
            [1005, 1, np.nan, "0006"],
            [1005, 2, np.nan, "0006"],
            [1006, 0, "Yes", "0001"],
            [1006, 1, "Yes", "0001"],
            [1006, 2, "Yes", "0001"],
            [1007, 0, "No", "0001"],
        ]

        # Create DataFrame from the lists of values
        df = pd.DataFrame(values, columns=columns)
        return df

    def cre_expected_output(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """ define expected output dataframes.
        """
        columns1 = ["reference", "instance", "604", "formtype"]
        values1 = [
            [1000, 0, "No", "0001"],
            [1000, 1, "No", "0001"],
            [1001, 0, "Yes", "0001"],
            [1001, 1, "Yes", "0001"],
            [1001, 2, "Yes", "0001"],
            [1002, np.nan, np.nan, "0001"],
            [1003, 0, "No", "0001"],
            [1003, 1, "No", "0001"],
            [1004, 0, "Yes", "0006"],
            [1004, 1, "Yes", "0006"],
            [1004, 2, "Yes", "0006"],
            [1005, 0, np.nan, "0006"],
            [1005, 1, np.nan, "0006"],
            [1005, 2, np.nan, "0006"],
            [1006, 0, "Yes", "0001"],
            [1006, 1, "Yes", "0001"],
            [1006, 2, "Yes", "0001"],
            [1007, 0, "No", "0001"],
            [1007, 1, "No", "0001"],
        ]

        # Create DataFrame from the lists of values
        final_df = pd.DataFrame(values1, columns=columns1)

        columns2 = ["reference", "instance", "604", "formtype"]
        values2 = [
            [1003, 0, "No", "0001"],
            [1003, 1, "No", "0001"],
        ]
        # Create DataFrame from the lists of values
        mult_604_qa_df = pd.DataFrame(values2, columns=columns2)

        return final_df, mult_604_qa_df

    def test_create_r_and_d_instance(self):
        """Test for function check_r_and_d_instance"""
        input_df = self.cre_input_df()
        expected_final_df, expected_mult_604_qa_df  = self.cre_expected_output()

        check_final_df, check_mult_604_qa_df = create_r_and_d_instance(input_df)

        assert_frame_equal(check_final_df.reset_index(drop=True), expected_final_df, check_dtype=False)
        assert_frame_equal(check_mult_604_qa_df.reset_index(drop=True), expected_mult_604_qa_df, check_dtype=False)

class TestCreateNotnullMask:
    """ Unit test for create_notnull_mask function """
    def cre_input_df(self) -> pd.DataFrame:
        """Define columns and values for the DataFrame"""
        columns_df = ['600', '601', '602']
        values_df = [
            ["AA", "AA01 1AA", np.nan],
            [np.nan, np.nan, "XX"],
            ["BB", "", "YY"],
            ["CC", "BB1 1BB", "ZZ"]
        ]

        # Create DataFrame from the lists of values
        df = pd.DataFrame(values_df, columns=columns_df)
        return df

    def cre_expected_output(self) -> pd.Series:
        """ define expecetd output series """
        ser = pd.Series(
            [
                True,
                False,
                False,
                True,
            ],
            name="601",)
        return ser

    def test_create_notnull_mask(self):
        input_df = self.cre_input_df()
        expected_output = self.cre_expected_output()

        output = create_notnull_mask(input_df, "601")
        assert_series_equal(output, expected_output)

class TestGetImputationCols:
    """ Unit test for get_imputation_cols function """
    def cre_input_dict(self) -> dict:
        """Define config dict"""

        config_dict = {
            "breakdowns" :
            {
                "299" : ["200", "201", "202", "298"],
                "399" : ["300", "301", "302", "398"],
                "emp_stat" : ["emp_type1", "emp_type2", "emp_type3"],
                "headcount_stat" : ["headcount_type1", "headcount_type2", "headcount_type3"]
            },
            "imputation" :
            {
                "sum_cols" : ["emp_stat", "headcount_1_tot", "headcount_2_tot", "headcount_tot"]
            }

        }

        return config_dict

    def cre_expected_output(self) -> list:
        """ define expected output list """
        exp_list = [
            "299", "399", "emp_stat", "headcount_stat",
            "200", "201", "202", "298",
            "300", "301", "302", "398",
            "emp_type1", "emp_type2", "emp_type3",
            "headcount_type1", "headcount_type2", "headcount_type3",
            "headcount_1_tot", "headcount_2_tot", "headcount_tot"
            ]
        return exp_list

    def test_get_imputation_cols(self):
        input_dict = self.cre_input_dict()
        expected_output = self.cre_expected_output()

        output = get_imputation_cols(input_dict)
        assert output == expected_output

class TestCreateMask:
    """Unit tests for create_mask function."""

    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "instance",
            "imp_class",
            "imp_marker",
            "211",
            "601",
            "604",
            "status",
            "formtype",
            "selectiontype",
        ]

        data = [
            [111, 0, "nan_A", "CF", np.nan, None, "Yes", "Check needed", "0001", "C"],
            [111, 1, "C_A", "MoR", 1, None, None, "Check needed", "0001", "C"],
            [222, 0, "nan_A", "R", np.nan, None, "No", "Clear", "0001", "C"],
            [222, 1, "C_A", "R", 1, "CB1 2NF", "No", "Clear", "0001", "C"],
            [222, 2, "C_A", "R", np.nan, "BA1 5DA", "No", "Clear", "0001", "C"],
            [333, np.nan, None, "R", np.nan, None, "No", "Form sent out", "0006", "P"],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def test_clear_status(self):
        df = self.create_input_df()
        options = ["clear_status"]
        expected_mask = pd.Series([False, False, True, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_bad_status(self):
        df = self.create_input_df()
        options = ["bad_status"]
        expected_mask = pd.Series([True, True, False, False, False, True])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_instance_zero(self):
        df = self.create_input_df()
        options = ["instance_zero"]
        expected_mask = pd.Series([True, False, True, False, False, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_instance_nonzero(self):
        df = self.create_input_df()
        options = ["instance_nonzero"]
        expected_mask = pd.Series([False, True, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_no_r_and_d(self):
        df = self.create_input_df()
        options = ["no_r_and_d"]
        expected_mask = pd.Series([False, False, True, True, True, True])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_postcode_only(self):
        df = self.create_input_df()
        options = ["postcode_only"]
        expected_mask = pd.Series([False, False, False, False, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_excl_postcode_only(self):
        df = self.create_input_df()
        options = ["excl_postcode_only"]
        expected_mask = pd.Series([True, True, True, True, False, True])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_clear_instance_zero(self):
        df = self.create_input_df()
        options = ["clear_status", "instance_zero"]
        expected_mask = pd.Series([False, False, True, False, False, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_exclude_nan_classes(self):
        df = self.create_input_df()
        options = ["exclude_nan_classes"]
        expected_mask = pd.Series([False, True, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_clear_instance_nonzero(self):
        df = self.create_input_df()
        options = ["clear_status", "instance_nonzero"]
        expected_mask = pd.Series([False, False, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_clear_instance_nonzero_exclude_nan_classes(self):
        df = self.create_input_df()
        options = ["clear_status", "instance_nonzero", "exclude_nan_classes"]
        expected_mask = pd.Series([False, False, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_clear_longfom_instance_nonzero(self):
        df = self.create_input_df()
        options = ["clear_status", "instance_nonzero", "longform"]
        expected_mask = pd.Series([False, False, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

    def test_not_mor_imputed_longform(self):
        df = self.create_input_df()
        options = ["not_mor_imputed", "longform_only"]
        expected_mask = pd.Series([False, False, True, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask)

class TestSpecialFilter:
    """Tests for the SpecialFilter function."""
    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "instance",
            "imp_class",
            "211",
            "601",
            "604",
            "status",
            "formtype",
            "selectiontype",
        ]

        data = [
            [111, 0, "nan_A", np.nan, None, "Yes", "Clear", "0001", "C"],
            [111, 1, "C_A", 1, None, None, "Clear - overridden", "0001", "C"],
            [222, 0, "nan_A", np.nan, None, None, "Clear", "0001", "C"],
            [222, 1, "C_A", 1, "CB1 2NF", "No", "Clear", "0001", "C"],
            [222, 2, "C_A", np.nan, "BA1 5DA", "No", "Clear", "0001", "C"],
            [333, np.nan, "nan_A", np.nan, None, "No", "Form sent out", "0006", "P"],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def test_special_filter_create_mean_case(self):
        filter_conditions_list = ["clear_status", "instance_nonzero", "exclude_nan_classes"]
