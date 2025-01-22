"""Test for carry_forward imputation"""
# Imports
import pandas as pd
import pytest
import numpy as np

from pandas._testing import assert_frame_equal
from src.imputation.MoR import carry_forwards


class Test_carry_forward(object):
    """Tests for carry_forwards."""

    @pytest.fixture(scope="function")
    def dummy_CF_backdata(self):
        """Create an backdata dataframe for the test."""
        columns = [
            "reference",
            "instance",
            "period_year",
            "200",
            "201",
            "211",
            "212",
            "601",
            "602",
            "604",
            "emp_total",
            "formtype",
            "status",
            "imp_marker",
            "imp_class"
        ]

        data = [
            [1031, 0, 2021, np.nan, "AA", 6000.0, np.nan, "CF14 7UB", np.nan, "Yes", np.nan, "0001", "Form sent out", "R", "nan_AA"],
            [1031, 1, 2021, "C", "AA", np.nan, np.nan, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "R", "C_AA"],
            [1031, 2, 2021, "D", "AA", np.nan, np.nan, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "R", "D_AA"],
            [1032, 0, 2021, np.nan, "L", 11000.0, 11000.0, "CV34 6UX", np.nan, np.nan, 10.0, "0001", "Form sent out", "R", "nan_L"],
            [1032, 1, 2021, "C", "L", np.nan, np.nan, "CV34 6UX", np.nan, np.nan, 10.0, "0001", "Check needed", "R", "C_L"],
            [1040, 1, 2021, "D", "G", 87200.0, np.nan, np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "TMI", "D_G"],
            [1042, 1, 2021, "D", "P", 8000.0, np.nan, np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "TMI", "D_P"],
            [1045, 0, 2021, np.nan, "AH", 20000.0, np.nan, "WA3 6AE", np.nan, "Yes", np.nan, "0001", "Form sent out", "R", "nan_AH"],
            [1045, 1, 2021, "C", "AH", 10000.0, np.nan, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "R", "C_AH"],
            [1045, 2, 2021, "D", "AH", 10000.0, np.nan, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "R", "D_AH"],
            [1047, 0, 2021, np.nan, "BC", 600.0, 600.0, np.nan, np.nan, np.nan, np.nan, "0001", "Form sent out", "TMI", "nan_BC"],
            [1047, 1, 2021, "C", "BC", 400.0, np.nan, "TY85 1ND", np.nan, "Yes", np.nan, "0001", "Check needed", "TMI", "C_BC"],
            [1047, 2, 2021, "D", "BC", 200.0, np.nan, np.nan, np.nan, np.nan, np.nan, "0001", "Check needed", "TMI", "D_BC"]
            ]

        df = pd.DataFrame(data=data, columns=columns)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df

    @pytest.fixture(scope="function")
    def dummy_CF_input(self):
        """Create an input dataframe for the test."""
        columns = [
            "reference",
            "instance",
            "period_year",
            "200",
            "201",
            "211",
            "212",
            "cellnumber",
            "601",
            "602",
            "604",
            "emp_total",
            "formtype",
            "status",
            "postcodes_harmonised",
            "imp_marker",
            "imp_class"
        ]

        data = [
            [1031, 0, 2022, np.nan, "AA", np.nan, np.nan, 286, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "CF14 7UB", "no_imputation", "<NA>_AA"],
            [1031, 0, 2022, np.nan, "AA", np.nan, np.nan, 286, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "CF14 7UB", "no_imputation", "<NA>_AA"],
            [1031, 0, 2022, np.nan, "AA", np.nan, np.nan, 286, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "CF14 7UB", "no_imputation", "<NA>_AA"],
            [1031, 1, 2022, "C", "AA", np.nan, np.nan, 286, np.nan, np.nan, np.nan, 10.0, "0001", "Check needed", "CF14 7UB", "no_imputation", "C_AA"],
            [1031, 1, 2022, "C", "AA", np.nan, np.nan, 286, np.nan, np.nan, np.nan, 10.0, "0001", "Check needed", "CF14 7UB", "no_imputation", "C_AA"],
            [1031, 1, 2022, "C", "AA", np.nan, np.nan, 286, np.nan, np.nan, np.nan, 10.0, "0001", "Check needed", "CF14 7UB", "no_imputation", "C_AA"],
            [1031, 2, 2022, "D", "AA", np.nan, np.nan, 286, np.nan, np.nan, np.nan, np.nan, "0001", "Check needed", "CF14 7UB", "no_imputation", "D_AA"],
            [1031, 2, 2022, "D", "AA", np.nan, np.nan, 286, np.nan, np.nan, np.nan, np.nan, "0001", "Check needed", "CF14 7UB", "no_imputation", "D_AA"],
            [1031, 2, 2022, "D", "AA", np.nan, np.nan, 286, np.nan, np.nan, np.nan, np.nan, "0001", "Check needed", "CF14 7UB", "no_imputation", "D_AA"],
            [1032, 0, 2022, np.nan, "L", 12000.0, 12000.0, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1032, 0, 2022, np.nan, "L", 12000.0, 12000.0, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1032, 1, 2022, np.nan, "L", np.nan, np.nan, 41, np.nan, np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1032, 1, 2022, np.nan, "L", np.nan, np.nan, 41, np.nan, np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "no_imputation", "<NA>_L"],
            [1033, 0, 2022, np.nan, "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "<NA>_AB"],
            [1033, 0, 2022, np.nan, "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "<NA>_AB"],
            [1033, 1, 2022, "C", "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "C_AB"],
            [1033, 1, 2022, "C", "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "C_AB"],
            [1040, 1, 2022, "D", "G", 86000.0, 86000.0, 60, np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "UB6 OHE", "no_imputation", "D_AB"],
            [1042, 1, 2022, "D", "P", 9000.0, 9000.0, 82, np.nan, np.nan, np.nan, np.nan, "0006", "Check needed", "AB10 1BL", "no_imputation", "D_AB"],
            [1045, 0, 2022, np.nan, "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "WA3 6AE", "no_imputation", "<NA>_AH"],
            [1045, 0, 2022, np.nan, "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "WA3 6AE", "no_imputation", "<NA>_AH"],
            [1045, 0, 2022, np.nan, "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "WA3 6AE", "no_imputation", "<NA>_AH"],
            [1045, 1, 2022, "C", "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "WA3 6AE", "no_imputation", "C_AH"],
            [1045, 1, 2022, "C", "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "WA3 6AE", "no_imputation", "C_AH"],
            [1045, 1, 2022, "C", "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "WA3 6AE", "no_imputation", "C_AH"],
            [1045, 2, 2022, "D", "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "WA3 6AE", "no_imputation", "D_AH"],
            [1045, 2, 2022, "D", "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "WA3 6AE", "no_imputation", "D_AH"],
            [1045, 2, 2022, "D", "AH", np.nan, np.nan, 473, np.nan, np.nan, "Yes", np.nan, "0001", "Check needed", "WA3 6AE", "no_imputation", "D_AH"],
            [1046, 0, 2022, np.nan, "AD", 84100.0, 84100.0, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "<NA>_AD"],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "<NA>_AD"],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "<NA>_AD"],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "<NA>_AD"],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "<NA>_AD"],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD"],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD"],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD"],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD"],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD"],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD"],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD"],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD"],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD"],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "<NA>_AD"],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "<NA>_AD"],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "<NA>_AD"],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "<NA>_AD"],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "<NA>_AD"],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "<NA>_AD"],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "<NA>_AD"],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "<NA>_AD"],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "<NA>_AD"],
            [1047, 0, 2022, np.nan, "BC", 600.0, np.nan, 262, np.nan, np.nan, np.nan, np.nan, "0001", "Form sent out", "TY85 1ND", "no_imputation", "<NA>_BC"],
            [1047, 1, 2022, "C", "BC", 400.0, np.nan, 262, "TY85 1ND", np.nan, "Yes", np.nan, "0001", "Form sent out", "TY85 1ND", "no_imputation", "C_BC"],
            [1047, 2, 2022, "D", "BC", 200.0, np.nan, 262, np.nan, np.nan, np.nan, np.nan, "0001", "Form sent out", "TY85 1ND", "no_imputation", "D_BC"]
        ]

        df = pd.DataFrame(data=data, columns=columns)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df

    @pytest.fixture(scope="function")
    def expected_CF_output(self):
        """Expected output from carry_forwards."""
        columns = [
            "reference",
            "instance",
            "period_year",
            "200",
            "201",
            "211",
            "212",
            "cellnumber",
            "601",
            "602",
            "604",
            "emp_total",
            "formtype",
            "status",
            "postcodes_harmonised",
            "imp_marker",
            "imp_class",
            "212_imputed",
            "emp_total_imputed",
            "212_prev",
            "emp_total_prev",
            "formtype_prev",
            "imp_marker_prev",
            "imp_class_prev"
            ]

        data = [
            [1032, 0, 2022, np.nan, "L", np.nan, np.nan, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "CF", "nan_L", 11000.0, 10.0, 11000.0, 10.0, "0001", "R", "nan_L"],
            [1032, 1, 2022, "C", "L", np.nan, np.nan, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "CF", "C_L", 0.0, 10.0, np.nan, 10.0, "0001", "R", "C_L"],
            [1032, 0, 2022, np.nan, "L", np.nan, np.nan, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "CF", "nan_L", 11000.0, 10.0, 11000.0, 10.0, "0001", "R", "nan_L"],
            [1032, 1, 2022, "C", "L", np.nan, np.nan, 41, "CV34 6UX", np.nan, np.nan, np.nan, "0001", "Form sent out", "CV34 6UX", "CF", "C_L", 0.0, 10.0, np.nan, 10.0, "0001", "R", "C_L"],
            [1033, 0, 2022, np.nan, "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "nan_AB", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1033, 0, 2022, np.nan, "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "nan_AB", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1033, 1, 2022, "C", "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "C_AB", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1033, 1, 2022, "C", "AB", np.nan, np.nan, 177, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "NY56 9DV", "no_imputation", "C_AB", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 0, 2022, np.nan, "AD", 84100.0, 84100.0, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "nan_AD_817", 84100.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 0, 2022, np.nan, "AD", np.nan, np.nan, 817, np.nan, np.nan, "Yes", np.nan, "0001", "Form sent out", "GJ73 3GB", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 1, 2022, "D", "AD", 80500.0, np.nan, 817, "GJ73 3GB", 25.0, "Yes", np.nan, "0001", "Check needed", "GJ73 3GB", "no_imputation", "D_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD_817", np.nan, 50.0, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD_817", np.nan, 50.0, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD_817", np.nan, 50.0, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 2, 2022, "C", "AD", 36000.0, np.nan, 817, "PL6 8BX", 10.0, "Yes", 50.0, "0001", "Check needed", "PL6 8BX", "no_imputation", "C_AD_817", np.nan, 50.0, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 3, 2022, np.nan, "AD", np.nan, np.nan, 817, "RG7 2PQ", 15.0, "Yes", np.nan, "0001", "Check needed", "RG7 2PQ", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1046, 4, 2022, np.nan, "AD", np.nan, np.nan, 817, "GU16 7HF", 50.0, "Yes", np.nan, "0001", "Check needed", "GU16 7HF", "no_imputation", "nan_AD_817", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [1047, 0, 2022, np.nan, "BC", 400.0, np.nan, 262, np.nan, np.nan, np.nan, np.nan, "0001", "Form sent out", "TY85 1ND", "CF", "nan_BC", 600.0, 0.0, 600.0, np.nan, "0001", "TMI", "nan_BC"],
            [1047, 1, 2022, "C", "BC", 400.0, np.nan, 262, "TY85 1ND", np.nan, "Yes", np.nan, "0001", "Form sent out", "TY85 1ND", "CF", "C_BC", 0.0, 0.0, np.nan, np.nan, "0001", "TMI", "C_BC"],
            [1047, 2, 2022, "D", "BC", 400.0, np.nan, 262, np.nan, np.nan, np.nan, np.nan, "0001", "Form sent out", "TY85 1ND", "CF", "D_BC", 0.0, 0.0,np.nan, np.nan, "0001", "TMI", "D_BC"],
            ]
        df = pd.DataFrame(data=data, columns=columns)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df

    def test_carry_forwards(
        self,
        dummy_CF_input,
        dummy_CF_backdata,
        expected_CF_output,
        imputation_config
        ):
        """Testing carry_forwards function on dummy data"""

        wanted_cols = ["212", "emp_total"]

        # Copy the df in preparation for new columns
        df = dummy_CF_input.copy()

        # Create new columns to hold the imputed values
        for col in wanted_cols:
            df[f"{col}_imputed"] = df[col]

        result_df = carry_forwards(
            df=df,
            backdata=dummy_CF_backdata,
            impute_vars=wanted_cols,
            config=imputation_config
        )

        # Reset index of both DataFrames to ensure they are  comparable
        result_df = result_df.reset_index(drop=True)
        expected_CF_output = expected_CF_output.reset_index(drop=True)
        assert_frame_equal(result_df, expected_CF_output, check_dtype=False)
