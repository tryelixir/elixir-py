import os
from typing import IO, Optional
import aiohttp
import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()

print("hi!")


async def upload_stream_to_s3(
    stream: IO, presigned_url: str, content_length: int
) -> None:
    """
    Uploads a stream to an S3 bucket using a presigned URL asynchronously.

    Args:
      stream (IO): The stream to upload.
      presigned_url (str): The presigned URL for the S3 bucket.
      content_length (int): The length of the stream in bytes.

    Returns:
      None

    Raises:
      Exception: If the upload fails.
    """
    headers = {
        "content-type": "application/octet-stream",
        "content-length": str(content_length),
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(presigned_url, data=stream, headers=headers) as response:
            if response.status != 200:
                raise Exception(
                    f"Failed to upload stream: {response.status} {await response.text()}"
                )


# TODO: This should call an API endpoint, so that we don't expose our keys for AWS.
def generate_presigned_s3_url(
    bucket_name: str,
    object_name: str,
    expiration: int = 3600,
    metadata: Optional[dict] = None,
) -> str:
    """
    Generates a presigned URL for uploading an object to an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_name (str): The name of the object to be uploaded.
        expiration (int, optional): The expiration time of the presigned URL in seconds. Defaults to 3600.
        metadata (dict, optional): Additional metadata to be included with the object. Defaults to None.

    Returns:
        str: The presigned URL for uploading the object.

    Raises:
        NoCredentialsError: If the AWS credentials are not found.

    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2",
        config=Config(signature_version="s3v4"),
    )

    params = {
        "Bucket": bucket_name,
        "Key": object_name,
        "ContentType": "application/octet-stream",
    }

    if metadata:
        params["Metadata"] = metadata

    presigned_url = s3_client.generate_presigned_url(
        "put_object", Params=params, ExpiresIn=expiration
    )
    return presigned_url
