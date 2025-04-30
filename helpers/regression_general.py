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

# Input folder and file names
root_path = "R:/BERD Results System Development 2023/DAP_emulation/"
folder_path = root_path + "2023_surveys/BERD/02_freezing/frozen_data_staged/"
# folder_path = root_path + "2023_surveys/BERD/10_outputs/output_tau/"
# folder_path = root_path + "2023_surveys/BERD/01_staging/staging_qa/full_responses_qa/"
in_file_old = "2023_FROZEN_staged_full_responses_25-04-29_v103_new_snapshot.csv"
in_file_new = "2023_FROZEN_staged_full_responses_25-04-29_v109_all_updates.csv"
# in_file_old = "2023_output_tau_25-04-28_v96_new_snapshot.csv"
# in_file_new = "2023_output_tau_25-04-29_v97_update_all.csv"
# in_file_old = "2023_staged_BERD_full_responses_25-04-28_v91_test.csv"
# in_file_new = "2023_staged_BERD_full_responses_25-04-28_v96.csv"

# Output folder and file
out_fol = folder_path
out_file = "staging_comparision_check2.csv"

# Columns to select
key_cols = ["reference", "instance"]
# key_cols = ["ref", "rtngrpno", "c_or_d"]
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


# df_out["any_different"] = df_out.apply(
#     lambda x: any(x[col + "_new"] != x[col + "_old"] for col in col_list), axis=1
# )

# %% Save output
df_out.to_csv(out_fol + out_file, index=False)


# %%
root_path = "R:/BERD Results System Development 2023/DAP_emulation/"
folder_path = root_path + "2023_surveys/BERD/02_freezing/freezing_updates/"
deletions_file = "2023_freezing_deletions_to_review_25-04-29_v108_all_true.csv"
additions_file = "2023_freezing_additions_to_review_25-04-29_v108_all_true.csv"
amendments_file = "2023_freezing_amendments_to_review_25-04-29_v108_all_true.csv"

# read in 3 new files
df_deletions = pd.read_csv((folder_path + deletions_file), low_memory=False)
df_additions = pd.read_csv((folder_path + additions_file), low_memory=False)
df_amendments = pd.read_csv((folder_path + amendments_file), low_memory=False)


# %%
keep_cols = ["reference", "instance", "change_type"]
merge_del = df_new.merge(df_deletions[keep_cols], on=key_cols, how="outer", indicator=True)
merge_del_both = merge_del[merge_del["_merge"] == "both"]
merge_del_left = merge_del[merge_del["_merge"] == "left_only"]
merge_del_right = merge_del[merge_del["_merge"] == "right_only"]
print(f"Number of records in deletions old only: {len(merge_del_left)}")
print(f"Number of records in deletions new only: {len(merge_del_right)}")
print(f"Number of records in deletions both: {len(merge_del_both)}")
# %%
merge_add = df_new.merge(df_additions[keep_cols], on=key_cols, how="outer", indicator=True)
merge_add_both = merge_add[merge_add["_merge"] == "both"]
merge_add_left = merge_add[merge_add["_merge"] == "left_only"]
merge_add_right = merge_add[merge_add["_merge"] == "right_only"]
print(f"Number of records in additions old only: {len(merge_add_left)}")
print(f"Number of records in additions new only: {len(merge_add_right)}")
print(f"Number of records in additions both: {len(merge_add_both)}")

# %%
merge_amend = df_new.merge(df_amendments[keep_cols], on=key_cols, how="outer", indicator=True)
merge_amend_both = merge_amend[merge_amend["_merge"] == "both"]
merge_amend_left = merge_amend[merge_amend["_merge"] == "left_only"]
merge_amend_right = merge_amend[merge_amend["_merge"] == "right_only"]
print(f"Number of records in amendments old only: {len(merge_amend_left)}")
print(f"Number of records in amendments new only: {len(merge_amend_right)}")
print(f"Number of records in amendments both: {len(merge_amend_both)}")
# %%
# %%
# check if all the items in the additions/ amendments files etc are on the old file
check_deletions = df_deletions.merge(df_old, on=key_cols, how="outer", indicator=True)
check_deletions_both = check_deletions[check_deletions["_merge"] == "both"]
check_deletions_left = check_deletions[check_deletions["_merge"] == "left_only"]
check_deletions_right = check_deletions[check_deletions["_merge"] == "right_only"]
print(f"Number of records in deletions old only: {len(check_deletions_left)}")
print(f"Number of records in deletions new only: {len(check_deletions_right)}")
print(f"Number of records in deletions both: {len(check_deletions_both)}")
# NOTE: This seems to be correct
# do the same for additions and amendments
check_additions = df_additions.merge(df_old, on=key_cols, how="outer", indicator=True)
check_additions_both = check_additions[check_additions["_merge"] == "both"]
check_additions_left = check_additions[check_additions["_merge"] == "left_only"]
check_additions_right = check_additions[check_additions["_merge"] == "right_only"]
print(f"Number of records in additions old only: {len(check_additions_left)}")
print(f"Number of records in additions new only: {len(check_additions_right)}")
print(f"Number of records in additions both: {len(check_additions_both)}")
# NOTE: This seems to be correct
# do the same for amendments
check_amendments = df_amendments.merge(df_old, on=key_cols, how="outer", indicator=True)
check_amendments_both = check_amendments[check_amendments["_merge"] == "both"]
check_amendments_left = check_amendments[check_amendments["_merge"] == "left_only"]
check_amendments_right = check_amendments[check_amendments["_merge"] == "right_only"]
print(f"Number of records in amendments old only: {len(check_amendments_left)}")
print(f"Number of records in amendments new only: {len(check_amendments_right)}")
print(f"Number of records in amendments both: {len(check_amendments_both)}")
# need to look at aditions and deletions to see if this is correct

