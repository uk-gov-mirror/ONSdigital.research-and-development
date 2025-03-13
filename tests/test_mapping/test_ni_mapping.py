import pandas as pd

from src.mapping.ni_mapping import join_itl_regions_ni, create_additional_ni_cols

class TestJoinItlRegionsNi(object):
    """Tests for join_itl_regions_ni function."""

    def config(self) -> dict:
        """A dummy config for running join_itl_regions tests."""
        config = {
            "mappers": {
                "geo_cols": ["ITL221CD", "ITL221NM", "ITL121CD", "ITL121NM"],
                "gb_itl": "LAU121CD",
                "ni_itl": "N92000002",
            }
        }
        return config

    def itl_mapper(self) -> pd.DataFrame:
        """ITL mapper for output_intram_by_itl tests."""
        columns = ["LAU121CD", "ITL221CD", "ITL221NM", "ITL121CD", "ITL121NM"]
        data = [
            ["N92000002", "TLN0", "Northern Ireland", "TLN", "Northern Ireland"],
        ]
        df = pd.DataFrame(columns=columns, data=data)
        return df

    def input_df(self) -> pd.DataFrame:
        """Input DataFrame for join_itl_regions_ni tests."""
        columns = ["reference", "itl"]
        data = [
            [1, "N92000002"],
            [2, "N92000002"],
            [3, "N92000002"],
        ]
        df = pd.DataFrame(data=data, columns=columns)
        return df

    def expected_output(self) -> pd.DataFrame:
        """Expected output for join_itl_regions_ni tests."""
        columns = [
            "reference",
            "itl",
            "ITL221CD",
            "ITL221NM",
            "ITL121CD",
            "ITL121NM",
        ]

        data = [
            [1, "N92000002", "TLN0", "Northern Ireland", "TLN", "Northern Ireland"],
            [2, "N92000002", "TLN0", "Northern Ireland", "TLN", "Northern Ireland"],
            [3, "N92000002", "TLN0", "Northern Ireland", "TLN", "Northern Ireland"],
        ]

        df = pd.DataFrame(data=data, columns=columns)
        return df

    def test_join_itl_regions_ni(self):
        """Test join_itl_regions_ni function."""
        df = self.input_df()
        itl_mapper = self.itl_mapper()
        config = self.config()
        expected_df = self.expected_output()

        # Call the function
        output_df = join_itl_regions_ni(df, itl_mapper, config)

        # Check if the output matches the expected DataFrame
        assert output_df.equals(
            expected_df,
        ), "Output from join_itl_regions_ni not as expected."

class TestCreateAdditionalNiCols(object):
    """Tests for create_additional_ni_cols function."""

    def test_create_additional_ni_cols(self):
        """Test create_additional_ni_cols function."""
        # Create sample input DataFrame
        columns = ["reference", "value"]
        data = [
            [1, 10],
            [2, 20],
            [3, 30],
        ]
        df = pd.DataFrame(data=data, columns=columns)

        # Expected output DataFrame
        expected_columns = [
            "reference",
            "value",
            "a_weight",
            "g_weight",
            "604",
            "form_status",
            "602",
            "formtype",
        ]
        expected_data = [
            [1, 10, 1, 1, "Yes", 600, 100.0, "0003"],
            [2, 20, 1, 1, "Yes", 600, 100.0, "0003"],
            [3, 30, 1, 1, "Yes", 600, 100.0, "0003"],
        ]
        expected_df = pd.DataFrame(data=expected_data, columns=expected_columns)

        # Call the function
        output_df = create_additional_ni_cols(df)

        # Check if the output matches the expected DataFrame
        assert output_df.equals(
            expected_df
        ), "Output from create_additional_ni_cols not as expected."
