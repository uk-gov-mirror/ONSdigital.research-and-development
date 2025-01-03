"""Main pipeline file for the exporting of files"""

import os

from importlib import reload


def setup_environment():
    # Change to the project repository location
    my_wd = os.getcwd()
    my_repo = "research-and-development"
    if not my_wd.endswith(my_repo):
        os.chdir(my_repo)
    # Import the module after changing the directory
    from src.outputs import export_files

    reload(export_files)
    return export_files


user_path = os.path.join("src", "user_config.yaml")
dev_path = os.path.join("src", "dev_config.yaml")

if __name__ == "__main__":
    export_files = setup_environment()
    export_files.run_export(user_path, dev_path)
