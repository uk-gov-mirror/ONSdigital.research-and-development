"""Tests for intram_by_pg.py."""
# Standard Library Imports

from pandas.testing import assert_frame_equal
import logging
from io import StringIO
import pandas as pd
import pytest

# Local Imports
from src.outputs.intram_by_pg import output_intram_by_pg
from src.outputs.intram_by_pg import _generate_intarm_by_pg
from tests.test_outputs.conftest import read_config


# Assign config values to paths
config = read_config()
LOCATION = config["global"]["platform"]


# create logger (required pass to function)
TestLogger = logging.getLogger(__name__)


class TestIngramBYPg():
    """Unit tests for:
    - intram_by_pg._output_intram_by_pg
    - intram_by_pg.generate_intarm_by_pg.
    """

    # Arrange

    # Input dataframes
    @pytest.fixture()
    def gb_input_data(self) -> pd.DataFrame:
        """Tests for: _output_intram_by_pg & _generate_intarm_by_pg."""

        """Fixture for gb input data for tests."""
        gb_columns = ["reference", "instance", "201", "211"]
        gb_data = [[1, 1, "AA", 4628363.6364],
                    [1, 2, "AA", 0.0],
                    [2, 1, "AA", 0.0],
                    [3, 1, "I", 244533.1667],
                    [4, 1, "I", 244523.1667],
                    [5, 1, "D", 79911.0],
                    [6, 1, "AH", 26254673.0],
                    [7, 1, "AD", 2196.1027],
                    [8, 1, "C", 282622.6444],
                    [9, 1, "Z", 90163.1053]]
        gb_input_data_df = pd.DataFrame(data=gb_data,
                                        columns=gb_columns)
        return gb_input_data_df

    @pytest.fixture()
    def ni_input_data(self) -> pd.DataFrame:
        """Fixture for NI input data for tests."""
        ni_columns = ["reference", "instance", "201", "211"]
        ni_data = [[1, 1, "C", 27.0],
                   [1, 2, "G", 102.0],
                   [2, 1, "AA", 250.0],
                   [3, 1, "I", 628.0],
                   [4, 1, "D", 18.0],
                   [5, 1, "AA", 7.0],
                   [6, 1, "E", 41.0],
                   [7, 1, "AA", 0.0],
                   [8, 1, "AD", 143.0],
                   [9, 1, "J", 138.0]]
        ni_input_data_df = pd.DataFrame(data=ni_data,
                                        columns=ni_columns)

        return ni_input_data_df

    @pytest.fixture()
    def pg_detailed_mapper_data(self) -> pd.DataFrame:
        """pg_detailed mapper, including a subset of PGs"""
        pg_mapper_columns = [
            "ranking",
            "pg_alpha",
            "Detailed product groups (Alphabetical product groups A-AH)",
            "Notes"]
        pg_mapper_data = [
            [1, "total", "Total", "Total q211 across all PG"],
            [4, "C", "Food products and beverages; Tobacco products",
                "Total q211 for PG C"],
            [5, "D", "Textiles, clothing and leather products",
                "Total q211 for PG D"],
            [6, "E",
                "Pulp, paper and paper products; Printing; Wood and straw products",
                "Total q211 for PG E"],
            [8, "G", "Chemicals and chemical products", "Total q211 for PG G"],
            [10, "I", "Rubber and plastic products", "Total q211 for PG I"],
            [11, "J", "Other non-metallic mineral products", "Total q211 for PG J"],
            [27, "Z", "Construction", "Total q211 for PG Z"],
            [28, "AA", "Wholesale and retail trade", "Total q211 for PG AA"],
            [31, "AD",
                "Miscellaneous business activities; Technical testing and analysis",
                "Total q211 for PG AD"],
            [35, "AH", "Software Development", "Total q211 for PG AH"]]
        pg_detailed_mapper = pd.DataFrame(data=pg_mapper_data,
                                          columns=pg_mapper_columns)

        return pg_detailed_mapper

    # Expected output dataframes

    @pytest.fixture()
    def gb_expected_output_data(self) -> pd.DataFrame:
        """The expected output of output_intram_by_pg (no NI data)."""
        gb_expcted_columns = [
            "Detailed product groups (Alphabetical product groups A-AH)",
            "2023",
            "Notes"]
        gb_expcted_data = [
            ["Total", 31826985.8222, "Total q211 across all PG"],
            ["Food products and beverages; Tobacco products", 282622.6444,
                "Total q211 for PG C"],
            ["Textiles, clothing and leather products", 79911.0,
                "Total q211 for PG D"],
            ["Pulp, paper and paper products; Printing; Wood and straw products",
                0.0, "Total q211 for PG E"],
            ["Chemicals and chemical products", 0.0, "Total q211 for PG G"],
            ["Rubber and plastic products", 489056.3334, "Total q211 for PG I"],
            ["Other non-metallic mineral products", 0.0, "Total q211 for PG J"],
            ["Construction", 90163.1053, "Total q211 for PG Z"],
            ["Wholesale and retail trade", 4628363.6364, "Total q211 for PG AA"],
            ["Miscellaneous business activities; Technical testing and analysis",
                2196.1027, "Total q211 for PG AD"],
            ["Software Development", 26254673.0, "Total q211 for PG AH"]]
        gb_expected_df = pd.DataFrame(data=gb_expcted_data,
                                      columns=gb_expcted_columns)
        return gb_expected_df

    @pytest.fixture()
    def uk_expected_output_data(self) -> pd.DataFrame:
        """The expected output of output_intram_by_pg (with NI data)."""
        uk_expected_columns = [
            "Detailed product groups (Alphabetical product groups A-AH)",
            "2023",
            "Notes"]
        uk_expected_data = [
            ["Total", 31828339.822200004, "Total q211 across all PG"],
            ["Food products and beverages; Tobacco products", 282649.6444,
                "Total q211 for PG C"],
            ["Textiles, clothing and leather products", 79929.0,
                "Total q211 for PG D"],
            ["Pulp, paper and paper products; Printing; Wood and straw products",
                41.0, "Total q211 for PG E"],
            ["Chemicals and chemical products", 102.0, "Total q211 for PG G"],
            ["Rubber and plastic products", 489684.3334, "Total q211 for PG I"],
            ["Other non-metallic mineral products", 138.0, "Total q211 for PG J"],
            ["Construction", 90163.1053, "Total q211 for PG Z"],
            ["Wholesale and retail trade", 4628620.6364, "Total q211 for PG AA"],
            ["Miscellaneous business activities; Technical testing and analysis",
                2339.1027, "Total q211 for PG AD"],
            ["Software Development", 26254673.0, "Total q211 for PG AH"]]

        uk_expected_df = pd.DataFrame(data=uk_expected_data,
                                      columns=uk_expected_columns)

        return uk_expected_df

    def test_generate_intarm_by_pg(self,
                                   gb_input_data,
                                   ni_input_data,
                                   pg_detailed_mapper_data,
                                   gb_expected_output_data,
                                   uk_expected_output_data):
        """Test for _generate_intarm_by_pg."""

        # Act
        gb_result = _generate_intarm_by_pg(gb_input_data,
                                           ni_input_data,
                                           pg_detailed_mapper_data,
                                           uk_output=False,
                                           config=config)
        uk_result = _generate_intarm_by_pg(gb_input_data,
                                           ni_input_data,
                                           pg_detailed_mapper_data,
                                           uk_output=True,
                                           config=config)

        # Assert
        assert_frame_equal(gb_result[0], gb_expected_output_data)
        assert_frame_equal(uk_result[0], uk_expected_output_data)
    
    def _aws_credentials():
        """Mock AWS Credentials for moto."""
        boto3.setup_default_session(
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
            aws_session_token="testing",
        )

    def generate_s3_client(_aws_credentials):
        """Provide a mocked AWS S3 client for testing
        using moto with temporary credentials.
        """
        with mock_aws():
            client = boto3.client("s3", region_name="us-east-1")
            client.create_bucket(Bucket="test-bucket")
            yield client

    generate_s3_client(_aws_credentials)

    #@pytest.fixture()
    #def mock_write_csv(s3_client):
    #    """Fixture to write a Pandas DataFrame to CSV in an S3 bucket."""
    @pytest.fixture()
    def mock_write_csv(filepath: str, data: pd.DataFrame) -> None:
        """Write a Pandas DataFrame to CSV in an S3 bucket.

        Args:
            filepath (str): The filepath to save the DataFrame to.
            data (pd.DataFrame): The DataFrame to write to the passed path.

        Returns:
            None
        """
        # Create an Input-Output buffer
        csv_buffer = StringIO()

        # Write the DataFrame to the buffer in the CSV format
        data.to_csv(
            csv_buffer, header=True, date_format="%Y-%m-%d %H:%M:%S.%f+00", index=False
        )

        # "Rewind" the stream to the start of the buffer
        csv_buffer.seek(0)

        # Write the buffer into the S3 bucket
        _ = s3_client.put_object(
            Bucket="test-bucket", Body=csv_buffer.getvalue(), Key=filepath
        )
        return None
    #    return _mock_write_csv

    def test_output_intram_by_pg(self,
                                 gb_input_data,
                                 ni_input_data,
                                 pg_detailed_mapper_data,
                                 mock_write_csv):
        """Test for output_intram_by_pg."""

        config["outputs_paths"]["outputs_master"] = "temp/path"

        # Act
        gb_result = output_intram_by_pg(gb_input_data,
                                        ni_input_data,
                                        pg_detailed_mapper_data,
                                        config=config,
                                        intram_tot_dict=dict(),
                                        write_csv=mock_write_csv(),
                                        run_id="test",
                                        uk_output=False)
        uk_result = output_intram_by_pg(gb_input_data,
                                        ni_input_data,
                                        pg_detailed_mapper_data,
                                        config=config,
                                        intram_tot_dict=dict(),
                                        write_csv=mock_write_csv,
                                        run_id="test",
                                        uk_output=True)

        # Assert
        self.assertEqual(gb_result == {"intram_by_pg_gb": 31826986})
        self.assertEqual(uk_result == {"intram_by_pg_uk": 31828340})
