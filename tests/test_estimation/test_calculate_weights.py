"""Tests for functions in calculate_weights"""

import pandas as pd
import numpy as np
import logging
import pytest
import src.estimation.calculate_weights as calw
from pandas._testing import assert_frame_equal, assert_series_equal


class TestCreateEstimationFilter:
    """Test for create_estimation_filter."""

    def create_input_df(self):
        """Create input df for test."""
        input_cols = [
            "reference",
            "instance",
            "709",
            "selectiontype",
            "status",
            "formtype",
            "cellnumber",
            "uni_count",
            "outlier",
        ]

        data = [
            [1, 0, "12", "P", "Clear", "0006", 1, 20, True],
            [2, 0, 14, "P", "Clear - overridden", "0006", 2, 4, False],
            [2, 1, 16, "P", "Clear", "0006", 2, 4, False],
            [4, 0, 18, "P", "Clear", "0006", 4, 3, False],
            [1, 0, "20", "X", "Clear", "0006", 5, 10, False],
            [3, 0, 1, "P", "999", "0006", 1, 20, False],
            [5, 0, 14, "P", "Clear - overridden", "0001", 2, 4, False],
            [6, 0, 10, "P", "Clear", "0006", 1, 20, False],
            [7, 1, 10, "P", "Clear", "0006", 5, 10, False],
            [8, 1, np.nan, "P", "Clear", "0006", 2, 4, False],
            [9, 0, 5, "P", "Clear", "0006", 1, 20, False],
            [10, 0, 10, "P", "Clear", "0006", 1, 20, False],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def create_expected_output(self):
        """Create expected output boolean series for test"""
        expected_output = pd.Series(
            [True, True, False, True, False, False, False, True, False, False, True, True]
        )
        return expected_output

    def test_create_estimation_filter(self):
        """Test for create_estimation_filter."""
        input_df = self.create_input_df()
        expected_output = self.create_expected_output()

        actual_output = calw.create_estimation_filter(input_df)

        assert_series_equal(actual_output, expected_output)


class TestCalcLowerNDuplicateRefs:
    """Test for calc_lower_n with duplicate refs."""

    def create_input_df(self):
        """Creates input df for test"""
        input_cols = [
            "reference",
            "709",
        ]
        data = [
            [1, "A"],
            [2, "B"],
            [2, "C"],
            [4, "D"],
            [1, "E"],
            [4, np.nan]
        ]
        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def test_calc_lower_n(self):
        """Test for calc_lower_n with duplicate refs."""

        input_df = self.create_input_df()
        # Call calc_lower_n function
        actual_result = calw.calc_lower_n(input_df)
        # Defined expected result
        expected_result = 3
        assert actual_result == expected_result, "calc_lower_n not behaving as expected"


class TestCalcLowerNDuplicateRefs:
    """Test for calc_lower_n with duplicate refs."""

    def create_input_df(self):
        """Creates input df for test"""
        input_cols = [
            "reference",
            "709",
        ]
        data = [
            [1, "A"],
            [2, "B"],
            [2, "C"],
            [4, "D"],
            [1, "E"],
            [4, np.nan]
        ]
        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def test_calc_lower_n(self):
        """Test for calc_lower_n with duplicate refs."""

        input_df = self.create_input_df()
        # Call calc_lower_n function
        actual_result = calw.calc_lower_n(input_df)
        # Defined expected result
        expected_result = 3
        assert actual_result == expected_result, "calc_lower_n not behaving as expected"

class TestCalcLowerNRefNan:
    """Test for calc_lower_n with nan in reference."""

    def create_input_df(self):
        """Creates input df for test"""
        input_cols = [
            "reference",
            "709",
        ]

        data = [
            [1, "A"],
            [2, "B"],
            [np.nan, "C"],
            [4, "D"],
            [1, "E"],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def test_calc_lower_n_nan_ref(self):
        """Test for calc_lower_n with nan in reference."""

        input_df = self.create_input_df()

        # Call calc_lower_n function
        actual_result = calw.calc_lower_n(input_df)

        # Defined expected result
        expected_result = 3

        assert actual_result == expected_result, "calc_lower_n not behaving as expected"

class TestCalcLowerE:
    """Test for calc_lower_e with nan."""
    def create_input_df(self):
        """Creates input df for test"""

        input_cols = [
            "employment",
            "711"]
        data = [
            [1, 10],
            [2, 5],
            [2, np.nan],
            [4, np.nan],
            [1, 10],
            [4, np.nan],
        ]
        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def test_calc_lower_e(self):
        """Test for calc_lower_e with nan."""

        input_df = self.create_input_df()
        expected_result = 14

        # Call calc_lower_e function
        actual_result = calw.calc_lower_e(input_df)
        assert actual_result == expected_result, "calc_lower_e not behaving as expected"

class TestCalcLowerS:
    """Test for calc_lower_s"""
    def create_input_df(self):
        """Creates input dataframe"""
        cols =['reference', 'cellnumber', 'employment', 'outlier']
        data =[[1, 22, 100, False],
               [2, 22, 10, False],
               [3, 22, 5, False],
               [4, 8, 60, False],
               [5, 8, 45, True],
               [6, 8, 100, True]]
        input_df = pd.DataFrame(data=data, columns=cols)
        return input_df

    def test_calc_lower_s(self):
        """Test for lower_s calculation"""

        input_df = self.create_input_df()
        # Call calc_lower_s function
        actual_result = calw.calc_lower_s(input_df)
        # Define expected result
        expected_result = 145
        assert actual_result == expected_result, "calc_lower_s not behaving as expected"


class TestCalcLowerSNoOutliers:
    """Test to check if calc_lower_s returns 0 when there are no outliers"""
    def create_input_df(self):
        """Creates input dataframe"""
        cols = ['reference', 'cellnumber', 'employment', 'outlier']
        data = [[1, 22, 100, False],
                [2, 22, 10, False],
                [3, 22, 5, False],
                [4, 8, 60, False],
                [5, 8, 45, False],
                [6, 8, 100, False]]
        input_df = pd.DataFrame(data=data, columns=cols)
        return input_df

    def test_calc_lower_s_emptydf_(self):
        """Test for lower_s calculation"""

        input_df = self.create_input_df()
        # Call calc_lower_s function
        actual_result = calw.calc_lower_s(input_df)
        # Define expected result
        expected_result = 0
        assert actual_result == expected_result, "calc_lower_s not behaving as expected"



# Five tests for calculate_weighting_factors:
# testing calculate_weighting_factors where missing outlier col
# testing calculate_weighting_factors filter
# testing calculate_weighting_factors 709 to numeric with no missing vals
# testing calculate_weighting_factors 709 to numeric with missing vals
# testing calculate_weighting_factors with missing vals
class TestCalcWeightMissingCol:
    """Test for calculate_weighting_factors with missing outlier col"""

    def create_input_df(self):
        """Creates input df for test"""
        input_cols = [
            "reference",
            "709",
        ]

        data = [
            [1, "A"],
            [2, "B"],
            [2, "C"],
            [4, "D"],
            [1, "E"],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def test_calculate_weighting_factors_missing_col(self):
        """Test for calculate_weighting_factors with missing outlier col"""
        input_df = self.create_input_df()

        with pytest.raises(
            ValueError, match=r"The column essential 'outlier' is missing"
        ):
            calw.calculate_weighting_factors(input_df)


class TestCalcWeightFactor:
    """Test for calculate_weighting_factors for filter
    and np.nan taken out of calculation"""

    def create_input_df(self):
        """Creates input df for test"""
        input_cols = [
            "reference",
            "instance",
            "709",
            "selectiontype",
            "status",
            "formtype",
            "cellnumber",
            "uni_count",
            "uni_employment",
            "employment",
            "outlier",
        ]

        data = [
            [1, 0, "12", "P", "Clear", "0006", 1, 20, 5000, 66, True],
            [2, 0, 14, "P", "Clear - overridden", "0006", 2, 4, 5000, 77, False],
            [2, 1, 16, "P", "Clear", "0006", 2, 4, 5000, 77, False],
            [4, 0, 18, "P", "Clear", "0006", 4, 3, 5000, 88, False],
            [1, 0, "20", "X", "Clear", "0006", 5, 10, 5000, 99, False],
            [3, 0, 1, "P", "999", "0006", 1, 20, 5000, 11, False],
            [5, 0, 14, "P", "Clear - overridden", "0001", 2, 4, 5000, 22, False],
            [6, 0, 10, "P", "Clear", "0006", 1, 20, 5000, 7, False],
            [7, 1, 10, "P", "Clear", "0006", 5, 10, 5000, 7, False],
            [8, 1, np.nan, "P", "Clear", "0006", 2, 4, 5000, 7, False],
            [9, 0, 5, "P", "Clear", "0006", 1, 20, 5000, 44, False],
            [10, 0, 10, "P", "Clear", "0006", 1, 20, 5000, 44, False],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def create_expected_output(self):
        """Creates expected df for test"""
        expected_cols = [
            "reference",
            "instance",
            "cellnumber",
            "formtype",
            "709",
            "selectiontype",
            "status",
            "uni_count",
            "uni_employment",
            "employment",
            "outlier",
            "a_weight",
            "g_weight",
            ]
        data = [
            [1, 0, 1, "0006", "12", "P", "Clear", 20, 5000, 66, True, 6.3, 8.2],
            [2, 0, 2, "0006", 14, "P", "Clear - overridden", 4, 5000, 77, False, 4.0, 16.2],
            [2, 1, 2, "0006", 16, "P", "Clear", 4, 5000, 77, False, 1.0, 1.0],
            [4, 0, 4, "0006", 18, "P", "Clear", 3, 5000, 88, False, 3.0, 18.9],
            [1, 0, 5, "0006", "20", "X", "Clear", 10, 5000, 99, False, 1.0, 1.0],
            [3, 0, 1, "0006", 1, "P", "999", 20, 5000, 11, False, 1.0, 1.0],
            [5, 0, 2, "0001", 14, "P", "Clear - overridden", 4, 5000, 22, False, 1.0, 1.0],
            [6, 0, 1, "0006", 10, "P", "Clear", 20, 5000, 7, False, 6.3, 8.2],
            [7, 1, 5, "0006", 10, "P", "Clear", 10, 5000, 7, False, 1.0, 1.0],
            [8, 1, 2, "0006", np.nan, "P", "Clear", 4, 5000, 7, False, 1.0, 1.0],
            [9, 0, 1, "0006", 5, "P", "Clear", 20, 5000, 44, False, 6.3, 8.2],
            [10, 0, 1, "0006", 10, "P", "Clear", 20, 5000, 44, False, 6.3, 8.2],
        ]
        expected_df = pd.DataFrame(data=data, columns=expected_cols)
        return expected_df

    def create_expected_qa(self):
        """Creates expected qa df for test"""
        expected_qa_cols = [
            "Cell Number",
            "N - uni_count",
            "n - num clear records in cell",
            "o - num outliers in cell",
            "E - uni_employment",
            "e - sum of employment in cell",
            "s - sum of employment outliers in cell",
            "a_weight",
            "g_weight"
        ]

        data = [
            [1, 20, 4, 1, 5000, 161, 66, 6.3, 8.20],
            [2, 4, 1, 0, 5000, 77, 0, 4.0, 16.23],
            [4, 3, 1, 0, 5000, 88, 0, 3.0, 18.93],

        ]

        expected_qa_df = pd.DataFrame(data=data, columns=expected_qa_cols)
        return expected_qa_df

    def test_calculate_weighting_factors_filter(self):
        """Test for calculate_weighting_factors for filter
        and np.nan taken out of calculation"""

        input_df = self.create_input_df()
        expected_df = self.create_expected_output()
        expected_qa_df = self.create_expected_qa()

        result_df, result_qa_df = calw.calculate_weighting_factors(input_df)

        # List of DataFrames and columns to round
        dfs = [result_qa_df, result_df, expected_df, expected_qa_df]
        columns = ["a_weight", "g_weight"]

        # Round specified columns in each DataFrame
        for df in dfs:
            for col in columns:
                df[col] = df[col].round(1)

        # Ensure both DataFrames have the same data type for the "709" column
        result_df["709"] = result_df["709"].astype(float)
        expected_df["709"] = expected_df["709"].astype(float)

        assert_frame_equal(result_df, expected_df, check_exact=False, rtol=0.01, check_dtype=False)
        assert_frame_equal(result_qa_df, expected_qa_df, check_exact=False, rtol=0.01, check_dtype=False)


class TestCalcWeightWithMissingVals:
    """Test for calculate_weighting_factors for filter
    and np.nan taken out of calculation"""

    def create_input_df(self):
        """Creates input df for test"""
        input_cols = [
            "reference",
            "instance",
            "709",
            "selectiontype",
            "status",
            "formtype",
            "cellnumber",
            "uni_count",
            "uni_employment",
            "employment",
            "outlier",
        ]

        data = [
            [1, 0, 12, "P", "Clear", "0006", 1, 20, 2000, 50, True],
            [2, 0, 14, "P", "Clear - overridden", "0006", 2, 4, 2000, 77, False],
            [2, 1, 16, "P", "Clear", "0006", 2, 4, 2000, 77, False],
            [4, 0, 18, "P", "Clear", "0006", 4, 3, 2000, 88, False],
            [1, np.nan, 20, "P", "Clear", "0006", 5, 10, 2000, 99, True],
            [3, 0, np.nan, "P", "Clear - overridden", "0006", 1, 20, 2000, 11, True],
            [5, 0, 14, "P", "Clear - overridden", "0006", 2, 4, 2000, 22, False],
            [6, 0, 10, "P", "Clear", "0006", 1, 20, 2000, 7, False],]

        ]
        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def create_expected_output(self):
        """Creates expected df for test"""
        expected_cols = [
 v          "reference",
            "instance",
            "709",
            "selectiontype",
            "status",
            "formtype",
            "cellnumber",
            "uni_count",
            "uni_employment",
            "employment",
            "outlier",
            "a_weight",
            "g_weight",
        ]
        data = [
            [1, 0, 12, "P", "Clear", "0006", 1, 20, 2000, 50, True, 19.0],
            [2, 0, 14, "P", "Clear - overridden", "0006", 2, 4, 2000, 77, False, 4.0, 3.25],
            [2, 0, 16, "P", "Clear", "0006", 2, 4, 2000, 77, False, 4.0, 3.25],
            [4, 0, 18, "P", "Clear", "0006", 4, 3, 2000, 88, False, 3.0,7.57],
            [1, np.nan, 20, "P", "Clear", "0006", 5, 10, 2000, 99, True, 1.0 1.0],
            [3, 0, np.nan, "P", "Clear - overridden", "0006", 1, 20, 2000, 11, True, 1.0, 1.0],
            [5, 1, 14, "P", "Clear - overridden", "0006", 2, 4, 2000, 22, False, 1.0, 1.0],
            [6, 0, 10, "P", "Clear", "0006", 1, 20, 2000, 7, False, 19.0, 14.66],
            ]

        expected_df = pd.DataFrame(data=data, columns=expected_cols)
        return expected_df

    def create_expected_qa(self):
        """Creates expected qa df for test"""
        expected_qa_cols = [
            "Cell Number",
            "N - uni_count",
            "n - num clear records in cell",
            "o - num outliers in cell",
            "E - uni_employment",
            "e - sum of employment in cell",
            "s - sum of employment outliers in cell",
            "a_weight",
            "g_weight"
        ]

        data = [
            [1.0, 20, 2.0, 1.0, 2000, 57, 50, 19, 14.66],
            [2.0, 4, 1.0, 0.0, 2000, 154, 0, 4.0, 3.25],
            [4.0, 3, 1.0, 0.0, 2000, 88, 0, 3.0, 7.57],
        ]

        expected_qa_df = pd.DataFrame(data=data, columns=expected_qa_cols)
        return expected_qa_df

    def test_calculate_weighting_factors_with_missing_vals(self):
        """Test for calculate_weighting_factors for filter
        and np.nan taken out of calculation"""

        input_df = self.create_input_df()
        expected_df = self.create_expected_output()
        expected_qa_df = self.create_expected_qa()

        result_df, result_qa_df = calw.calculate_weighting_factors(input_df)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.expand_frame_repr", False)
        print(result_qa_df)

        assert_frame_equal(
            result_df, expected_df, check_exact=False, rtol=0.01, check_dtype=False
        )
        assert_frame_equal(
            result_qa_df,
            expected_qa_df,
            check_exact=False,
            rtol=0.01,
            check_dtype=False,
        )


# One tests for outlier_weights:
# test that all appropriate rows are given an a_weight = 1.0


class TestOutlierWeight:
    """Test for outlier_weights."""

    def create_input_df(self):
        """Creates input df for test"""
        input_cols = [
            "reference",
            "outlier",
        ]

        data = [
            [1, True],
            [2, False],
            [2, True],
            [4, True],
            [1, False],
        ]

        input_df = pd.DataFrame(data=data, columns=input_cols)
        return input_df

    def create_expected_output(self):
        """Creates expected df for test"""
        expected_cols = [
            "reference",
            "outlier",
            "a_weight",
            "g_weight"
        ]

        data = [
            [1, True, 1.0, 1.0],
            [2, False, None, None],
            [2, True, 1.0, 1.0],
            [4, True, 1.0, 1.0],
            [1, False, None, None],
        ]

        expected_df = pd.DataFrame(data=data, columns=expected_cols)
        return expected_df

    def test_outlier_weights(self):
        """Test for outlier_weights."""
        input_df = self.create_input_df()
        expected_df = self.create_expected_output()

        result_df = calw.outlier_weights(input_df)
        assert_frame_equal(result_df, expected_df)
