import pytest
import pandas as pd
import numpy as np
from pandas import DataFrame as pandasDF
from pandas._testing import assert_series_equal, assert_frame_equal


from src.utils.filter_helpers import (
    create_mask,
    create_notnull_mask,
    check_cols_in_df,
    get_clear_status_mask,
    get_bad_status_mask,
    get_instance_zero_mask,
    get_instance_nonzero_mask,
    get_no_r_and_d_mask,
    get_postcode_only_mask,
    get_excl_postcode_only_mask,
    get_exclude_nan_classes_mask,
    get_prn_only_mask,
    get_census_only_mask,
    get_longform_only_mask,
    get_shortform_only_mask,
    get_mor_imputed_mask,
    get_not_mor_imputed_mask,
)

@pytest.fixture
def create_input_df():
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
        [111, 0, "nan_A", "CF", np.nan, None, "Yes", "Check needed", "0001", "X"],
        [111, 1, "C_A", "MoR", 1, None, None, "Check needed", "0001", "X"],
        [222, 0, "nan_A", "R", np.nan, None, "No", "Clear", "0001", "C"],
        [222, 1, "C_A", "R", 1, "CB1 2NF", "No", "Clear", "0001", "C"],
        [222, 2, "C_A", "R", np.nan, "BA1 5DA", "No", "Clear", "0001", "C"],
        [333, np.nan, None, "R", np.nan, None, "No", "Form sent out", "0006", "P"],
    ]

    input_df = pd.DataFrame(data=data, columns=input_cols)
    return input_df


def test_clear_status_mask(create_input_df):
    expected_mask = pd.Series([False, False, True, True, True, False])
    result_mask = get_clear_status_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_bad_status_mask(create_input_df):
    expected_mask = pd.Series([True, True, False, False, False, True])
    result_mask = get_bad_status_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_instance_zero_mask(create_input_df):
    expected_mask = pd.Series([True, False, True, False, False, False])
    result_mask = get_instance_zero_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_instance_nonzero_mask(create_input_df):
    expected_mask = pd.Series([False, True, False, True, True, False])
    result_mask = get_instance_nonzero_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_no_r_and_d_mask(create_input_df):
    expected_mask = pd.Series([False, False, True, True, True, True])
    result_mask = get_no_r_and_d_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_postcode_only_mask(create_input_df):
    expected_mask = pd.Series([False, False, False, False, True, False])
    result_mask = get_postcode_only_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_excl_postcode_only_mask(create_input_df):
    expected_mask = pd.Series([True, True, True, True, False, True])
    result_mask = get_excl_postcode_only_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_exclude_nan_classes_mask(create_input_df):
    expected_mask = pd.Series([False, True, False, True, True, True])
    result_mask = get_exclude_nan_classes_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_prn_only_mask(create_input_df):
    expected_mask = pd.Series([False, False, False, False, False, True])
    result_mask = get_prn_only_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_census_only_mask(create_input_df):
    expected_mask = pd.Series([False, False, True, True, True, False])
    result_mask = get_census_only_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_longform_only_mask(create_input_df):
    expected_mask = pd.Series([True, True, True, True, True, False])
    result_mask = get_longform_only_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_shortform_only_mask(create_input_df):
    expected_mask = pd.Series([False, False, False, False, False, True])
    result_mask = get_shortform_only_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_get_mor_imputed_mask(create_input_df):
    expected_mask = pd.Series([True, True, False, False, False, False])
    result_mask = get_mor_imputed_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


def test_get_not_mor_imputed_mask(create_input_df):
    expected_mask = pd.Series([False, False, True, True, True, True])
    result_mask = get_not_mor_imputed_mask(create_input_df)
    assert_series_equal(result_mask, expected_mask, check_names=False)


class TestCreateNotNullMask:
    """Unit tests for create_notnull_mask function."""
    def test_create_notnull_mask(self, create_input_df):
        expected_mask = pd.Series([True, True, True, True, True, False])
        result_mask = create_notnull_mask(create_input_df, "imp_class")
        assert_series_equal(result_mask, expected_mask, check_names=False)


class TestCreateMask:
    """Unit tests for create_mask function."""
    def test_clear_status_mask(self, create_input_df):
        df = create_input_df
        options = ["clear_status"]
        expected_mask = pd.Series([False, False, True, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask, check_names=False)

    def test_excl_postcode_only(self, create_input_df):
        df = create_input_df
        options = ["excl_postcode_only"]
        expected_mask = pd.Series([True, True, True, True, False, True])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask, check_names=False)

    def test_clear_instance_zero(self, create_input_df):
        df = create_input_df
        options = ["clear_status", "instance_zero"]
        expected_mask = pd.Series([False, False, True, False, False, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask, check_names=False)

    def test_clear_instance_nonzero(self, create_input_df):
        df = create_input_df
        options = ["clear_status", "instance_nonzero"]
        expected_mask = pd.Series([False, False, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask, check_names=False)

    def test_clear_instance_nonzero_exclude_nan_classes(self, create_input_df):
        df = create_input_df
        options = ["clear_status", "instance_nonzero", "exclude_nan_classes"]
        expected_mask = pd.Series([False, False, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask, check_names=False)

    def test_clear_longfom_instance_nonzero(self, create_input_df):
        df = create_input_df
        options = ["clear_status", "instance_nonzero", "longform_only"]
        expected_mask = pd.Series([False, False, False, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask, check_names=False)

    def test_not_mor_imputed_longform(self, create_input_df):
        df = create_input_df
        options = ["not_mor_imputed", "longform_only"]
        expected_mask = pd.Series([False, False, True, True, True, False])
        result_mask = create_mask(df, options)
        assert_series_equal(result_mask, expected_mask, check_names=False)


class TestSpecialFilter:
    """Tests for the SpecialFilter function."""
    def create_input_df(self, create_input_df):
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

    # def test_special_filter_create_mean_case(self, create_input_df):
    #     filter_conditions_list = ["clear_status", "instance_nonzero", "exclude_nan_classes"]
