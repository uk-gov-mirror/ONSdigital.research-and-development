import numpy as np
from pandas._testing import assert_frame_equal
from pandas import DataFrame as pandasDF

from src.imputation.short_to_long import run_short_to_long


class TestShortToLong:

    """Unit tests for short_to_long function."""
    def create_input_df(self):
        """Create an input dataframe for the test."""
        input_cols = [
            "reference",
            "status",
            "formtype",
            "200",
            "instance",
            "701",
            "702",
            "211",
            "703",
            "704",
            "305",
            "705",
            "706",
            "707",
            "709",
            "710",
            "711",
            "emp_total",
            "headcount_total"
        ]

        input_data = [
            [11, "Clear", "0001", 'C', 0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [11, "Clear", "0006", 'C', 0, 1337, 0, np.nan, 1000, 18, np.nan, 20, 21, 22, 1337, 1000, 8, np.nan, 20],
            [11, "Clear", "0006", 'C', 1, 1337, 0, np.nan, 1000, 18, np.nan, 20, 21, 22, 1337, 1000, 8, np.nan, 20],
            [11, "Clear", "0006", 'C', 2, 1337, 2, np.nan, 600, 18, np.nan, 20, 21, 22, 1337, 600, 6, np.nan, 20],
            [11, "Clear", "0006", 'C', 3, 1337, 4, np.nan, 600, 18, np.nan, 20, 0, 0, 1337, 600, 6, np.nan, 20]
        ]

        input_df = pandasDF(data=input_data, columns=input_cols)

        return input_df

    def create_expected_df(self):
        expected_cols = [
            "reference",
            "status",
            "formtype",
            "200",
            "instance",
            "701",
            "702",
            "211",
            "703",
            "704",
            "305",
            "705",
            "706",
            "707",
            "709",
            "710",
            "711",
            "emp_total",
            "headcount_total"
        ]

        expected_data = [
            [11, "Clear", "0001", "C" , 0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [11, "Clear", "0006", "C", 0, 1337.0, 0.0, np.nan, 1000.0, 18.0, np.nan, 20.0, 21.0, 22.0, 1337.0, 1000.0, 8.0, np.nan, 20.0],
            [11, "Clear", "0006", "C", 0, 1337.0, 0.0, np.nan, 1000.0, 18.0, np.nan, 20.0, 21.0, 22.0, 1337.0, 1000.0, 8.0, np.nan, 20.0],
            [11, "Clear", "0006", "C", 0, 1337.0, 2.0, np.nan, 600.0, 18.0, np.nan, 20.0, 21.0, 22.0, 1337.0, 600.0, 6.0, np.nan, 20.0],
            [11, "Clear", "0006", "C", 0, 1337.0, 4.0, np.nan, 600.0, 18.0, np.nan, 20.0, 0.0, 0.0, 1337.0, 600.0, 6.0, np.nan, 20.0],
            [11, "Clear", "0006", "C", 1, 1337.0, 0.0, 1337.0, 1000.0, 18.0, 1000.0, 20.0, 21.0, 22.0, 1337.0, 1000.0, 8.0, 21.0, 9.7674],
            [11, "Clear", "0006", "C", 1, 1337.0, 0.0, 1337.0, 1000.0, 18.0, 1000.0, 20.0, 21.0, 22.0, 1337.0, 1000.0, 8.0, 21.0, 9.7674],
            [11, "Clear", "0006", "C", 1, 1337.0, 2.0, 1337.0, 600.0, 18.0, 600.0, 20.0, 21.0, 22.0, 1337.0, 600.0, 6.0, 21.0, 9.7674],
            [11, "Clear", "0006", "C", 1, 1337.0, 4.0, 1337.0, 600.0, 18.0, 600.0, 20.0, 0.0, 0.0, 1337.0, 600.0, 6.0, 0.0, 0.0],
            [11, "Clear", "0006", "D", 2, 1337.0, 0.0, 0.0, 1000.0, 18.0, 18.0, 20.0, 21.0, 22.0, 1337.0, 1000.0, 8.0, 22.0, 10.2326],
            [11, "Clear", "0006", "D", 2, 1337.0, 0.0, 0.0, 1000.0, 18.0, 18.0, 20.0, 21.0, 22.0, 1337.0, 1000.0, 8.0, 22.0, 10.2326],
            [11, "Clear", "0006", "D", 2, 1337.0, 2.0, 2.0, 600.0, 18.0, 18.0, 20.0, 21.0, 22.0, 1337.0, 600.0, 6.0, 22.0, 10.2326],
            [11, "Clear", "0006", "D", 2, 1337.0, 4.0, 4.0, 600.0, 18.0, 18.0, 20.0, 0.0, 0.0, 1337.0, 600.0, 6.0, 0.0, 0.0]
        ]

        expected_df = pandasDF(data=expected_data, columns=expected_cols)

        return expected_df

    def test_short_to_long(self):
        """Test the short_to_long function."""
        # Create an input DataFrame
        input_df = self.create_input_df()

        input_df.to_csv("input_df.csv", index=False)

        # Create the expected DataFrame
        expected_df = self.create_expected_df()

        # Run the function
        output_df = run_short_to_long(input_df)

        output_df.to_csv("output_df.csv", index=False)

        # Check the output
        assert_frame_equal(output_df, expected_df)
