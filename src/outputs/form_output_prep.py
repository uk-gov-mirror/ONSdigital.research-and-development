import pandas as pd
from src.staging.validation import flag_no_rand_spenders
from src.estimation.apply_weights import apply_weights
from src.outputs.outputs_helpers import create_period_year


def filter_outputs(df: pd.DataFrame) -> pd.DataFrame:
    """Filters the outputs based on the conditions.

    Args:
        df (pd.DataFrame): dataframe with weights computed but not applied

    Returns:
        tau_outputs_df (pd.DataFrame): dataframe filtered for output
    """
    no_rnd_spenders_filter = ~((df["604"] == "No") & (df["211"] > 0))
    nonzero_only_filter = df["211"] > 0

    conditions = no_rnd_spenders_filter & nonzero_only_filter
    output_df = df.copy().loc[conditions]

    return output_df


def form_output_prep(
    weighted_df: pd.DataFrame,
    ni_full_responses: pd.DataFrame,
    config: dict,
):
    """Prepares the data for the outputs.

    Args:
        weighted_df (pd.DataFrame): Dataset with weights computed but not applied
        ni_full_responses(pd.DataFrame): Dataset with all NI data
        config (dict): The configuration settings.

    Returns:
        ni_full_responses (pd.DataFrame): If available, prepared NI data
        outputs_df (pd.DataFrame): estimated GB data
        tau_outputs_df (pd.DataFrame): UK data without estimation weights applied
    """
    # Deal with "No" in 604, also eliminating spenders
    flag_no_rand_spenders(weighted_df, "error")

    tau_outputs_df = filter_outputs(weighted_df)
    tau_outputs_df = create_period_year(tau_outputs_df)

    # Now that the tau outputs have been created, we can apply the weights to the
    # weighted_df to get the estimated values.
    estimated_df = apply_weights(weighted_df, config, for_qa=False)

    outputs_df = filter_outputs(estimated_df)
    outputs_df = create_period_year(outputs_df)

    if ni_full_responses is not None:
        # outputs_df = pd.concat([outputs_df, ni_full_responses])
        tau_outputs_df = pd.concat([tau_outputs_df, ni_full_responses])

        return ni_full_responses, outputs_df, tau_outputs_df

    else:
        # create an empty ni_responses dataframe
        ni_full_responses = pd.DataFrame()

        return ni_full_responses, outputs_df, tau_outputs_df