# %% check if the items in the deletions additions/ amendments files etc are on the new file
check_deletions = df_deletions.merge(df_new, on=key_cols, how="outer", indicator=True)
check_deletions_both = check_deletions[check_deletions["_merge"] == "both"]
check_deletions_left = check_deletions[check_deletions["_merge"] == "left_only"]
check_deletions_right = check_deletions[check_deletions["_merge"] == "right_only"]
print(f"Number of records in deletions old only: {len(check_deletions_left)}")
print(f"Number of records in deletions new only: {len(check_deletions_right)}")
print(f"Number of records in deletions both: {len(check_deletions_both)}")
# NOTE: This seems to be correct
# do the same for additions and amendments
check_additions = df_additions.merge(df_new, on=key_cols, how="outer", indicator=True)
check_additions_both = check_additions[check_additions["_merge"] == "both"]
check_additions_left = check_additions[check_additions["_merge"] == "left_only"]
check_additions_right = check_additions[check_additions["_merge"] == "right_only"]
print(f"Number of records in additions old only: {len(check_additions_left)}")
print(f"Number of records in additions new only: {len(check_additions_right)}")
print(f"Number of records in additions both: {len(check_additions_both)}")
# NOTE: This seems to be correct
# do the same for amendments
check_amendments = df_amendments.merge(df_new, on=key_cols, how="outer", indicator=True)
check_amendments_both = check_amendments[check_amendments["_merge"] == "both"]
check_amendments_left = check_amendments[check_amendments["_merge"] == "left_only"]
check_amendments_right = check_amendments[check_amendments["_merge"] == "right_only"]
print(f"Number of records in amendments old only: {len(check_amendments_left)}")
print(f"Number of records in amendments new only: {len(check_amendments_right)}")
print(f"Number of records in amendments both: {len(check_amendments_both)}")


# %%
# Now focus on those rows which disagree in the old and new files
check_df = df_merge.copy()[df_merge["_merge"].isin(["left_only", "right_only"])]
# replace "left_only" with "snapshot" and "right_only" with "frozen"
check_df["_merge"] = check_df["_merge"].replace({"left_only": "snapshot", "right_only": "frozen"})
# rename indicator col
check_df.rename(columns={"_merge": "old_merge"}, inplace=True)
check_df_saved = check_df.copy()
# %%
check_and_deletions = check_df.merge(df_deletions[keep_cols], on=key_cols, how="outer", indicator=True)
check_and_deletions_both = check_and_deletions[check_and_deletions["_merge"] == "both"]
check_and_deletions_left = check_and_deletions[check_and_deletions["_merge"] == "left_only"]
check_and_deletions_right = check_and_deletions[check_and_deletions["_merge"] == "right_only"]
print(f"Number of records in deletions old only: {len(check_and_deletions_left)}")
print(f"Number of records in deletions new only: {len(check_and_deletions_right)}")
print(f"Number of records in deletions both: {len(check_and_deletions_both)}")

# %%
# do the same for additions and amendments
check_and_additions = check_df.merge(df_additions[keep_cols], on=key_cols, how="outer", indicator=True)
check_and_additions_both = check_and_additions[check_and_additions["_merge"] == "both"]
check_and_additions_left = check_and_additions[check_and_additions["_merge"] == "left_only"]
check_and_additions_right = check_and_additions[check_and_additions["_merge"] == "right_only"]
print(f"Number of records in additions old only: {len(check_and_additions_left)}")
print(f"Number of records in additions new only: {len(check_and_additions_right)}")
print(f"Number of records in additions both: {len(check_and_additions_both)}")
# NOTE: This seems to be correct
# do the same for amendments
check_and_amendments = check_df.merge(df_amendments[keep_cols], on=key_cols, how="outer", indicator=True)
check_and_amendments_both = check_and_amendments[check_and_amendments["_merge"] == "both"]
check_and_amendments_left = check_and_amendments[check_and_amendments["_merge"] == "left_only"]
check_and_amendments_right = check_and_amendments[check_and_amendments["_merge"] == "right_only"]
print(f"Number of records in amendments old only: {len(check_and_amendments_left)}")
print(f"Number of records in amendments new only: {len(check_and_amendments_right)}")
print(f"Number of records in amendments both: {len(check_and_amendments_both)}")
# NOTE: This seems to be correct
# %%
