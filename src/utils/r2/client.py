import os
import boto3

def client():
    R2_ENDPOINT = os.environ["R2_ENDPOINT"]
    R2_ACCESS_KEY_ID = os.environ["R2_ACCESS_KEY_ID"]
    R2_SECRET_ACCESS_KEY = os.environ["R2_SECRET_ACCESS_KEY"]
    R2_BUCKET = os.environ["R2_BUCKET"]

    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )
