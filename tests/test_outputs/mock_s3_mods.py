from tests.test_outputs.singleton_moto import SingletonMoto
from io import StringIO
import logging
import pandas as pd

s3_logger = logging.getLogger(__name__)
s3_client = SingletonMoto.get_client()
s3_bucket = SingletonMoto.get_bucket()


def mock_write_csv(filepath: str, data: pd.DataFrame) -> None:
    """Write a Pandas DataFrame to CSV in an S3 bucket.

    Args:
        filepath (str): The filepath to save the DataFrame to.
        data (pd.DataFrame): The DataFrame to write to the passed path.

    Returns:
        None
    """

    # Create an Input-Output buffer
    csv_buffer = StringIO()

    # Write the DataFrame to the buffer in the CSV format
    data.to_csv(csv_buffer,
                header=True,
                date_format="%Y-%m-%d %H:%M:%S.%f+00",
                index=False)

    # "Rewind" the stream to the start of the buffer
    csv_buffer.seek(0)

    # Write the buffer into the S3 bucket
    _ = s3_client.put_object(Bucket=s3_bucket,
                             Body=csv_buffer.getvalue(),
                             Key=filepath)
    return None
