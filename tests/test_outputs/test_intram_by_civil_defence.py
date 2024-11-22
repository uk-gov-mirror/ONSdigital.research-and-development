"""Tests for intram_by_civil_defence.py."""

# Local Standard Library Imports
import pandas as pd
import pytest

# Local Imports
from src.outputs.intram_by_civil_defence import generate_intram_by_civil_defence
from src.outputs.intram_by_civil_defence import _save_output_intram_civil_def_as_csv

class TestIntramByCivilDefence(object):

    """Test for Civil and Defence Output."""
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
        return None
