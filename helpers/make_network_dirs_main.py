"""Script that creates all directories"""
import os
import sys
my_wd = os.getcwd()
from src.utils.helpers import tree_to_list
from src.utils.local_file_mods import rd_file_exists

# Change to the project repository location
my_repo = "R:/BERD Results System Development 2023/DAP_emulation"
if not my_wd.endswith(my_repo):
    os.chdir(my_repo)


def make_dir(dir):
    """Creates a directory bassed on the provided folder_path."""
    # create directory if it does not exist

    if rd_file_exists(dir, raise_error=False) is False:
        os.makedirs(dir)
        print(f"Created {dir}")
    else:
        print(f"Directory {dir} already exists.")


def run_make_dirs(years, surveys):
    """Creates all directories based on the `tree` structure.

    tree (dict) converted to list of lists by function src.utils.helpers.tree_to_list.
    make_dir function is called for item in the list of directories. Itertates through
    years (list) and surveys (list) to create the directories for said years and
    surveys.

    """

    for year in years:
        for survey in surveys:

            tree = {
                f"{year}_surveys": {
                    f"{survey}": {
                        "01_staging": {
                            "feather": {},
                            "staging_qa": {
                                "full_responses_qa": {},
                                "postcode_validation": {},
                                "Postcodes for QA": {},
                            },
                        },
                        "02_freezing": {
                            "changes_to_review": {},
                            "freezing_updates": {},
                            "frozen_data_staged": {},
                        },
                        "03_northern_ireland": {
                            f"{year}": {},
                            "ni_staging_qa": {},
                        },
                        "04_construction": {
                            "manual_construction": {},
                        },
                        "05_mapping": {
                            "mapping_qa": {},
                        },
                        "06_imputation": {
                            "backdata_output": {},
                            "imputation_qa": {},
                            "manual_trimming": {},
                        },
                        "07_outliers": {
                            "auto_outliers": {},
                            "manual_outliers": {},
                            "outliers_qa": {},
                        },
                        "08_estimation": {
                            "estimation_qa": {},
                        },
                        "09_apportionment": {
                            "apportionment_qa": {},
                        },
                        "10_outputs": {
                            "output_frozen_group": {},
                            "output_fte_total_qa": {},
                            "output_gb_sas": {},
                            "output_intram_by_civil_defence": {},
                            "output_intram_by_pg_gb": {},
                            "output_intram_by_pg_uk": {},
                            "output_intram_by_sic": {},
                            "output_intram_gb_itl1": {},
                            "output_intram_gb_itl2": {},
                            "output_intram_totals": {},
                            "output_intram_uk_itl1": {},
                            "output_intram_uk_itl2": {},
                            "output_long_form": {},
                            "output_ni_sas": {},
                            "output_short_form": {},
                            "output_status_filtered_qa": {},
                            "output_tau": {},
                        },
                    },
                    "mappers": {
                        "v1": {},
                    }
                },
            }

            dir_list = tree_to_list(tree, prefix="", path_list=[])
            for s in dir_list:
                make_dir(s)


if __name__ == "__main__":

    years = ["2022", "2023"]
    surveys = ["BERD", "PNP"]

    run_make_dirs(years, surveys)
