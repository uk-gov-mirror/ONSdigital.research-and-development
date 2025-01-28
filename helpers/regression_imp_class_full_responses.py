"""
Regression test to compare two versions of outputs
Reads two csv files, old and new
Selects the columns of interest
Joins old and new on key columns, outer
Checks which records are in old only (left), new only (right) or both
Compares if the old and new values are the same within tolerance
Saves the outputs
"""

# %% Configuration settings
import pandas as pd
# %% set filenames and paths
# Input folder and file names
survey = "BERD"
pref = ""
if survey == "PNP":
    pref = "PNP_"
root_path = f"R:/BERD Results System Development 2023/DAP_emulation/2023_surveys/{survey}/06_imputation/imputation_qa/"
in_file_old = f"{pref}2023_full_responses_imputed_25-01-28_v1028_develop.csv"
in_file_new = f"{pref}2023_full_responses_imputed_25-01-28_v1034_branch_1055.csv"

# in_file_old = f"{pref}2023_full_responses_imputed_25-01-28_v1030_develop.csv"
# in_file_new = f"{pref}2023_full_responses_imputed_25-01-28_v1029_branch_1055.csv"


# Output folder and file
out_fol = root_path
out_file = f"{survey}_imputation_qa_check_branch_1055.csv"

# %% columns to select
key_cols = ["reference", "instance"]
value_cols = ["202",
              "211",
              "emp_other",
              "emp_total",
              "202_imputed",
              "211_imputed",
              "emp_total_imputed",
            #   "202_prev",
            #   "211_prev",
            #   "emp_total_prev",
              "formtype_prev",
              "211_link",
              "emp_other_link"]

catagoricol_cols = ["imp_marker",
                    "imp_class",
                    "601",
                    "604",
]


tolerance = 0.01
# %% Read files
wanted_cols = key_cols + catagoricol_cols + value_cols
df_old = pd.read_csv(root_path + in_file_old, usecols= wanted_cols)
df_new = pd.read_csv(root_path + in_file_new, usecols= wanted_cols)

# join old and new
df_merge = df_old.merge(df_new,
                        on=key_cols,
                        how="inner",
                        suffixes=("_old", "_new"))

# %% rearrange the columns so that the old and new columns are next to each other
new_col_order = []
for col in wanted_cols:
    if col not in key_cols:  # Skip key columns as they are already merged
        new_col_order.append(col + "_old")
        new_col_order.append(col + "_new")
        if col in value_cols:
            new_col_order.append(col + "_diff")
            # round values then calc differences
            df_merge[col + "_old"] = df_merge[col + "_old"].round(0)
            df_merge[col + "_new"] = df_merge[col + "_new"].round(0)
            df_merge[col + "_diff"] = abs(df_merge[col + "_old"] - df_merge[col + "_new"])

df = df_merge[key_cols + new_col_order]
# df_merge.to_csv(root_path + out_file, index=False)

# %% Filter good statuses only
imp_markers_to_keep = ["TMI", "CF", "MoR", "constructed"]
df_old_good = df_old[df_old["imp_marker"].isin(imp_markers_to_keep)]
df_new_good = df_new[df_new["imp_marker"].isin(imp_markers_to_keep)]

# sizes
print(f"Old size: {df_old_good.shape}")
print(f"New size: {df_new_good.shape}")

# Join
# df_merge = df_old_good.merge(
#    df_new_good, on=key_cols, how="outer", suffixes=("_old", "_new"), indicator=True
# )
# %% Compare the important total values

old_211_sum = df["211_old"].sum()
new_211_sum = df["211_new"].sum()

old_211_imputed_sum = df["211_imputed_old"].sum()
new_211_imputed_sum = df["211_imputed_new"].sum()

print(f"Old 211 sum: {old_211_sum}")
print(f"New 211 sum: {new_211_sum}")
print(f"Old 211 imputed sum: {old_211_imputed_sum}")
print(f"New 211 imputed sum: {new_211_imputed_sum}")


# %% Save output
df.to_csv(out_fol + out_file, index=False)
