
from pandas import DataFrame as pandasDF
from pandas._testing import assert_frame_equal
import numpy as np
from src.imputation.MoR import carry_forwards


class test_carry_forward:
    """Unit test to check the carry forward imputation method"""

    def create_backdata(self):
        """Create an input_dataframe for the test."""
        input__columns = [
            "reference",
            "instance",
            "period_year",
            "200",
            "201",
            "211",
            "601",
            "604",
            "formtype",
            "status",
            "imp_marker",
            "imp_class",
        ]

        data = [
            [1031, 0, 2021, None, "AA", np.nan, "CF14 7UB", "Yes", "0006", "Form sent out", "R", "nan_AA"],
            [1031, 1, 2021, "C", "AA", 100000.0, np.nan, "Yes", "0006", "Check needed", "R", "C_AA"],
            [1031, 2, 2021, "D", "AA", np.nan, None, "Yes", "0006", "Check needed", "R", "D_AA"],
            [1032, 0, 2021, np.nan, "L", np.nan, np.nan, np.nan, "0006", "Form sent out", "R", "nan_L"],
            [1032, 1, 2021, "C", "L", np.nan, np.nan, np.nan, "0006", "Check needed", "R", "C_L"],
            [1033, 0, 2021, np.nan, "AB", np.nan, np.nan, "No", "0001", "Clear", "R", "nan_AB"],
            [1033, 1, 2021, "C", "AB", 62500.0, "NY56 9DV", "No", "0001", "Clear", "R", "C_AB"],
            [1040, 1, 2021, "D", "G", 86000.0, np.nan, np.nan, "0006", "Check needed", "TMI", "D_G"],
            [1042, 1, 2021, "D", "P", 9000.0, np.nan, "No", "0006", "Check needed", "TMI", "D_P"],
            [1045, 0, 2021, np.nan, "AH", np.nan, np.nan, "No", "0001", "Form sent out", "R", "nan_AH"],
            [1045, 1, 2021, "C", "AH", 20000.0, np.nan, "Yes", "0001", "Check needed", "R", "C_AH"],
            [1045, 2, 2021, "D", "AH", 30000.0, np.nan, "Yes", "0001", "Check needed", "R", "D_AH"],
            [1046, 0, 2021, np.nan, "AD", None, np.nan, "Yes", "0006", "Form sent out", "R", "nan_AD"],
            [1046, 1, 2021, "D", "AD", 80500.0, "GJ73 3GB", "Yes", "0006", "Check needed", "R", "D_AD"],
            [1046, 2, 2021, "C", "AD", 36000.0, "PL6 8BX", "Yes", "0006", "Check needed", "R", "C_AD"],
            [1046, 3, 2021, np.nan, "AD", np.nan, "RG7 2PQ", "Yes", "0006", "Check needed", "R", "nan_AD"],
            [1046, 4, 2021, np.nan, "AD", np.nan, "GU16 7HF", "Yes", "0006", "Check needed", "R", "nan_AD"],
        ]

        backdata_df = pandasDF(data, columns=input__columns)
        return backdata_df

    def create_input__df(self):
        """Create an input_ dataframe for the test."""
        input_columns = [
            "reference",
            "instance",
            "period_year",
            "200",
            "201",
            "211",
            "601",
            "602",
            "604",
            "formtype",
            "status",
            "postcodes_harmonised",
            "imp_marker",
            "imp_class",
        ]

        data = [
            [1031, 0, 2022, None, "AA", np.nan, "CF14 7UB", np.nan, "Yes", "0006", "Form sent out", "CF14 7UB", "no_imputation", "<NA>_AA"],
            [1031, 0, 2022, None, "AA", 100000.0, np.nan, np.nan, "Yes", "0006", "Form sent out", "CF14 7UB", "no_imputation", "<NA>_AA"],
            [1031, 0, 2022, None, "AA", np.nan, np.nan, np.nan, "Yes", "0006", "Form sent out", "CF14 7UB", "no_imputation", "<NA>_AA"],
            [1031, 1, 2022, "C", "AA", np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "CF14 7UB", "no_imputation", "C_AA"],
            [1031, 1, 2022, "C", "AA", np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "CF14 7UB", "no_imputation", "C_AA"],
            [1031, 1, 2022, "C", "AA", np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "CF14 7UB", "no_imputation", "C_AA"],
            [1031, 2, 2022, "D", "AA", np.nan, None, np.nan, np.nan, "0006", "Check needed", "CF14 7UB", "no_imputation", "D_AA"],
            [1031, 2, 2022, "D", "AA", np.nan, None, np.nan, np.nan, "0006", "Check needed", "CF14 7UB", "no_imputation", "D_AA"],
            [1031, 2, 2022, "D", "AA", np.nan, None, np.nan, np.nan, "0006", "Check needed", "CF14 7UB", "no_imputation", "D_AA"],
            [1032, 0, 2022, np.nan, "L", np.nan, np.nan, np.nan, np.nan, "0006", "Form sent out", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1032, 0, 2022, np.nan, "L", np.nan, np.nan, np.nan, np.nan, "0006", "Form sent out", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1032, 1, 2022, np.nan, "L", np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1032, 1, 2022, np.nan, "L", np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1033, 0, 2022, np.nan, "AB", np.nan, np.nan, np.nan, "No", "0001", "Clear", "NY56 9DV", "no_imputation", "<NA>_AB"],
            [1033, 0, 2022, np.nan, "AB", np.nan, np.nan, np.nan, "No", "0001", "Clear", "NY56 9DV", "no_imputation", "<NA>_AB"],
            [1033, 1, 2022, "C", "AB", 62500.0, "NY56 9DV", np.nan, "No", "0001", "Clear", "NY56 9DV", "no_imputation", "C_AB"],
            [1033, 1, 2022, "C", "AB", 62500.0, "NY56 9DV", np.nan, "No", "0001", "Clear", "NY56 9DV", "no_imputation", "C_AB"],
            [1040, 1, 2022, "D", "G", 86000.0, np.nan, np.nan, np.nan, "0006", "Check needed", "UB6 OHE", "no_imputation", "D_AB"],
            [1042, 1, 2022, "D", "P", 9000.0, np.nan, np.nan, "No", "0006", "Check needed", "AB10 1BL", "no_imputation", "D_AB"],
            [1045, 0, 2022, np.nan, "AH", np.nan, np.nan, np.nan, "No", "0001", "Form sent out", "WA3 6AE", "no_imputation", "<NA>_AH"],
            [1045, 0, 2022, np.nan, "AH", np.nan, np.nan, np.nan, "No", "0001", "Form sent out", "WA3 6AE", "no_imputation", "<NA>_AH"],
            [1045, 0, 2022, np.nan, "AH", np.nan, np.nan, np.nan, "No", "0001", "Form sent out", "WA3 6AE", "no_imputation", "<NA>_AH"],
            [1045, 1, 2022, "C", "AH", 20000.0, np.nan, np.nan, "Yes", "0001", "Check needed", "WA3 6AE", "no_imputation", "C_AH"],
            [1045, 1, 2022, "C", "AH", 20000.0, np.nan, np.nan, "Yes", "0001", "Check needed", "WA3 6AE", "no_imputation", "C_AH"],
            [1045, 1, 2022, "C", "AH", 20000.0, np.nan, np.nan, "Yes", "0001", "Check needed", "WA3 6AE", "no_imputation", "C_AH"],
            [1045, 2, 2022, "D", "AH", 30000.0, np.nan, np.nan, "Yes", "0001", "Check needed", "WA3 6AE", "no_imputation", "D_AH"],
            [1045, 2, 2022, "D", "AH", 30000.0, np.nan, np.nan, "Yes", "0001", "Check needed", "WA3 6AE", "no_imputation", "D_AH"],
            [1045, 2, 2022, "D", "AH", 30000.0, np.nan, np.nan, "Yes", "0001", "Check needed", "WA3 6AE", "no_imputation", "D_AH"],
        ]

        input__df = pandasDF(data, columns=input_columns)
        return input__df

    def create_output_df(self):
        """Create an output_dataframe for the test."""
