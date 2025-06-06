"""
Regression test to compare two versions of outputs
Reads two csv files, old and new
Selects the columns of interest
Joins old and new on key columns, outer
Checks which records are in old only (left), new only (right) or both
Compares if the old and new values are the same within tolerance
Saves the outputs
"""

#%% Configuration settings
import pandas as pd
import numpy as np

#%%

# Input folder and file names
root_path = "R:/BERD Results System Development 2023/DAP_emulation/"
folder_path = root_path + "2023_surveys/BERD/02_freezing/frozen_data_staged/"
in_file_old = "2023_FROZEN_staged_full_responses_25-04-29_v103_new_snapshot.csv"
in_file_new = "2023_FROZEN_staged_full_responses_25-05-01_v130_all_updates.csv"

# Output folder and file
out_fol = folder_path
out_file = "staging_comparision_check.csv"

# Columns to select
key_cols = ["reference", "instance"]

value_col = "211"
other_cols = [
    "200",
    "201",
    "formtype",
    "status",
]
tolerance = 0.001
# %% Read files with selected columns only
# cols_read = key_cols + [value_col] + other_cols
# df_old = pd.read_csv((folder_path + in_file_old), usecols=cols_read, low_memory=False)
# df_new = pd.read_csv((folder_path + in_file_new), usecols=cols_read, low_memory=False)

# %% alternatively read in all columns
df_old = pd.read_csv((folder_path + in_file_old), low_memory=False)
df_new = pd.read_csv((folder_path + in_file_new), low_memory=False)
# check if the columns are the same in both dataframes
if set(df_old.columns) != set(df_new.columns):
    print("Columns are not the same in both dataframes")
    print("Items in old file not in new file:")
    print(set(df_old.columns) - set(df_new.columns))
    print("Items in new file not in old file:")
    print(set(df_new.columns) - set(df_old.columns))


# %% join old and new
df_merge = df_old.merge(df_new, on=key_cols, how="outer", suffixes=("_old", "_new"), indicator=True)

old_only = df_merge[df_merge["_merge"] == "left_only"]
new_only = df_merge[df_merge["_merge"] == "right_only"]

print(f"Number of records in old only: {len(old_only)}")
print(f"Number of records in new only: {len(new_only)}")

# %% Creating copy of df to produce a defragmented df and improve performance
df_out = df_merge.copy()

# %% Compare the values
diff = abs(df_out[value_col + "_old"].fillna(0) - df_out[value_col + "_new"].fillna(0))
df_out["value_different"] =  diff > tolerance

# %% create a boolean column to check whether any of the values in any of the columns are different
col_list = [c for c in df_old.columns if c not in key_cols]
# get a list of columns in col_list that are of type float
numeric_cols = df_old[col_list].select_dtypes(include=["float64", "float", "int64", "Int64", "int"]).columns.tolist()
non_numeric_cols = [c for c in col_list if c not in numeric_cols]

df_out["any_different"] = ""
for col in numeric_cols:
    diff = abs(df_out[col + "_old"].fillna(0) - df_out[col + "_new"].fillna(0))
    # use python "where" to udpate the any_different column with the column name if the difference is greater than tolerance
    df_out["any_different"] += np.where(diff > tolerance, col + ", ", "")

for col in non_numeric_cols:
    # use python "where" to udpate the any_different column with the column name if the values are different
    df_out["any_different"] += np.where(
        df_out[col + "_old"].fillna("") != df_out[col + "_new"].fillna(""), col + ", ", ""
    )

# remove the last comma and space from the string
df_out["any_different"] = df_out["any_different"].str.rstrip(", ")


# %% Save output
df_out.to_csv(out_fol + out_file, index=False)
