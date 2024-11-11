# Standard Library Imports
import logging
import pytest

# Third Part Imports
import pandas as pd
import numpy as np

from unittest.mock import patch

# Local Imports
from src.site_apportionment.site_apportionment import (
    count_unique_postcodes_in_col,
    create_notnull_mask,
    set_percentages,
    split_sites_df,
    deduplicate_codes_values,
    calc_weights_for_sites,
    create_cartesian_product,
    sort_rows_order_cols,
    create_sites_df,
    count_duplicate_sites,
    weight_values,
    create_category_df,
    run_apportion_sites,
)

# Define easier pandas usages
pandasDF = pd.DataFrame
assert_frame_equal = pd._testing.assert_frame_equal
assert_series_equal = pd._testing.assert_series_equal

# Add a new column "period" with a value of "2020" in the third position
@pytest.fixture
def create_input_df():
    """Create an input dataframe for the beginning of the site apportionment module."""
    input_columns = [
        "reference",
        "instance",
        "period",
        "200",
        "201",
        "pg_numeric",
        "formtype",
        "211",
        "251",
        "601",
        "602",
        "status",
        "imp_marker",
        "postcodes_harmonised",
        "itl"
    ]

    data = [
        [111, 0, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [111, 1, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [111, 2, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [222, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP20 6YY", "cym"],
        [222, 1, "2020", "C", "A", 40, "0001", 100, "yes", "CB1 3NF", 60.0, "Clear", "R", "CB1 3NF", "cym"],
        [222, 2, "2020", "D", "ZZ", 80, "0001", 100, "yes", "BA1 5DA", 40.0, "Clear", "R", "BA1 5DA", "cym"],
        [333, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Check needed", "TMI", "NP30 7ZZ", "cym"],
        [333, 1, "2020", "C", "A", 40, "0001", 100, "yes", "DE72 3AU", np.nan, "Check needed", "TMI", "DE72 3AU", "cym"],
        [333, 2, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "No mean found", "NP30 7ZZ", "cym"],
        [444, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "TMI", "CF10 BZZ", "cym"],
        [555, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "No mean found", "SA50 5BE", "cym"],
        # below, the case of short form in previous period and long form in current period
        [666, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        [666, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        [666, 2, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        # as above but status "Form sent out"
        [777, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym"],
        [777, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym"],
        [777, 2, "2020", "D", "XX", 70, "0001", 100, "yes", np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym"],
    ]

    input_df = pandasDF(data=data, columns=input_columns)
    return input_df


@pytest.fixture
def create_exp_postcode_count_output_df():
    """Create a dataframe for expected output of the count_unique_postcodes_in_col function test.

    NOTE: The columns 200, 201, 211, 251 and pg_numeric are dropped from the input before the function is called
    for the sake of simplicity.

    This will also be used as input for the set_percentages function test.
    """
    exp_output_columns = [
        "reference",
        "instance",
        "period",
        "formtype",
        "601",
        "602",
        "status",
        "imp_marker",
        "postcodes_harmonised",
        "itl",
        "601_count"
    ]
    data = [
        [111, 0, "2020", "0006", np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym", np.nan],
        [111, 1, "2020", "0006", np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym", np.nan],
        [111, 2, "2020", "0006", np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym", np.nan],
        [222, 0, "2020", "0001",  np.nan, np.nan, "Clear", "R", "NP20 6YY", "cym", 2.0],
        [222, 1, "2020", "0001",  "CB1 3NF", 60.0, "Clear", "R", "CB1 3NF", "cym", 2.0],
        [222, 2, "2020", "0001",  "BA1 5DA", 40.0, "Clear", "R", "BA1 5DA", "cym", 2.0],
        [333, 0, "2020", "0001",  np.nan, np.nan, "Check needed", "TMI", "NP30 7ZZ", "cym", 1.0],
        [333, 1, "2020", "0001",  "DE72 3AU", np.nan, "Check needed", "TMI", "DE72 3AU", "cym", 1.0],
        [333, 2, "2020", "0001",  np.nan, np.nan, "Check needed", "No mean found", "NP30 7ZZ", "cym", 1.0],
        [444, 1, "2020", "0001",  np.nan, np.nan, "Form sent out", "TMI", "CF10 BZZ", "cym", np.nan],
        [555, 1, "2020", "0001",  np.nan, np.nan, "Form sent out", "No mean found", "SA50 5BE", "cym", np.nan],
        # below, the case of short form in previous period and long form in current period
        [666, 0, "2020", "0001",  np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym", np.nan],
        [666, 1, "2020", "0001",  np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym", np.nan],
        [666, 2, "2020", "0001",  np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym", np.nan],
        # as above but status "Form sent out"
        [777, 0, "2020", "0001",  np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym", np.nan],
        [777, 1, "2020", "0001",  np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym", np.nan],
        [777, 2, "2020", "0001",  np.nan, np.nan, "Form sent out", "MoR", "NP10 5XX", "cym", np.nan],
    ]

    exp_output_df = pandasDF(data=data, columns=exp_output_columns)
    return exp_output_df


@pytest.fixture
def create_exp_percent_test_output_df():
    """Create a dataframe for expected output of the for the set_percentages function test.

    NOTE: The columns 200, 201, 211, 251 and pg_numeric are dropped from the input before the function is called
    for the sake of simplicity.

    This will also be used as input for the split_sites_df function test.
    """
    exp_output_columns = [
        "reference",
        "instance",
        "period",
        "formtype",
        "601",
        "602",
        "601_count",
        "status",
        "imp_marker",
        "postcodes_harmonised",
        "itl"
    ]
    data = [
        [111, 0, "2020", "0006", np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [111, 1, "2020", "0006", np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [111, 2, "2020", "0006", np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
        [222, 0, "2020", "0001",  np.nan, np.nan, 2.0, "Clear", "R", "NP20 6YY", "cym"],
        [222, 1, "2020", "0001",  "CB1 3NF", 60.0, 2.0, "Clear", "R", "CB1 3NF", "cym"],
        [222, 2, "2020", "0001",  "BA1 5DA", 40.0, 2.0, "Clear", "R", "BA1 5DA", "cym"],
        [333, 0, "2020", "0001",  np.nan, np.nan, 1.0, "Check needed", "TMI", "NP30 7ZZ", "cym"],
        [333, 1, "2020", "0001",  "DE72 3AU", 100.0, 1.0, "Check needed", "TMI", "DE72 3AU", "cym"],
        [333, 2, "2020", "0001",  np.nan, np.nan, 1.0, "Check needed", "No mean found", "NP30 7ZZ", "cym"],
        [444, 1, "2020", "0001",  "CF10 BZZ", 100.0, 1.0, "Form sent out", "TMI", "CF10 BZZ", "cym"],
        [555, 1, "2020", "0001",  "SA50 5BE", 100.0, 1.0, "Form sent out", "No mean found", "SA50 5BE", "cym"],
        # below, the case of short form in previous period and long form in current period
        [666, 0, "2020", "0001",  np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        [666, 1, "2020", "0001",  np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        [666, 2, "2020", "0001",  np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
        # as above but status "Form sent out"
        [777, 0, "2020", "0001",  "NP10 5XX", np.nan, 1.0, "Form sent out", "MoR", "NP10 5XX", "cym"],
        [777, 1, "2020", "0001",  "NP10 5XX", 100.0, 1.0, "Form sent out", "MoR", "NP10 5XX", "cym"],
        [777, 2, "2020", "0001",  "NP10 5XX", 100.0, 1.0, "Form sent out", "MoR", "NP10 5XX", "cym"],
    ]

    exp_output_df = pandasDF(data=data, columns=exp_output_columns)
    return exp_output_df

class TestCountUniquePostcodesInCol:
    """Tests for the count_unique_postcodes_in_col function."""

    def test_count_unique_postcodes_in_col(self, create_input_df, create_exp_postcode_count_output_df):
        """Test for the count_unique_postcodes_in_col function."""
        input_df = create_input_df
        input_df = input_df.drop(columns=["200", "201", "pg_numeric", "211", "251"])
        result_df = count_unique_postcodes_in_col(input_df)
        expected_output_df = create_exp_postcode_count_output_df

        assert_frame_equal(result_df[expected_output_df.columns], expected_output_df)

class TestSetPercentages:
    """Tests for the set_percentages function."""

    def test_set_percentage(self, create_exp_percent_test_output_df, create_exp_postcode_count_output_df):
        """Test for the set_percentages function."""
        input_df = create_exp_postcode_count_output_df
        expected_output_df = create_exp_percent_test_output_df

        result_df = set_percentages(input_df)
        assert_frame_equal(result_df[expected_output_df.columns], expected_output_df)


class TestSplitSitesDf:
    """Tests for the split_sites_df function."""

    def create_exp_to_apportion_output(self):
        """Expected output for the to_apportion_df dataframe."""
        exp_output_cols1 = [
            "reference",
            "instance",
            "period",
            "formtype",
            "601",
            "602",
            "601_count",
            "status",
            "imp_marker",
            "postcodes_harmonised",
            "itl"
        ]

        data1 = [
            [222, 1, "2020", "0001",  "CB1 3NF", 60.0, 2.0, "Clear", "R", "CB1 3NF", "cym"],
            [222, 2, "2020", "0001",  "BA1 5DA", 40.0, 2.0, "Clear", "R", "BA1 5DA", "cym"],
            [333, 1, "2020", "0001",  "DE72 3AU", 100.0, 1.0, "Check needed", "TMI", "DE72 3AU", "cym"],
            [333, 2, "2020", "0001",  np.nan, np.nan, 1.0, "Check needed", "No mean found", "NP30 7ZZ", "cym"],
            [444, 1, "2020", "0001",  "CF10 BZZ", 100.0, 1.0, "Form sent out", "TMI", "CF10 BZZ", "cym"],
            [555, 1, "2020", "0001",  "SA50 5BE", 100.0, 1.0, "Form sent out", "No mean found", "SA50 5BE", "cym"],
            [777, 1, "2020", "0001",  "NP10 5XX", 100.0, 1.0, "Form sent out", "MoR", "NP10 5XX", "cym"],
            [777, 2, "2020", "0001",  "NP10 5XX", 100.0, 1.0, "Form sent out", "MoR", "NP10 5XX", "cym"],
        ]

        exp_output_df1 = pandasDF(data=data1, columns=exp_output_cols1)
        return exp_output_df1

    def create_exp_remaining_output(self):
        """Expected output for the df_out dataframe.

        This should contain all the records not in the to_apportion dataframe,
        except those with imp_marker = "No mean found" or "no_imputation"
        """
        exp_output_cols2 = [
            "reference",
            "instance",
            "period",
            "formtype",
            "601",
            "602",
            "601_count",
            "status",
            "imp_marker",
            "postcodes_harmonised",
            "itl"
        ]

        data2 = [
            [111, 0, "2020", "0006", np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
            [111, 1, "2020", "0006", np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
            [111, 2, "2020", "0006", np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym"],
            [222, 0, "2020", "0001",  np.nan, np.nan, 2.0, "Clear", "R", "NP20 6YY", "cym"],
            [333, 0, "2020", "0001",  np.nan, np.nan, 1.0, "Check needed", "TMI", "NP30 7ZZ", "cym"],
            # below, the case of short form in previous period and long form in current period
            [666, 0, "2020", "0001",  np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
            [666, 1, "2020", "0001",  np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
            [666, 2, "2020", "0001",  np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym"],
            # as above but status "Form sent out"
            [777, 0, "2020", "0001",  "NP10 5XX", np.nan, 1.0, "Form sent out", "MoR", "NP10 5XX", "cym"],
        ]
        exp_output_df2 = pandasDF(data=data2, columns=exp_output_cols2)
        exp_output_df2 = exp_output_df2.astype({"601": object})
        return exp_output_df2


    def test_split_sites_df(self, create_exp_percent_test_output_df):
        """Test for the split_sites_df function."""
        input_df = create_exp_percent_test_output_df
        exp_to_apportion_df = self.create_exp_to_apportion_output()
        exp_df_out = self.create_exp_remaining_output()

        imp_markers_to_keep: list = ["R", "TMI", "CF", "MoR", "constructed"]
        result_to_apportion, result_df_out = split_sites_df(
            input_df, imp_markers_to_keep
        )

        assert_frame_equal(
            result_to_apportion.reset_index(drop=True), exp_to_apportion_df
        )

        assert_frame_equal(result_df_out.reset_index(drop=True), exp_df_out)


class TestDeduplicateCodeValues:
    """Tests for the deduplicate_codes_values function."""

    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_columns = [
            "reference",
            "period",
            "200",
            "201",
            "pg_numeric",
            "211",
            "251",
        ]

        data = [
            [111, "2020", "C", "A", 42, 5000.0, "Yes"],
            [111, "2020", "C", "A", 42, 777.0, "No"],
            [111, "2020", "D", "B", 37, 300.0, "Yes"],
            [222, "2020", "C", "A", 61, 1000.0, "Yes"],
            [222, "2020", "C", "A", 63, 500.0, "No"],
        ]

        input_df = pandasDF(data=data, columns=input_columns)
        return input_df

    def create_exp_output_df(self):
        """Create an input dataframe for the test."""
        exp_output_columns = [
            "reference",
            "period",
            "200",
            "201",
            "pg_numeric",
            "211",
            "251",
        ]

        data = [
            [111, "2020", "C", "A", 42, 5777.0, "Yes"],
            [111, "2020", "D", "B", 37, 300.0, "Yes"],
            [222, "2020", "C", "A", 61, 1000.0, "Yes"],
            [222, "2020", "C", "A", 63, 500.0, "No"],
        ]

        exp_output_df = pandasDF(data=data, columns=exp_output_columns)
        return exp_output_df

    def test_deduplicate_codes_values(self):
        """Test for the deduplicate_codes_values function."""
        input_df = self.create_input_df()
        exp_df = self.create_exp_output_df()

        result_df = deduplicate_codes_values(
            input_df,
            ["reference", "period", "200", "201", "pg_numeric"],
            ["211"],
            ["251"],
        )

        assert_frame_equal(result_df.reset_index(drop=True), exp_df)


class TestCalcWeightsForSites:
    """Tests for the calc_weights_for_sites function."""

    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_columns = [
            "reference",
            "period",
            "instance",
            "601",
            "602",
            "postcodes_harmonised",
        ]

        data = [
            [111, "2020", 1, "AB15 3GU", 0.0, "AB15 3GU"],
            [111, "2020", 2, "BA1 5DA", 0.0, "BA1 5DA"],
            [222, "2020", 1, "CB1 3NF", 60.0, "CB1 3NF"],
            [222, "2020", 2, "DE72 3AU", 40.0, "BA1 5DA"],
            [333, "2020", 1, "EH10 7DZ", 10.0, "DE72 3AU"],
            [333, "2020", 2, "FL27 3DE", 20.0, "NP30 7ZZ"],
            [333, "2020", 3, "GL14 1DD", 50.0, "CF10 BZZ"],
            [333, "2020", 4, "GP15 3XX", np.nan, "CF10 BZZ"],
            [444, "2020", 1, "HA3 2BE", 100.0, "SA50 5BE"],
            [555, "2020", 1, "IP24 8XX", 100.0, "IP24 8XX"],
        ]

        input_df = pandasDF(data=data, columns=input_columns)
        return input_df

    def create_exp_output_df(self):
        """Create an input dataframe for the test."""
        exp_output_columns = [
            "reference",
            "period",
            "instance",
            "601",
            "602",
            "postcodes_harmonised",
            "site_weight",
        ]

        data = [
            [222, "2020", 1, "CB1 3NF", 60.0, "CB1 3NF", 0.6],
            [222, "2020", 2, "DE72 3AU", 40.0, "BA1 5DA", 0.4],
            [333, "2020", 1, "EH10 7DZ", 10.0, "DE72 3AU", 0.125],
            [333, "2020", 2, "FL27 3DE", 20.0, "NP30 7ZZ", 0.25],
            [333, "2020", 3, "GL14 1DD", 50.0, "CF10 BZZ", 0.625],
            [333, "2020", 4, "GP15 3XX", np.nan, "CF10 BZZ", 0.0],
            [444, "2020", 1, "HA3 2BE", 100.0, "SA50 5BE", 1.0],
            [555, "2020", 1, "IP24 8XX", 100.0, "IP24 8XX", 1.0],
        ]

        exp_output_df = pandasDF(data=data, columns=exp_output_columns)
        return exp_output_df

    def test_calc_weights_for_sites(self):
        """Test for the cacl_weights_for_sites function."""
        input_df = self.create_input_df()
        exp_df = self.create_exp_output_df()

        result_df = calc_weights_for_sites(input_df, ["reference", "period"])

        assert_frame_equal(result_df.reset_index(drop=True), exp_df)


class TestCreateCartesianProduct:
    """Tests for the create_cartesian_product function."""

    def create_sites_input_df(self):
        """Create an input dataframe for the test."""
        sites_input_columns = [
            "reference",
            "period",
            "instance",
            "601",
            "602",
            "postcodes_harmonised",
            "site_weights",
        ]

        sites_data = [
            [222, "2020", 1, "CB1 3NF", 60, "CB1 3NF", 0.6],
            [222, "2020", 2, "DE72 3AU", 40, "DE72 3AU", 0.4],
            [222, "2021", 1, "CB1 3NF", 70, "CB1 3NF", 0.7],
            [222, "2021", 2, "DE72 3AU", 30, "DE72 3AU", 0.3],
            [333, "2020", 1, "EH10 7DZ", 10, "EH10 7DZ", 0.125],
            [333, "2020", 2, "FL27 3DE", 20, "FL27 3DE", 0.25],
            [333, "2020", 3, "GL14 1DD", 50, "GL14 1DD", 0.625],
            [444, "2020", 1, "HA3 2BE", 100, "HA3 2BE", 1.0],
            [555, "2020", 1, "IP24 8XX", 100, "IP24 8XX", 1.0],
        ]

        sites_input_df = pandasDF(data=sites_data, columns=sites_input_columns)
        return sites_input_df

    def create_category_input_df(self):
        """Create an input dataframe for the test."""
        category_input_columns = [
            "reference",
            "period",
            "200",
            "201",
            "pg_numeric",
            "211",
        ]

        category_data = [
            [111, "2020", "C", "AA", 34, 3000],
            [111, "2020", "C", "A", 42, 5700],
            [111, "2020", "D", "B", 37, 2000],
            [222, "2020", "C", "A", 61, 1000],
            [222, "2020", "C", "A", 63, 500],
            [222, "2021", "C", "A", 61, 2000],
            [333, "2020", "C", "E", 24, 100],
            [444, "2020", "D", "F", 31, 240],
        ]

        category_input_df = pandasDF(data=category_data, columns=category_input_columns)
        return category_input_df

    def create_exp_output_df(self):
        """Create an input dataframe for the test."""
        exp_output_columns = [
            "reference",
            "period",
            "instance",
            "601",
            "602",
            "postcodes_harmonised",
            "site_weights",
            "200",
            "201",
            "pg_numeric",
            "211",
        ]

        data = [
            [222, "2020", 1, "CB1 3NF", 60, "CB1 3NF", 0.6, "C", "A", 61, 1000],
            [222, "2020", 1, "CB1 3NF", 60, "CB1 3NF", 0.6, "C", "A", 63, 500],
            [222, "2020", 2, "DE72 3AU", 40, "DE72 3AU", 0.4, "C", "A", 61, 1000],
            [222, "2020", 2, "DE72 3AU", 40, "DE72 3AU", 0.4, "C", "A", 63, 500],
            [222, "2021", 1, "CB1 3NF", 70, "CB1 3NF", 0.7, "C", "A", 61, 2000],
            [222, "2021", 2, "DE72 3AU", 30, "DE72 3AU", 0.3, "C", "A", 61, 2000],
            [333, "2020", 1, "EH10 7DZ", 10, "EH10 7DZ", 0.125, "C", "E", 24, 100],
            [333, "2020", 2, "FL27 3DE", 20, "FL27 3DE", 0.25, "C", "E", 24, 100],
            [333, "2020", 3, "GL14 1DD", 50, "GL14 1DD", 0.625, "C", "E", 24, 100],
            [444, "2020", 1, "HA3 2BE", 100, "HA3 2BE", 1.0, "D", "F", 31, 240],
        ]

        exp_output_df = pandasDF(data=data, columns=exp_output_columns)
        return exp_output_df

    def test_create_cartesian_product(self):
        """Test for the create_cartesian_product function."""
        category_input_df = self.create_category_input_df()
        sites_input_df = self.create_sites_input_df()

        exp_output_df = self.create_exp_output_df()

        result_df = create_cartesian_product(sites_input_df, category_input_df)

        assert_frame_equal(result_df.reset_index(drop=True), exp_output_df)


class TestCreateNotnullMask:
    """Tests for the function create_not_null_mask."""

    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_columns = ["reference", "col"]

        data = [
            [0, 1],
            [111, "a"],
            [222, ""],
            [333, pd.NA],
            [444, np.nan],
            [555, " "],
        ]

        input_df = pandasDF(data=data, columns=input_columns)
        return input_df

    def test_create_notnull_mask(self):
        """Test for create_notnull_mask function."""
        self.input_df = self.create_input_df()

        exp_output = pd.Series([False, True, False, False, False, True], name="col")

        result = create_notnull_mask(self.input_df, "col")
        assert_series_equal(result, exp_output)

    def create_demo_expected_df(self):
        """Create an input dataframe to show how other nulls work."""
        expected_columns = [
            "reference",
            "col",
            "this_test",
            "flag_is_null",
            "flag_is_emty",
            "flag_is_notnull",
            "flag_not_is_null",
            "len",
            "flag_length_greater_than_zero",
        ]

        data = [
            [0, 1, False, np.nan, np.nan, True, True, np.nan, np.nan],
            [111, "a", True, np.nan, np.nan, True, True, 1.0, True],
            [222, "", False, np.nan, True, True, True, 0.0, np.nan],
            [333, pd.NA, False, True, np.nan, np.nan, np.nan, np.nan, np.nan],
            [444, np.nan, False, True, np.nan, np.nan, np.nan, np.nan, np.nan],
            [555, " ", True, np.nan, np.nan, True, True, 1.0, True],
        ]

        expected_df = pandasDF(data=data, columns=expected_columns)
        return expected_df

    def test_other_nulls_demo(self):
        """Demonstrate how this function works and compare with other tests for null.

        The column under test has the following values:
        [111, "a", "", pd.NA, np.nan, " "]
        """
        demo_df = self.create_input_df()

        # here's the original test again
        result = create_notnull_mask(demo_df, "col")
        exp_output = pd.Series([False, True, False, False, False, True], name="col")
        assert_series_equal(result, exp_output)

        # test the effect of apply applying .isnull() to column col
        result_not_isnull = ~demo_df["col"].isnull()
        # note that "" does not register as null
        exp_isnull = pd.Series([True, True, True, False, False, True], name="col")
        assert_series_equal(result_not_isnull, exp_isnull)

        # test the effect of apply applying .notnull() to column col
        result_notnull = demo_df["col"].notnull()
        # note that "" registers as not null
        exp_notnull = pd.Series([True, True, True, False, False, True], name="col")
        assert_series_equal(result_notnull, exp_notnull)

        # test applying str.len() to column col
        result_len = demo_df["col"].str.len()
        exp_len = pd.Series([np.nan, "a", "", pd.NA, np.nan, " "], name="col")

        actual_len = pd.Series([np.nan, 1, 0, pd.NA, np.nan, 1], name="col")
        assert_series_equal(result_len, actual_len, check_dtype=False)

    def test_other_nulls_dataframe_demo(self):
        """Dataframe visualisation of tests for nulls.

        The column under test has the following values:
        [111, "a", "", pd.NA, np.nan, " "]
        """
        # set up an input dataframe
        demo_df = self.create_input_df()

        # create new mask columns in demo_df for various null-checking functions
        demo_df.loc[demo_df["col"].isnull(), "flag_is_null"] = True
        demo_df.loc[demo_df["col"] == "", "flag_is_emty"] = True
        demo_df.loc[demo_df["col"].notnull(), "flag_is_notnull"] = True
        demo_df.loc[~demo_df["col"].isnull(), "flag_not_is_null"] = True
        demo_df["len"] = demo_df["col"].str.len()
        demo_df.loc[demo_df["len"] > 0, "flag_length_greater_than_zero"] = True

        # create the expected dataframe for these operations
        expected_columns = [
            "reference",
            "col",
            "flag_is_null",
            "flag_is_emty",
            "flag_is_notnull",
            "flag_not_is_null",
            "len",
            "flag_length_greater_than_zero",
        ]

        data = [
            [0, 1, np.nan, np.nan, True, True, np.nan, np.nan],  # noqa
            [111, "a", np.nan, np.nan, True, True, 1.0, True],  # noqa
            [222, "", np.nan, True, True, True, 0, np.nan],  # noqa
            [333, pd.NA, True, np.nan, np.nan, pd.NA, np.nan, np.nan],  # noqa
            [444, np.nan, True, np.nan, np.nan, np.nan, np.nan, np.nan],  # noqa
            [555, " ", np.nan, np.nan, True, True, 1.0, True],  # noqa
        ]

        expected_df = pandasDF(data=data, columns=expected_columns)
        # expected_df = expected_df.astype({"len": object})

        # test that the operations in this function give the expected output
        assert_frame_equal(demo_df, expected_df, check_dtype=False)


class TestSortRowsOrderCols:
    def create_input_df(self):
        """Create an input dataframe for the test."""

        input_columns = [
            "instance",
            "Forth",
            "reference",
            "Remove",
            "period",
        ]

        data = [
            [2, "X", 3, "test", 22],
            [1, "X", 3, "test", 21],
            [np.nan, "X", 3, "test", 22],
            [2, "Y", 1, "test", 21],
            [1, "X", 1, "test", 22],
            [2, "X", 1, "test", 22],
            [1, "Y", 4, "test", 21],
            [1, "Z", 2, "test", 22],
            [1, "X", 1, "test", 21],
            [3, "Z", 1, "test", 22],
        ]

        input_df = pandasDF(data=data, columns=input_columns)
        return input_df

    def create_output_df(self):
        """Create an output dataframe for the test."""

        output_columns = [
            "reference",
            "period",
            "instance",
            "Forth",
        ]

        data = [
            [1, 21, 1.0, "X"],
            [1, 21, 2.0, "Y"],
            [3, 21, 1.0, "X"],
            [4, 21, 1.0, "Y"],
            [1, 22, 1.0, "X"],
            [1, 22, 2.0, "X"],
            [1, 22, 3.0, "Z"],
            [2, 22, 1.0, "Z"],
            [3, 22, 2.0, "X"],
            [3, 22, np.nan, "X"],
        ]

        expected_df = pandasDF(data=data, columns=output_columns)
        return expected_df

    def test_sort_rows_order_cols(self, caplog):
        """Unit test for sorting rows and ordering cols."""

        cols_in_order = ["reference", "period", "instance", "Forth"]

        input_df = self.create_input_df()
        expected_df = self.create_output_df()

        with caplog.at_level(logging.DEBUG):
            result_df = sort_rows_order_cols(input_df, cols_in_order)

            assert "Removing {'Remove'} from df_cart" in caplog.text
            assert_frame_equal(result_df, expected_df)

    def create_input_df_missing_col(self):
        """Create an input dataframe for missing col test."""

        input_columns = [
            "instance",
            "reference",
            "Remove",
            "period",
        ]

        data = [
            [2, 3, "test", 22],
            [1, 3, "test", 21],
            [np.nan, 3, "test", 22],
            [2, 1, "test", 21],
            [1, 1, "test", 22],
            [2, 1, "test", 22],
            [1, 4, "test", 21],
            [1, 2, "test", 22],
            [1, 1, "test", 21],
            [3, 1, "test", 22],
        ]

        input_missing_col_df = pandasDF(data=data, columns=input_columns)
        return input_missing_col_df

    def test_sort_rows_missing_cols(self, caplog):
        """Unit test for ordering cols with missing col."""

        cols_in_order = ["reference", "period", "instance", "Forth"]

        input_df = self.create_input_df_missing_col()

        with pytest.raises(KeyError):
            sort_rows_order_cols(input_df, cols_in_order)


@pytest.fixture(scope="function")
def sites_df_input():
    """
    Input df for create_sites_df tests.

    This input data consists of:
    1. Columns that will be dropped
    2. NaN's in used columns (601, 602)
    3. Combinations of Postcodes/Periods/References to create multiple groups
    """
    input_cols = [
        "reference",
        "instance",
        "period",
        "601",
        "602",
        "601_count",
        "status",
        "imp_marker",
        "postcodes_harmonised",
        "itl"
    ]
    input_data = [
        [111, 1, "2020", "RH12 1XL", 100.0, np.nan, "Clear", "R", "RH12 1XL", "cym"],
        [111, 2, "2020", "RH12 1XL", 125.0, np.nan, "Clear", "R", "RH12 1XL", "cym"],
        [111, 3, "2020", "RH12 1XL", np.nan, np.nan, "Clear", "R", "RH12 1XL", "cym"],  # Nan 602 - Ensure conv to 0
        [111, 4, "2020", "RH12 1XZ", 100.0, np.nan, "Clear", "R", "RH12 1XZ", "cym"],  # different postcode
        [222, 1, "2020", "NP44 2NZ", np.nan, 2.0, "Clear", "R", "NP44 2NZ", "cym"],
        [222, 2, "2020", "NP44 2NZ", 50.0, 2.0, "Clear", "R", "NP44 2NZ", "cym"],
        [333, 1, "2020", np.nan, np.nan, 1.0, "Check needed", "TMI", "NP30 7ZZ", "cym"],  # NaN 601 - Ensure dropped
    ]
    input_df = pandasDF(data=input_data, columns=input_cols)

    return input_df


class TestCreateSitesDf(object):
    """Tests for create_sites_df."""

    @pytest.fixture(autouse=True)
    def set_attrs(self):
        """Set class attributes that are passed as parameters."""
        self.groupby_cols = ["reference", "period"]
        self.site_cols = ["instance", "601", "602", "postcodes_harmonised"]
        self.geo_cols = ["itl"]

    def test_create_sites_df_on_pass(self, sites_df_input):
        """General tests for create_sites_df."""
        output = create_sites_df(sites_df_input, self.groupby_cols, self.site_cols, self.geo_cols)
        print(output)
        # assert the resultant dataframe is as expected
        exp_columns = [
            "reference",
            "instance",
            "period",
            "601",
            "postcodes_harmonised",
            "itl",
            "602",
        ]
        exp_data = [
            [111, 1, "2020", "RH12 1XL", "RH12 1XL", "cym", 225.0],
            [111, 4, "2020", "RH12 1XZ", "RH12 1XZ", "cym", 100.0],
            [222, 1, "2020", "NP44 2NZ", "NP44 2NZ", "cym", 50.0],
        ]
        expected = pandasDF(data=exp_data, columns=exp_columns)
        assert_frame_equal(output[expected.columns], expected)


class TestCountDuplicateSites(object):
    """Tests for count_duplicate_sites."""

    def test_count_duplicate_sites_on_pass(self, caplog, sites_df_input):
        """General tests for count_duplicate_sites."""
        # set log level
        caplog.set_level(logging.INFO)
        count_duplicate_sites(sites_df_input)
        # parse logs and assert
        log_records = [record.msg for record in caplog.records]
        expected_log_message = "There are 2 duplicate sites."
        assert (
            log_records[0] == expected_log_message
        ), "Duplicate sites not added to logger at level INFO."


class TestWeightValues(object):
    """Tests for weight_values."""

    @pytest.fixture(scope="function")
    def weight_values_test_df(self):
        """Test data for weight_values."""
        columns = ["reference", "val_col_1", "val_col_2", "weight_col"]
        data = [
            [0, 10, 3.5, 1.5],
            [111, 14, 4.5, 1.5],
            [222, 16, 10, 1.0],
            [333, 18.0, np.nan, 2.0],
            [444, 6, 0, 3.0],
        ]
        return pandasDF(data=data, columns=columns)

    @pytest.fixture(autouse=True)
    def set_attrs(self):
        """Set class attributes to pass to function."""
        self.value_cols = ["val_col_1", "val_col_2"]
        self.weight_col = "weight_col"

    def test_weight_values_on_pass(self, weight_values_test_df):
        """General tests for weight_values."""
        output = weight_values(weight_values_test_df, self.value_cols, self.weight_col)

        columns = ["reference", "val_col_1", "val_col_2", "weight_col"]

        data = [
            [0, 15.0, 5.25, 1.5],
            [111, 21.0, 6.75, 1.5],
            [222, 16.0, 10.0, 1.0],
            [333, 36.0, np.nan, 2.0],
            [444, 18.0, 0.0, 3.0],
        ]
        exp_out = pandasDF(data=data, columns=columns)
        assert output.equals(exp_out), "weight_values not acting as expected."


class TestCreateCategoryDf(object):
    """Tests for create_category_df."""

    @pytest.fixture(scope="function")
    def category_df_input(self):
        """Test data for create_category_df."""
        columns = [
            "reference",
            "instance",
            "period",
            "imp_marker",
            "201",
            "200",
            "pg_numeric",
            "601",
            "602",
            "210",
        ]

        # data includes:

        data = [
            [49900000404, 0, 202212, "R", "AA", np.nan, np.nan, np.nan, 100.0, np.nan],
            [49900000404, 1, 202212, "R", "AA", "C", 29, np.nan, 100.0, 243600.0379],
            [49900000404, 2, 202212, "R", "AA", "D", 29, np.nan, 100.0, 0.0],
            [49900000408, 0, 202212, "R", "I", np.nan, 32, np.nan, 100.0, np.nan],  # group code nan (dropped)
            [49900000408, 1, 202212, "R", "AA", "C", 33, np.nan, 100.0, 0.0],
            [49900000407, 2, 202212, "test", "AA", "D", np.nan, np.nan, 100.0, 0.0],  # bad imp marker
            [49900000576, 1, 202212, "TMI", "AA", "C", np.nan, np.nan, np.nan, 0.0],
            [49900000960, 0, 202212, "R", "AA", np.nan, 1, np.nan, np.nan, np.nan],
            [49900000960, 1, 202212, "R", "AA", "C", 23, np.nan, np.nan, np.nan],
            [49900001029, 1, 202212, "TMI", "I", "C", 5, np.nan, np.nan, 833.3333],
        ]

        return pd.DataFrame(data=data, columns=columns)

    @pytest.fixture(autouse=True)
    def set_attrs(self):
        """Set class attributes to pass to functions for testing."""
        self.imp_markers_to_keep = ["R", "TMI", "CF", "MoR", "constructed"]
        self.groupby_cols = ["reference", "period"]
        self.code_cols = ["201", "200", "pg_numeric"]
        # excluding postcode_harmonised as it is irrelevant to this test
        self.site_cols = ["instance", "601", "602"]
        self.geo_cols = ["itl"]
        self.value_cols = ["210"]

    def test_create_category_df_on_pass(self, category_df_input):
        """General tests for create_category_df."""
        output = create_category_df(
            category_df_input,
            self.imp_markers_to_keep,
            category_df_input.columns,
            self.groupby_cols,
            self.code_cols,
            self.site_cols,
            self.geo_cols,
            self.value_cols,
        )
        exp_cols = [
            "reference",
            "period",
            "201",
            "200",
            "pg_numeric",
            "210",
            "imp_marker",
        ]
        exp_data = [
            [49900000404, 202212, "AA", "C", 29.0, 243600.0379, "R"],
            [49900000404, 202212, "AA", "D", 29.0, 0.0000, "R"],
            [49900000408, 202212, "AA", "C", 33.0, 0.0000, "R"],
            [49900000960, 202212, "AA", "C", 23.0, 0.0000, "R"],
            [49900001029, 202212, "I", "C", 5.0, 833.3333, "TMI"],
        ]
        expected = pandasDF(data=exp_data, columns=exp_cols)
        assert output.equals(expected), "create_category_df not acting as expected"

    def test_create_category_df_drops_duplicates(self, category_df_input):
        """Test that create_category_df de-duplicates."""
        # reduce input data to the first four rows
        category_df_input = category_df_input.loc[:3]
        # add duplicate row and pass to create_category_df
        output = create_category_df(
            category_df_input.append(category_df_input.iloc[0]),
            self.imp_markers_to_keep,
            category_df_input.columns,
            self.groupby_cols,
            self.code_cols,
            self.site_cols,
            self.geo_cols,
            self.value_cols,
        )
        exp_cols = [
            "reference",
            "period",
            "201",
            "200",
            "pg_numeric",
            "210",
            "imp_marker",
        ]
        exp_data = [
            [49900000404, 202212, "AA", "C", 29.0, 243600.0379, "R"],
            [49900000404, 202212, "AA", "D", 29.0, 0.0000, "R"],
        ]
        expected = pandasDF(data=exp_data, columns=exp_cols)
        assert output.equals(expected), "Duplicates not dropped by create_category_df."


class TestRunApportionSites(object):
    """Tests for run_apportion_sites."""

    def create_exp_output_df(self):
        """Create a dataframe for the expected output of the apportionment module."""
        exp_output_cols = [
            "reference",
            "instance",
            "period",
            "200",
            "201",
            "pg_numeric",
            "formtype",
            "211",
            "251",
            "601",
            "602",
            "status",
            "imp_marker",
            "postcodes_harmonised",
            "itl",
            "itl2",
        ]

        data = [
            [111, 0, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym", "eng"],
            [111, 1, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym", "eng"],
            [111, 2, "2020", "C", "A", 40, "0006", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP10 5XX", "cym", "eng"],
            [222, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Clear", "R", "NP20 6YY", "cym", "eng"],
            # the following 4 rows are the ones that have been apportioned
            [222, 1, "2020", "C", "A", 40, "0001", 60, "yes", "CB1 3NF", 60.0, "Clear", "R", "CB1 3NF", "cym", "eng"],
            [222, 1, "2020", "D", "ZZ", 80, "0001", 60, "yes", "CB1 3NF", 60.0, "Clear", "R", "CB1 3NF", "cym", "eng"],
            [222, 2, "2020", "C", "A", 40, "0001", 40, "yes", "BA1 5DA", 40.0, "Clear", "R", "BA1 5DA", "cym", "eng"],
            [222, 2, "2020", "D", "ZZ", 80, "0001", 40, "yes", "BA1 5DA", 40.0, "Clear", "R", "BA1 5DA", "cym", "eng"],
            [333, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Check needed", "TMI", "NP30 7ZZ", "cym", "eng"],
            [333, 1, "2020", "C", "A", 40, "0001", 100, "yes", "DE72 3AU", 100.0, "Check needed", "TMI", "DE72 3AU", "cym", "eng"],
            [444, 1, "2020", "C", "A", 40, "0001", 100, "yes", "CF10 BZZ", 100.0, "Form sent out", "TMI", "CF10 BZZ", "cym", "eng"],
            [666, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym", "eng"],
            [666, 1, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym", "eng"],
            [666, 2, "2020", "C", "A", 40, "0001", 100, "yes", np.nan, np.nan, "Check needed", "MoR", "NP10 5XX", "cym", "eng"],
            [777, 0, "2020", "C", "A", 40, "0001", np.nan, np.nan, "NP10 5XX", np.nan, "Form sent out", "MoR", "NP10 5XX", "cym", "eng"],
            [777, 1, "2020", "C", "A", 40, "0001", 100, "yes", "NP10 5XX", 200.0, "Form sent out", "MoR", "NP10 5XX", "cym", "eng"],
            [777, 1, "2020", "D", "XX", 70, "0001", 100, "yes", "NP10 5XX", 200.0, "Form sent out", "MoR", "NP10 5XX", "cym", "eng"],
        ]

        exp_output_df = pandasDF(data=data, columns=exp_output_cols)
        return exp_output_df


    def test_run_apportion_sites(self, create_input_df):
        """General tests for run_apportion_sites."""
        input_df = create_input_df
        input_df["itl2"] = "eng"

        exp_output_df = self.create_exp_output_df()

        config = {
            "mappers": {"geo_cols": ["itl2"]},
            "breakdowns": {"211": []},
            "imputation": {"sum_cols": ["211"], "impute_cols": ["211"]},
        }
        imp_markers_to_keep: list = ["R", "TMI", "CF", "MoR"]

        # we will mock the function consistency_checks for simplicity
        with patch("src.site_apportionment.site_apportionment.consistency_checks") as mock_consistency_checks:
            mock_consistency_checks.return_value = True

            results_df = run_apportion_sites(input_df, imp_markers_to_keep, config, intram_tot_dict={})

        assert_frame_equal(results_df, exp_output_df)
