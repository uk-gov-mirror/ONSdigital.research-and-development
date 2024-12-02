from importlib import reload
import os


def setup_environment():
    # Change to the project repository location
    my_wd = os.getcwd()
    my_repo = "research-and-development"
    if not my_wd.endswith(my_repo):
        os.chdir(my_repo)
    # Import the module after changing the directory
    import src.pipeline as src

    reload(src)
    return src


user_path = os.path.join("src", "user_config.yaml")
dev_path = os.path.join("src", "dev_config.yaml")

src = setup_environment()
run_time = src.run_pipeline(user_path, dev_path)

min_secs = divmod(round(run_time), 60)

print(f"Time taken for pipeline: {min_secs[0]} mins and {min_secs[1]} seconds")
