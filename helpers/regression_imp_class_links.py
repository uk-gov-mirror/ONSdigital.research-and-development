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
in_file_old = "PNP_2023_links_qa_25-01-14_v371_version_develop.csv"
in_file_new = "PNP_2023_links_qa_25-01-14_v373_version_1091.csv"

# Output folder and file
out_fol = root_path
out_file = "imputation_links_qa_check.csv"

# Columns to select
key_cols = ["reference"]
value_cols = [# "imp_class",
              # "reference",
              "211",
              "211_prev",
              "211_group_size",
              "211_gr",
              # "211_gr_trim",
              "211_link",
              "305",
              "305_prev",
              "305_group_size",
              "305_gr",
              # "305_gr_trim",
              "305_link",
              "emp_researcher",
              "emp_researcher_prev",
              "emp_researcher_group_size",
              "emp_researcher_gr",
              # "emp_researcher_gr_trim",
              "emp_researcher_link",
              "emp_technician",
              "emp_technician_prev",
              "emp_technician_group_size",
              "emp_technician_gr",
              # "emp_technician_gr_trim",
              "emp_technician_link",
              "emp_other",
              "emp_other_prev",
              "emp_other_group_size",
              "emp_other_gr",
              # "emp_other_gr_trim",
              "emp_other_link",
              "headcount_res_m",
              "headcount_res_m_prev",
              "headcount_res_m_group_size",
              "headcount_res_m_gr",
              # "headcount_res_m_gr_trim",
              "headcount_res_m_link",
              "headcount_res_f",
              "headcount_res_f_prev",
              "headcount_res_f_group_size",
              "headcount_res_f_gr",
              # "headcount_res_f_gr_trim",
              "headcount_res_f_link",
              "headcount_tec_m",
              "headcount_tec_m_prev",
              "headcount_tec_m_group_size",
              "headcount_tec_m_gr",
              # "headcount_tec_m_gr_trim",
              "headcount_tec_m_link",
              "headcount_tec_f",
              "headcount_tec_f_prev",
              "headcount_tec_f_group_size",
              "headcount_tec_f_gr",
              # "headcount_tec_f_gr_trim",
              "headcount_tec_f_link",
              "headcount_oth_m",
              "headcount_oth_m_prev",
              "headcount_oth_m_group_size",
              "headcount_oth_m_gr",
              # "headcount_oth_m_gr_trim",
              "headcount_oth_m_link",
              "headcount_oth_f",
              "headcount_oth_f_prev",
              "headcount_oth_f_group_size",
              "headcount_oth_f_gr",
              # "headcount_oth_f_gr_trim",
              "headcount_oth_f_link",
              "formtype"]

tolerance = 0.001
# Read files
df_old = pd.read_csv(root_path + in_file_old)
df_new = pd.read_csv(root_path + in_file_new)

# join old and new
df_merge = df_old.merge(df_new,
                        on=key_cols,
                        how="inner",
                        suffixes=("_old", "_new"))

# df_merge.to_csv(root_path + out_file, index=False)



# sizes
print(f"Old size: {df_old.shape}")
print(f"New size: {df_new.shape}")

# Join
# df_merge = df_old_good.merge(
#    df_new_good, on=key_cols, how="outer", suffixes=("_old", "_new"), indicator=True
# )
# %% Compare the values

for col in value_cols:
    df_merge[f"{col}_value_different"] = (
        df_merge[col + "_old"] - df_merge[col + "_new"]
        ) ** 2 > tolerance**2

# %% Save output
df_merge.to_csv(out_fol + out_file)
