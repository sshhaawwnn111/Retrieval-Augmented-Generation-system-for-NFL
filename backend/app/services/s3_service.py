import boto3
import os
import json
from app.core.config import settings

def get_s3_data(bucket_name: str, json_file: str):
    s3 = boto3.client(
        "s3",
        region_name=settings.S3_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    response = s3.get_object(Bucket=bucket_name, Key=json_file)
    content = response["Body"].read().decode("utf-8")

    json_data = json.loads(content)
    return json_data