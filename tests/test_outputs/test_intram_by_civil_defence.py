"""Tests for intram_by_civil_defence.py."""

# Local Standard Library Imports
import pandas as pd
import pytest
from unittest.mock import Mock

# Local Imports
from src.outputs.intram_by_civil_defence import (
    output_intram_by_civil_defence,
    generate_intram_by_civil_defence,
    _save_output_intram_civil_def_as_csv
)

class TestIntramByCivilDefence(object):
    """Tests for Civil and Defence Output."""
    @pytest.fixture(scope="function")
    def config(self):
        config = {
            "outputs_paths": {"outputs_master": "tests/test_outputs/"},
            "survey": {"survey_year": 2020, "survey_type": "test"},
            "filename_items": {"run_id": "999", "tdate": "test_date"},
        }
        return config

    @pytest.fixture(scope="function")
    def input_data(self):
        """Create input dataframe"""

        data = {"200": ["C", "D", "C", "D", "C", "D", "D", "C", "D", "C"],
                "211": [1000, 2000, 0, 500, 3020, 40, 6000, 700, 8180, 960], }
        input_df = pd.DataFrame(data)
        return input_df

    @pytest.fixture(scope="function")
    def exp_out(self):
        """Create expected output dataframe"""
        columns = ["Catergory", "Total Intramural Expenditure"]
        data = [["Civil", 5680], ["Defence", 16720]]
        expected_df = pd.DataFrame(data=data, columns=columns)
        return expected_df

    def test_generate_intram_by_civil_defence(self, input_data, exp_out):
        """Test generate_intram_by_civil_defence function.
        The test checks if Civil and Defense are catergorised and summed correctly."""
        output_df = generate_intram_by_civil_defence(input_data)
        assert output_df.equals(exp_out)


    def mock_write_csv(self, filepath: str, data: pd.DataFrame) -> None:
        """Dummy script mimicking the function passed to the module as write_csv.

        Args:
            filepath (str): The filepath to save the DataFrame to.
            data (pd.DataFrame): The DataFrame to write to the passed path.

        Returns:
            None
        """
        return True

    def test_save_output_intram_civil_def_as_csv(self, config, exp_out):
        """Test _save_output_intram_civil_def_as_csv function.
        The test checks if the output is saved as a csv file."""

        # Use the mock_write_csv function
        mock_write_csv = Mock(side_effect=self.mock_write_csv)

        # Call the function with the mock write_csv
        _save_output_intram_civil_def_as_csv(exp_out, config, mock_write_csv)

        # Check that the mock write_csv function has been called with the correct arguments
        mock_write_csv.assert_called_once()
        args, kwargs = mock_write_csv.call_args
        assert isinstance(args[0], str), "The first argument should be a string (filepath)."
        assert isinstance(args[1], pd.DataFrame), "The second argument should be a DataFrame."

        # check the correct filename and file path are used
        exp_out_path = f"{config['outputs_paths']['outputs_master']}/output_intram_by_civil_defence/2020_output_intram_by_civil_defence_test_date_v999.csv"
        assert args[0] == exp_out_path, "The filepath should match the output path in the config."
        # check the correct dataframe is passed
        pd.testing.assert_frame_equal(args[1], exp_out, "The DataFrame should match the expected output.")

    def test_output_intram_by_civil_defence(self, input_data, exp_out, config):
        """Test output_intram_by_civil_defence function.
        The test checks if the output is saved as a csv file."""

        # Use the mock_write_csv function
        mock_write_csv = Mock(side_effect=self.mock_write_csv)

        # Call the function with the mock write_csv
        output_intram_by_civil_defence(input_data, config, mock_write_csv)

        # Check that the mock write_csv function has been called with the correct arguments
        mock_write_csv.assert_called_once()
        args, kwargs = mock_write_csv.call_args
        assert isinstance(args[0], str), "The first argument should be a string (filepath)."
        assert isinstance(args[1], pd.DataFrame), "The second argument should be a DataFrame."

        # check the output dataframe is as expected
        pd.testing.assert_frame_equal(args[1], exp_out, "The DataFrame should match the input data.")
