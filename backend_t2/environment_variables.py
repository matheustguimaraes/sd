import os


POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_DATABASE = os.environ.get("POSTGRES_DB", "mdcc_sd_db")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN", "")

DYNAMODB_REGION = os.environ.get("DYNAMODB_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "crud_logs")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD", "admin")
RABBITMQ_QUEUE_NAME = os.environ.get("RABBITMQ_QUEUE_NAME", "image-processing-queue")
RABBITMQ_QUEUE_NAME_T2 = os.environ.get("RABBITMQ_QUEUE_NAME_T2", "image-processing-queue-t2")

AWS_ACCESS_KEY_ID_ENV = os.environ.get("AWS_ACCESS_KEY_ID", "AKIA5ZWHKX42UT6RMSW6")
AWS_SECRET_ACCESS_KEY_ENV = os.environ.get("AWS_SECRET_ACCESS_KEY", "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")
AWS_STORAGE_BUCKET_NAME_ENV = os.environ.get("AWS_STORAGE_BUCKET_NAME", "mdcc-nuvem-images-t1-ufc")
AWS_S3_REGION_NAME_ENV = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_CUSTOM_DOMAIN_ENV = os.environ.get("AWS_S3_CUSTOM_DOMAIN", "mdcc-nuvem-images-t1-ufc.s3.us-east-1.amazonaws.com")
AWS_ALB_DOMAIN_ENV = os.environ.get("AWS_ALB_DOMAIN", "mdcc-nuvem-alb-1250827941.us-east-1.elb.amazonaws.com")

DYNAMODB_REGION_ENV = os.environ.get("DYNAMODB_REGION", "us-east-1")
DYNAMODB_TABLE_NAME_ENV = os.environ.get("DYNAMODB_TABLE_NAME", "crud_logs")


SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:948532068149:mdcc-nuvem-image-processing-topic")

USE_S3_ENV = os.environ.get("USE_S3", "true").upper() == "TRUE"

DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").upper() == "TRUE"
print(f"DEBUG_MODE: {os.environ.get('DEBUG_MODE')}")

SERVICE_API_TOKEN = os.environ.get("SERVICE_API_TOKEN", "mdcc-nuvem-service-token")
