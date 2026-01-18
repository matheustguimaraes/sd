import boto3
import json
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from environment_variables import (
    AWS_ACCESS_KEY_ID_ENV,
    AWS_SECRET_ACCESS_KEY_ENV,
    AWS_STORAGE_BUCKET_NAME_ENV,
    AWS_S3_REGION_NAME_ENV,
    DYNAMODB_REGION_ENV,
    DYNAMODB_TABLE_NAME_ENV,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_QUEUE_NAME_ENV,
)
import pika


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID_ENV,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ENV,
        region_name=AWS_S3_REGION_NAME_ENV,
    )


def get_s3_url(s3_key):
    if not s3_key:
        return None

    if settings.DEBUG:
        backend_url = "http://localhost:8000"
        return f"{backend_url}{settings.MEDIA_URL}{s3_key}"
    else:
        try:
            s3_client = get_s3_client()
            return s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": AWS_STORAGE_BUCKET_NAME_ENV, "Key": s3_key},
                ExpiresIn=3600,
            )
        except Exception:
            return f"https://{AWS_STORAGE_BUCKET_NAME_ENV}.s3.{AWS_S3_REGION_NAME_ENV}.amazonaws.com/{s3_key}"


def upload_to_s3(file, s3_key):
    default_storage.save(s3_key, file)
    return s3_key


def log_crud_action(action_type, model_name, data, user_id=None):
    if settings.DEBUG:
        return

    try:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=AWS_ACCESS_KEY_ID_ENV,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ENV,
            region_name=DYNAMODB_REGION_ENV,
        )

        table = dynamodb.Table(DYNAMODB_TABLE_NAME_ENV)

        log_item = {
            "id": f"{model_name}_{datetime.now().isoformat()}",
            "action_type": action_type,
            "model_name": model_name,
            "data": json.dumps(data, default=str),
            "timestamp": datetime.now().isoformat(),
            "user_id": str(user_id) if user_id else None,
        }

        table.put_item(Item=log_item)
    except Exception as e:
        print(f"Erro ao logar ação no DynamoDB: {e}")


def log_request_info(ip_address, user_id, username, path=None, method=None):
    if settings.DEBUG:
        return

    try:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=AWS_ACCESS_KEY_ID_ENV,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY_ENV,
            region_name=DYNAMODB_REGION_ENV,
        )

        table = dynamodb.Table(DYNAMODB_TABLE_NAME_ENV)

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

        table.put_item(Item=log_item)
    except Exception as e:
        print(f"Erro ao logar requisição no DynamoDB: {e}")


def publish_to_rabbitmq(message):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
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
        print(f"Erro ao publicar no RabbitMQ: {e}")
        return None
