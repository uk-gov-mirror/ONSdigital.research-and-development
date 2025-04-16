"""
Regression test to compare two versions of outputs
Reads two csv files, old and new
Selects the columns of interest
Joins old and new on key columns, outer
Checks which records are in old only (left), new only (right) or both
Compares if the old and new values are the same within tolerance
Saves the outputs
"""
# %% imports
import pandas as pd

#%% Configuration settings
# Input folder and file names
root_path = "R:/BERD Results System Development 2023/DAP_emulation/2023_surveys/BERD/06_imputation/imputation_qa/"
in_file_old = "2023_full_responses_imputed_25-04-16_v86.csv"
in_file_new = "2023_full_responses_imputed_25-04-16_v87.csv"

# Output folder and file
out_fol = root_path
out_file = "imputation_breakdown_check_imputed.csv"

# Columns to select
key_cols = ["reference", "instance"]
value_col = "211_imputed"
other_cols = [
    "200",
    "201",
    "formtype",
    "imp_class",
    "imp_marker",
    "status",
]

# %% Read files
cols_read = key_cols + [value_col] + other_cols
df_old = pd.read_csv((root_path + in_file_old), low_memory=False, usecols=cols_read)
df_new = pd.read_csv((root_path + in_file_new), low_memory=False, usecols=cols_read)

# %% join old and new
df_merge = df_old.merge(df_new, on=key_cols, how="outer", suffixes=("_old", "_new"))


# %% Filter good statuses only
# imp_markers_to_keep = ["TMI", "CF", "MoR", "constructed"]
# df_old_good = df_old[df_old["imp_marker"].isin(imp_markers_to_keep)]
# df_new_good = df_new[df_new["imp_marker"].isin(imp_markers_to_keep)]

# print(f"Old size: {df_old_good.shape}")
# print(f"New size: {df_new_good.shape}")

# df_merge = df_old_good.merge(
#     df_new_good, on=key_cols, how="outer", suffixes=("_old", "_new"), indicator=True
# )


# %% rename columns
# create a copy of the columns so we don't keep adding to this list each time the cell runs

cols = key_cols.copy()
for c in other_cols + [value_col]:
    cols.append(c + "_old")
    cols.append(c + "_new")


# %% Creating copy of df to produce a defragmented df and improve performance
df_out = df_merge.copy()[cols]

# %% Compare the values
df_out["abs_diffs"] = abs(
    df_out[value_col + "_old"].fillna(0) - df_out[value_col + "_new"].fillna(0)
)
df_out["value_different"] = df_out["abs_diffs"] > 0.01

# %% Save output
df_out.to_csv(out_fol + out_file, index=False)
