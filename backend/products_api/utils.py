import boto3
import json
from datetime import datetime
from django.core.files.storage import default_storage
from storages.backends.s3boto3 import S3Boto3Storage
from products_api.environment_variables import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_S3_REGION_NAME,
    DYNAMODB_REGION,
    DYNAMODB_TABLE_NAME,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_QUEUE_NAME,
    SNS_TOPIC_ARN,
    DEBUG_MODE,
)
import pika
from products_api.storage_backends import PrivateMediaStorage


class MediaStorage(S3Boto3Storage):
    """Custom S3 storage class for media files."""

    location = "media"
    default_acl = "public-read"
    file_overwrite = False


def get_s3_client():
    """Get S3 client (only used in production)."""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME,
    )


def get_s3_url(s3_key):
    """Gera signed URL para arquivo privado no S3."""
    if not s3_key:
        return None

    if not s3_key.startswith("private/"):
        s3_key = f"private/{s3_key}"

    storage = PrivateMediaStorage()
    real_key = s3_key.replace("private/", "", 1)
    return storage.url(real_key)


def upload_to_s3(file, s3_key):
    """Faz upload usando Django default storage."""
    return default_storage.save(s3_key, file)


def log_crud_action(action_type, model_name, data, user_id=None):
    """Log CRUD action to DynamoDB (only when DEBUG=False)."""
    if DEBUG_MODE:
        return  # Skip logging in development

    try:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=DYNAMODB_REGION,
        )

        table = dynamodb.Table(DYNAMODB_TABLE_NAME)

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
    """Log request information to DynamoDB (only when DEBUG=False)."""
    if DEBUG_MODE:
        return  # Skip logging in development

    try:
        dynamodb = boto3.resource(
            "dynamodb",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=DYNAMODB_REGION,
        )

        table = dynamodb.Table(DYNAMODB_TABLE_NAME)

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

        channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )

        connection.close()
        return True
    except Exception as e:
        print(f"Erro ao publicar no RabbitMQ: {e}")
        return None


def publish_to_sns(message):
    """Publica mensagem no SNS topic."""
    if not SNS_TOPIC_ARN:
        print("SNS_TOPIC_ARN não configurado, pulando publicação")
        return None

    try:
        sns_client = boto3.client(
            "sns",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION_NAME,
        )

        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN, Message=json.dumps(message), Subject="Image Processing Request"
        )

        print(f"Mensagem publicada no SNS: {response['MessageId']}")
        return response
    except Exception as e:
        print(f"Erro ao publicar no SNS: {e}")
        return None
