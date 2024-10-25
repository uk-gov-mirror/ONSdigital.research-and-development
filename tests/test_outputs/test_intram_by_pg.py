"""Tests for intram_by_pg.py."""
# Standard Library Imports

from pandas.testing import assert_frame_equal 
import pytest
import os
import logging
import pathlib

# Third Party Imports
import pandas as pd

# Local Imports
from src.outputs.intram_by_pg import output_intram_by_pg
from src.outputs.intram_by_pg import generate_intarm_by_pg
from tests.test_outputs.conftest import read_config


# Assign config values to paths
config = read_config()
LOCATION = config["global"]["platform"]

# create logger (required pass to function)
TestLogger = logging.getLogger(__name__)


class TestIngramBYPg(object):

    # @pytest.mark.parametrize(
    #    "ni, exp_out", ([False, exp_out_gb()], [True, exp_out_uk()]))
    def test_output_intram_by_pg(self):
        """Tests for output_intram_by_pg."""
        # Arrange

        # Input dataframes
        """Fixture for gb input data for tests."""
        gb_columns = ["reference", "instance", "201", "211"]
        gb_data = [
            [1, 1, "AA", 4628363.6364],
            [1, 2, "AA", 0.0],
            [2, 1, "AA", 0.0],
            [3, 1, "I", 244533.1667],
            [4, 1, "I", 244523.1667],
            [5, 1, "D", 79911.0],
            [6, 1, "AH", 26254673.0],
            [7, 1, "AD", 2196.1027],
            [8, 1, "C", 282622.6444],
            [9, 1, "Z", 90163.1053]]
        gb_input_data_df = pd.DataFrame(data=gb_data, columns=gb_columns)

        """Fixture for NI input data for tests."""
        ni_columns = ["reference", "instance", "201", "211"]
        ni_data = [
            [1, 1, "C", 27.0],
            [1, 2, "G", 102.0],
            [2, 1, "AA", 250.0],
            [3, 1, "I", 628.0],
            [4, 1, "D", 18.0],
            [5, 1, "AA", 7.0],
            [6, 1, "E", 41.0],
            [7, 1, "AA", 0.0],
            [8, 1, "AD", 143.0],
            [9, 1, "J", 138.0]]
        ni_input_data_df = pd.DataFrame(data=ni_data, columns=ni_columns)

        """pg_detailed mapper, including a subset of PGs"""
        mapper_columns = [
            "ranking",
            "pg_alpha",
            "Detailed product groups (Alphabetical product groups A-AH)",
            "Notes"]
        mapper_data = [
            [1, "total", "Total", "Total q211 across all PG"],
            [4, "C", "Food products and beverages; Tobacco products",
                "Total q211 for PG C"],
            [5, "D", "Textiles, clothing and leather products", "Total q211 for PG D"],
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
        pg_detailed_mapper = pd.DataFrame(data=mapper_data, columns=mapper_columns)

        # Expected output dataframes

        """The expected output of output_intram_by_pg (no NI data)."""
        gb_expcted_columns = [
            "Detailed product groups (Alphabetical product groups A-AH)",
            "2023 (Current period)",
            "Notes"]
        gb_expcted_data = [
            ["Total", 31826985.8222, "Total q211 across all PG"],
            ["Food products and beverages; Tobacco products", 282622.6444, 
             "Total q211 for PG C"],
            ["Textiles, clothing and leather products", 79911.0, "Total q211 for PG D"],
            ["Pulp, paper and paper products; Printing; Wood and straw products", 0.0,
             "Total q211 for PG E"],
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

        """The expected output of output_intram_by_pg (with NI data)."""
        uk_expected_columns = [
            "Detailed product groups (Alphabetical product groups A-AH)",
            "2023 (Current period)",
            "Notes"]
        uk_expected_data = [
            ["Total", 31828339.822200004, "Total q211 across all PG"],
            ["Food products and beverages; Tobacco products", 282649.6444,
             "Total q211 for PG C"],
            ["Textiles, clothing and leather products", 79929.0, "Total q211 for PG D"],
            ["Pulp, paper and paper products; Printing; Wood and straw products", 41.0,
             "Total q211 for PG E"],
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

        # Act
        gb_result = generate_intarm_by_pg(gb_input_data_df, ni_input_data_df,
                                          pg_detailed_mapper, uk_output=False)
        uk_result = generate_intarm_by_pg(gb_input_data_df, ni_input_data_df,
                                          pg_detailed_mapper, uk_output=True)

        # Assert
        assert_frame_equal(gb_result[0], gb_expected_df)
        assert_frame_equal(uk_result[0], uk_expected_df)

        '''

        """Tests for output_intram_by_pg."""
        pth = self.setup_tmp_dir(pathlib.Path(tmp_path), ni)
        # alter path so that tests pass
        config["outputs_paths"]["outputs_master"] = os.path.dirname(pth)
        intram_dict = {"estimated": 600}
        if not ni:
            input_data_ni = pd.DataFrame()
        intram_dict = output_intram_by_pg(
            gb_df=input_data_gb,
            ni_df=input_data_ni,
            pg_detailed=pg_detailed_df,
            config=config,
            intram_tot_dict=intram_dict,
            write_csv=write_csv_func,
            run_id=1,
            uk_output=ni,
        )
        # assert output saved
        found_paths = os.listdir(pth)
        assert len(found_paths) > 0, "Outputs not saved."
        output = pd.read_csv(os.path.join(pth, found_paths[0]))
        # refine df
        output = output[output["2023 (Current period)"] > 0].reset_index(drop=True)
        # assert output is correct
        assert output.equals(exp_out), "Output not as expected."
        '''
