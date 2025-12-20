import boto3
from io import BytesIO
from PIL import Image
from botocore.exceptions import ClientError
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
import traceback

from environment_variables import (
    AWS_ACCESS_KEY_ID_ENV,
    AWS_SECRET_ACCESS_KEY_ENV,
    AWS_STORAGE_BUCKET_NAME_ENV,
    AWS_S3_REGION_NAME_ENV,
    AWS_S3_ENDPOINT_URL_ENV,
)
from posts_api.models import Posts


def get_s3_client():
    """Get S3 client with proper configuration."""
    client_kwargs = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID_ENV,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY_ENV,
        "region_name": AWS_S3_REGION_NAME_ENV,
    }

    if AWS_S3_ENDPOINT_URL_ENV:
        client_kwargs["endpoint_url"] = AWS_S3_ENDPOINT_URL_ENV

    return boto3.client("s3", **client_kwargs)


def fetch_image_from_s3(s3_key: str):
    """Fetch image from S3, trying both original key and private/ prefix."""
    s3_client = get_s3_client()
    candidate_keys = [s3_key]

    if not s3_key.startswith("private/"):
        candidate_keys.append(f"private/{s3_key}")

    last_error = None
    for candidate in candidate_keys:
        try:
            response = s3_client.get_object(Bucket=AWS_STORAGE_BUCKET_NAME_ENV, Key=candidate)
            image_bytes = response["Body"].read()
            return candidate, image_bytes
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in ("NoSuchKey", "404"):
                last_error = error
                continue
            raise

    raise last_error


@shared_task
def sum_a_and_b(a: int, b: int):
    return a + b


@shared_task
def process_image_task(s3_key: str, product_id: int = None):
    """Process image: convert to black and white and update model entry."""
    try:
        resolved_key, image_data = fetch_image_from_s3(s3_key)

        image = Image.open(BytesIO(image_data))
        bw_image = image.convert("L")
        bw_image_rgb = bw_image.convert("RGB")

        output_buffer = BytesIO()
        format_ext = image.format if image.format else "JPEG"
        if format_ext not in ["JPEG", "PNG"]:
            format_ext = "JPEG"

        bw_image_rgb.save(output_buffer, format=format_ext, quality=95)
        output_buffer.seek(0)

        base_key = resolved_key.rsplit(".", 1)[0] if "." in resolved_key else resolved_key
        extension = resolved_key.rsplit(".", 1)[1] if "." in resolved_key else "jpg"
        bw_s3_key = f"{base_key}_bw.{extension}"

        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=AWS_STORAGE_BUCKET_NAME_ENV,
            Key=bw_s3_key,
            Body=output_buffer.getvalue(),
            ContentType=f"image/{format_ext.lower()}",
        )

        if product_id:
            try:
                post = Posts.objects.get(id=product_id)
                post.image_bw_s3_key = bw_s3_key
                post.save(update_fields=["image_bw_s3_key"])
            except ObjectDoesNotExist:
                print(f"Post with id {product_id} not found")

    except Exception as e:
        print(f"Error processing image {s3_key}: {str(e)}")
        traceback.print_exc()
        raise
