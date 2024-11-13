"""Tests for intram_by_civil_defence.py."""
# Standard Library Imports

#Local Standard Library Imports
import pytest

#Third Party Imports
import pandas as pd
import numpy as np

# Local Imports
from src.outputs.intram_by_civil_defence import (output_intram_by_civil_defence)

class TestIntramByCivilDefence(object):
    """Test for Civil and Defence Output."""
    
    @pytest.fixture(scope="function")
    def input_data(self):
        """Input dataframes for civil_defence output"""
        columns= ["reference", "period", "200", "211"]
    
        data = [1, 2020, "C", 1000,
                2, 2020, "D", 2000,
                3, 2020, "C", nan,
                4, 2020, "D", 500,
                5, 2020, "C", 3020,
                6, 2020, "D", 40,
                7  2020, "D", 6000,
                8, 2020, "C", 700,
                9, 2020, "D", 8180,
                10, 2020, "C", 960]
        df=pd.DataFrame(data=data, columns=columns)
        return
    
    @pytest.fixture(scope="function")
    def exp_out(self:
                """Expected output for civil_defence output"""
        columns = ["200", "211"]
        data = [["Civil", 4720], ["Defence", 10720]]
        df = pd.DataFrame(data=data, columns=columns)
        return df
