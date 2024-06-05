import os
import aioboto3
from botocore.client import Config
from typing import IO
from dotenv import load_dotenv

load_dotenv()


# Initialize aioboto3 client
def _create_s3_client():
    session = aioboto3.Session()
    return session.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2",
        config=Config(signature_version="s3v4"),
    )


async def upload_stream_to_s3(session_id: str, stream: IO) -> None:
    """
    Uploads a stream to an S3 bucket.

    Args:
      session_id (str): The session ID.
      stream (IO): The stream to upload.

    Returns:
      None

    Raises:
      Exception: If the upload fails.
    """
    # TODO: This should be dynamically fetched via the API key
    bucket = "elixir-123456"

    async with _create_s3_client() as s3_client:
        await s3_client.upload_fileobj(stream, bucket, session_id)
