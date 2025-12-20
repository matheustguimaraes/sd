import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.environ.get("POSTGRES_USER")
print(f"environment_variables.py POSTGRES_USER: {POSTGRES_USER}")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
print(f"environment_variables.py POSTGRES_HOST: {POSTGRES_HOST}")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
print(f"environment_variables.py POSTGRES_PORT: {POSTGRES_PORT}")
POSTGRES_DATABASE = os.environ.get("POSTGRES_DB")
print(f"environment_variables.py POSTGRES_DATABASE: {POSTGRES_DATABASE}")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
print(f"environment_variables.py POSTGRES_PASSWORD: {POSTGRES_PASSWORD}")

DYNAMODB_REGION = os.environ.get("DYNAMODB_REGION")
print(f"environment_variables.py DYNAMODB_REGION: {DYNAMODB_REGION}")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME")
print(f"environment_variables.py DYNAMODB_TABLE_NAME: {DYNAMODB_TABLE_NAME}")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD")
RABBITMQ_QUEUE_NAME = os.environ.get("RABBITMQ_QUEUE_NAME")
RABBITMQ_QUEUE_NAME_ENV = os.environ.get("RABBITMQ_QUEUE_NAME_ENV")

AWS_ACCESS_KEY_ID_ENV = os.environ.get("AWS_ACCESS_KEY_ID")
print(f"environment_variables.py AWS_ACCESS_KEY_ID_ENV: {AWS_ACCESS_KEY_ID_ENV}")
AWS_SECRET_ACCESS_KEY_ENV = os.environ.get("AWS_SECRET_ACCESS_KEY")
print(f"environment_variables.py AWS_SECRET_ACCESS_KEY_ENV: {AWS_SECRET_ACCESS_KEY_ENV}")
AWS_STORAGE_BUCKET_NAME_ENV = os.environ.get("AWS_STORAGE_BUCKET_NAME")
print(f"environment_variables.py AWS_STORAGE_BUCKET_NAME_ENV: {AWS_STORAGE_BUCKET_NAME_ENV}")
AWS_S3_REGION_NAME_ENV = os.environ.get("AWS_S3_REGION_NAME")
print(f"environment_variables.py AWS_S3_REGION_NAME_ENV: {AWS_S3_REGION_NAME_ENV}")
AWS_S3_CUSTOM_DOMAIN_ENV = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
print(f"environment_variables.py AWS_S3_CUSTOM_DOMAIN_ENV: {AWS_S3_CUSTOM_DOMAIN_ENV}")
AWS_ALB_DOMAIN_ENV = os.environ.get("AWS_ALB_DOMAIN")
print(f"environment_variables.py AWS_ALB_DOMAIN_ENV: {AWS_ALB_DOMAIN_ENV}")
AWS_S3_ENDPOINT_URL_ENV = os.environ.get("AWS_S3_ENDPOINT_URL")
print(f"environment_variables.py AWS_S3_ENDPOINT_URL_ENV: {AWS_S3_ENDPOINT_URL_ENV}")
MINIO_ACCESS_URL_ENV = os.environ.get("MINIO_ACCESS_URL")
print(f"environment_variables.py MINIO_ACCESS_URL_ENV: {MINIO_ACCESS_URL_ENV}")

DYNAMODB_REGION_ENV = os.environ.get("DYNAMODB_REGION")
DYNAMODB_TABLE_NAME_ENV = os.environ.get("DYNAMODB_TABLE_NAME")


SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

USE_S3_ENV = bool(os.environ.get("USE_S3"))
print(f"environment_variables.py USE_S3_ENV: {USE_S3_ENV}")

DEBUG_MODE = os.environ.get("DEBUG_MODE")
print(f"environment_variables.py DEBUG_MODE: {DEBUG_MODE}")

SERVICE_API_TOKEN = os.environ.get("SERVICE_API_TOKEN")
