import boto3
import json
from datetime import datetime
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage
from posts_api.environment_variables import (
    AWS_ACCESS_KEY_ID_ENV,
    AWS_SECRET_ACCESS_KEY_ENV,
    AWS_S3_REGION_NAME_ENV,
    DYNAMODB_REGION_ENV,
    DYNAMODB_TABLE_NAME_ENV,
    RABBITMQ_HOST,
    RABBITMQ_PORT_ENV,
    RABBITMQ_USER_ENV,
    RABBITMQ_PASSWORD_ENV,
    RABBITMQ_QUEUE_NAME_ENV,
    SNS_TOPIC_ARN,
    DEBUG_MODE,
)
import pika
from posts_api.storage_backends import PrivateMediaStorage
import traceback


class MediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID_ENV,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ENV,
        region_name=AWS_S3_REGION_NAME_ENV,
    )


def get_s3_url(s3_key):
    print(f"get_s3_url s3_key: {s3_key}")
    if not s3_key:
        return None

    if not s3_key.startswith("private/"):
        s3_key = f"private/{s3_key}"

    storage = PrivateMediaStorage()
    real_key = s3_key.replace("private/", "", 1)
    return storage.url(real_key)


def upload_to_s3(file, s3_key):
    print(f"upload_to_s3 file: {file}")
    print(f"upload_to_s3 s3_key: {s3_key}")

    return default_storage.save(s3_key, file)


def log_crud_action(action_type, model_name, data, user_id=None):
    if DEBUG_MODE:
        print(f"log_crud_action DEBUG: {DEBUG_MODE}")
        return

    try:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=AWS_ACCESS_KEY_ID_ENV,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ENV,
            region_name=DYNAMODB_REGION_ENV,
        )
        print(f"log_crud_action dynamodb: {dynamodb}")

        table = dynamodb.Table(DYNAMODB_TABLE_NAME_ENV)
        print(f"log_crud_action table: {table}")

        log_item = {
            "id": f"{model_name}_{datetime.now().isoformat()}",
            "action_type": action_type,
            "model_name": model_name,
            "data": json.dumps(data, default=str),
            "timestamp": datetime.now().isoformat(),
            "user_id": str(user_id) if user_id else None,
        }
        print(f"log_crud_action log_item: {log_item}")

        table.put_item(Item=log_item)
        print(f"log_crud_action table.put_item: {table.put_item}")

    except Exception as e:
        print(f"log_crud_action error: {e}")
        traceback.print_exc()


def log_request_info(ip_address, user_id, username, path=None, method=None):
    if DEBUG_MODE:
        print(f"log_request_info DEBUG: {DEBUG_MODE}")
        return

    try:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=AWS_ACCESS_KEY_ID_ENV,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ENV,
            region_name=DYNAMODB_REGION_ENV,
        )
        print(f"log_request_info dynamodb: {dynamodb}")

        table = dynamodb.Table(DYNAMODB_TABLE_NAME_ENV)
        print(f"log_request_info table: {table}")

        log_item = {
            "id": f"REQUEST_{datetime.now().isoformat()}",
            "action_type": "REQUEST",
            "model_name": "System",
            "ip_address": ip_address,
            "user_id": str(user_id) if user_id else None,
            "username": username if username else None,
            "path": path if path else None,
            "method": method if method else None,
            "timestamp": datetime.now().isoformat(),
        }
        print(f"log_request_info log_item: {log_item}")
        table.put_item(Item=log_item)
        print(f"log_request_info table.put_item: {table.put_item}")

    except Exception as e:
        print(f"log_request_info error: {e}")
        traceback.print_exc()


def publish_to_rabbitmq(message):
    print(f"publish_to_rabbitmq message: {message}")

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT_ENV,
                credentials=pika.PlainCredentials(RABBITMQ_USER_ENV, RABBITMQ_PASSWORD_ENV),
            )
        )
        channel = connection.channel()

        channel.queue_declare(queue=RABBITMQ_QUEUE_NAME_ENV, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE_NAME_ENV,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )

        connection.close()
        return True
    except Exception as e:
        print(f"publish_to_rabbitmq error: {e}")
        traceback.print_exc()
        return None


def publish_to_sns(message):
    print(f"publish_to_sns message: {message}")

    if not SNS_TOPIC_ARN:
        print("publish_to_sns error: SNS_TOPIC_ARN not configured, skipping publication")
        return None

    try:
        sns_client = boto3.client(
            "sns",
            aws_access_key_id=AWS_ACCESS_KEY_ID_ENV,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ENV,
            region_name=AWS_S3_REGION_NAME_ENV,
        )

        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN, Message=json.dumps(message), Subject="Image Processing Request"
        )

        print(f"publish_to_sns response: {response['MessageId']}")
        return response
    except Exception as e:
        print(f"publish_to_sns error: {e}")
        traceback.print_exc()
        return None
