
import os
import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from src.imputation.MoR import carry_forwards
from src.imputation.imputation_helpers import get_imputation_cols


class test_carry_forward(object):
    """Tests for carry_forwards."""

    @pytest.fixture(scope="function")
    def dummy_CF_backdata(self) -> pd.DataFrame:
        """Dummy backdata used for testing MoR imputation."""
        fpath = os.path.join("tests/data/imputation/CF_backdata.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df


    @pytest.fixture(scope="function")
    def dummy_CF_input(self) -> pd.DataFrame:
        """A dummy dataframe used for testing MoR imputation."""
        fpath = os.path.join("tests/data/imputation/CF_input_data.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df

    @pytest.fixture(scope="function")
    def expected_CF_output(self) -> pd.DataFrame:
        """Expected output from carry_forwards."""
        fpath = os.path.join("tests/data/imputation/expected_CF_output.csv")
        df = pd.read_csv(fpath)
        df = df.astype({"reference": "Int64", "instance": "Int64"})
        return df

    def test_carry_forwards(
            self,
            dummy_CF_input,
            dummy_CF_backdata,
            expected_CF_output,
            imputation_config):

        impute_vars = get_imputation_cols(imputation_config)

        result_df = carry_forwards(
            df=dummy_CF_input,
            backdata=dummy_CF_backdata,
            impute_vars=impute_vars,
            config=imputation_config
        )
        assert_frame_equal(result_df, expected_CF_output, check_dtype=False, check_exact=False)
