"""
Regression test to compare two versions of outputs
Reads two csv files, old and new
Selects the columns of interest
Joins old and new on key columns, outer
Checks which records are in old only (left), new only (right) or both
Compares if the old and new values are the same within tolerance
Saves the ouotputs
"""

#  Configuration settings
import pandas as pd

# Input folder and file names
root_path = "R:/BERD Results System Development 2023/DAP_emulation/2023_surveys/PNP/06_imputation/imputation_qa/"
in_file_old = "PNP_2023_full_responses_imputed_25-01-14_v371_version_develop.csv"
in_file_new = "PNP_2023_full_responses_imputed_25-01-14_v373_version_1091.csv"

# Output folder and file
out_fol = root_path
out_file = "imputation_qa_check.csv"

# Columns to select
key_cols = ["reference", "instance"]
value_cols = ["emp_researcher",
              "emp_researcher",
              "emp_technician",
              "emp_other",
              "emp_total",
              "headcount_res_m",
              "headcount_res_f",
              "headcount_tec_m",
              "headcount_tec_f",
              "headcount_oth_m",
              "headcount_oth_f",
              "headcount_tot_m",
              "headcount_tot_f",
              "headcount_total",
              # "imp_marker",
              "211_imputed",
              "305_imputed",
              "emp_total_imputed",
              "headcount_total_imputed",
              "202_imputed",
              "203_imputed",
              "204_imputed",
              "205_imputed",
              "206_imputed",
              "207_imputed",
              "209_imputed",
              "210_imputed",
              "212_imputed",
              "214_imputed",
              "216_imputed",
              "218_imputed",
              "219_imputed",
              "220_imputed",
              "221_imputed",
              "222_imputed",
              "223_imputed",
              "225_imputed",
              "226_imputed",
              "227_imputed",
              "228_imputed",
              "229_imputed",
              "237_imputed",
              "242_imputed",
              "243_imputed",
              "244_imputed",
              "245_imputed",
              "246_imputed",
              "247_imputed",
              "248_imputed",
              "249_imputed",
              "250_imputed",
              "302_imputed",
              "303_imputed",
              "304_imputed",
              "emp_researcher_imputed",
              "emp_technician_imputed",
              "emp_other_imputed",
              "headcount_res_m_imputed",
              "headcount_res_f_imputed",
              "headcount_tec_m_imputed",
              "headcount_tec_f_imputed",
              "headcount_oth_m_imputed",
              "headcount_oth_f_imputed",
              "headcount_tot_m_imputed",
              "headcount_tot_f_imputed",
              # "manual_trim",
              # "imp_class",
              "202_prev",
              "203_prev",
              "204_prev",
              "205_prev",
              "206_prev",
              "207_prev",
              "209_prev",
              "210_prev",
              "211_prev",
              "212_prev",
              "214_prev",
              "216_prev",
              "218_prev",
              "219_prev",
              "220_prev",
              "221_prev",
              "222_prev",
              "223_prev",
              "225_prev",
              "226_prev",
              "227_prev",
              "228_prev",
              "229_prev",
              "237_prev",
              "242_prev",
              "243_prev",
              "244_prev",
              "245_prev",
              "246_prev",
              "247_prev",
              "248_prev",
              "249_prev",
              "250_prev",
              "302_prev",
              "303_prev",
              "304_prev",
              "305_prev",
              "emp_researcher_prev",
              "emp_technician_prev",
              "emp_other_prev",
              "emp_total_prev",
              "headcount_res_m_prev",
              "headcount_res_f_prev",
              "headcount_tec_m_prev",
              "headcount_tec_f_prev",
              "headcount_oth_m_prev",
              "headcount_oth_f_prev",
              "headcount_tot_m_prev",
              "headcount_tot_f_prev",
              "headcount_total_prev",
              #"imp_class_prev",
              #"imp_marker_prev",
              "formtype_prev",
              "211_link",
              "305_link",
              "emp_researcher_link",
              "emp_technician_link",
              "emp_other_link",
              "headcount_res_m_link",
              "headcount_res_f_link",
              "headcount_tec_m_link",
              "headcount_tec_f_link",
              "headcount_oth_m_link",
              "headcount_oth_f_link"]

catagoricol_cols = ["imp_marker",
                    "manual_trim",
                    "imp_class",
                    "imp_class_prev",
                    "imp_marker_prev"]

tolerance = 0.01
# Read files
df_old = pd.read_csv(root_path + in_file_old)
df_new = pd.read_csv(root_path + in_file_new)

# join old and new
df_merge = df_old.merge(df_new,
                        on=key_cols,
                        how="inner",
                        suffixes=("_old", "_new"))

# df_merge.to_csv(root_path + out_file, index=False)

# Filter good statuses only
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
# %% Compare the values

for col in value_cols:
    df_merge[f"{col}_value_different"] = (
        df_merge[col + "_old"] - df_merge[col + "_new"]
        ) ** 2 > tolerance**2

for col in catagoricol_cols:
    df_merge[f"{col}_value_different"] = (
        df_merge[col + "_old"] != df_merge[col + "_new"]
        )

# %% Save output
df_merge.to_csv(out_fol + out_file)
