"""
A class that initialises a single instance of boto3 client
"""
import boto3
from moto import mock_aws

     
class SingletonMoto:
    _instance = None
    _bucket = None

    def __init__(self):
        raise RuntimeError("This is a Singleton, invoke get_client() instead.")

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            with mock_aws():
                client = boto3.client("s3", region_name="us-east-1")
                client.create_bucket(Bucket="test-bucket")
                cls._bucket = "test-bucket"
                cls._instance = client
            print(f"Initialized client: {cls._instance}")
            print(f"Initialized bucket: {cls._bucket}")
        return cls._instance

    @classmethod
    def get_bucket(cls):
        if cls._bucket is None:
            raise RuntimeError("Bucket is not set. Call get_client() first.")
        return cls._bucket
