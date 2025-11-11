import json
import boto3
import os
import requests
from io import BytesIO
from PIL import Image
from botocore.exceptions import ClientError
import traceback

# environment variables
s3_client = boto3.client("s3")
s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
backend_api_url = os.environ.get("BACKEND_API_URL")
service_api_token = os.environ.get("SERVICE_API_TOKEN")


def handler(event, context):
    print(f"handler Received event: {json.dumps(event)}")

    # Process each record from the SQS
    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])

            if "Message" in body:
                message = json.loads(body["Message"])
            else:
                message = body

            print(f"Processed message: {message}")

            # Extract information from the message
            s3_key = message.get("s3_key")
            product_id = message.get("product_id")

            if not s3_key:
                print("Error: s3_key not found in message")
                continue

            process_image(s3_key, product_id)

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            traceback.print_exc()
            continue

    return {"statusCode": 200, "body": json.dumps("Images processed successfully")}


def fetch_image_from_s3(original_key: str):
    print(f"fetch_image_from_s3 Fetching image from S3: {original_key}")

    candidate_keys = [original_key]
    if not original_key.startswith("private/"):
        candidate_keys.append(f"private/{original_key}")

    last_error = None
    for candidate in candidate_keys:
        try:
            print(f"fetch_image_from_s3 Trying to fetch image from S3: {candidate}")
            response = s3_client.get_object(Bucket=s3_bucket_name, Key=candidate)
            image_bytes = response["Body"].read()
            return candidate, image_bytes
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in ("NoSuchKey", "404"):
                print(f"fetch_image_from_s3 Image not found in S3: {candidate}")
                last_error = error
                continue
            raise

    raise last_error


def process_image(s3_key, product_id):
    try:
        print(f"process_image Processing image: {s3_key}")

        resolved_key, image_data = fetch_image_from_s3(s3_key)
        print(f"process_image Resolved key: {resolved_key}")

        image = Image.open(BytesIO(image_data))
        print(f"process_image Image: {image}")

        bw_image = image.convert("L")
        print(f"process_image BW Image: {bw_image}")

        bw_image_rgb = bw_image.convert("RGB")
        print(f"process_image BW Image RGB: {bw_image_rgb}")

        output_buffer = BytesIO()
        format_ext = image.format if image.format else "JPEG"
        if format_ext not in ["JPEG", "PNG"]:
            format_ext = "JPEG"

        bw_image_rgb.save(output_buffer, format=format_ext, quality=95)
        output_buffer.seek(0)
        print(f"process_image Output buffer: {output_buffer}")

        # Generate the S3 key for the processed image
        base_key = resolved_key.rsplit(".", 1)[0] if "." in resolved_key else resolved_key
        extension = resolved_key.rsplit(".", 1)[1] if "." in resolved_key else "jpg"
        bw_s3_key = f"{base_key}_bw.{extension}"
        print(f"process_image BW S3 Key: {bw_s3_key}")

        # Faz upload da imagem processada para o S3
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=bw_s3_key,
            Body=output_buffer.getvalue(),
            ContentType=f"image/{format_ext.lower()}",
        )

        print(f"process_image Processed image saved in: {bw_s3_key}")

        if product_id:
            register_bw_image(product_id, bw_s3_key)
        else:
            print("Post without ID informed, skipping black and white image registration")

    except Exception as e:
        print(f"Error processing image {s3_key}: {str(e)}")
        traceback.print_exc()
        raise


def register_bw_image(product_id, bw_s3_key):
    print(f"process_image Registering black and white image for post {product_id} with key {bw_s3_key}")

    if not backend_api_url:
        print("BACKEND_API_URL not configured, skipping notification")
        return
    if not service_api_token:
        print("SERVICE_API_TOKEN not configured, skipping notification")
        return

    endpoint = f"{backend_api_url.rstrip('/')}/posts/{product_id}/register-bw-image/"
    print(f"process_image Endpoint: {endpoint}")

    try:
        response = requests.post(
            endpoint,
            headers={"X-Service-Token": service_api_token},
            json={"image_bw_s3_key": bw_s3_key},
            timeout=10,
        )
        response.raise_for_status()
        print(f"register_bw_image Response: {response.json()}")
        print(f"register_bw_image Response status: {response.status_code}")
        print(f"register_bw_image Black and white image registered in backend for post {product_id}")
        return True
    except Exception as error:
        print(f"Error registering black and white image in backend: {error}")
        return False
