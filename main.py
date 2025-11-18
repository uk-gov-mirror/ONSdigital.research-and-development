"""Script for running the pipeline."""

from importlib import reload
from r_and_d_ex import pipeline as src

reload(src)


user_path = "config/test_configs/test_user_config.yaml"
dev_path = "config/test_configs/test_dev_config.yaml"


run_time = src.run_pipeline(user_path, dev_path)

min_secs = divmod(round(run_time), 60)

print(f"Time taken for pipeline: {min_secs[0]} mins and {min_secs[1]} seconds")  # noqa
