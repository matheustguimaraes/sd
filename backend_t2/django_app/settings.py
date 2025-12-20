from datetime import timedelta
from pathlib import Path
import os

# from dotenv import load_dotenv

# Carrega variáveis do .env antes de importar environment_variables
# BASE_DIR = Path(__file__).resolve().parent.parent
# env_path = BASE_DIR / '.env'
# if env_path.exists():
#     load_dotenv(env_path, override=True)

from environment_variables import (
    AWS_ACCESS_KEY_ID_ENV,
    AWS_S3_ENDPOINT_URL_ENV,
    AWS_SECRET_ACCESS_KEY_ENV,
    AWS_STORAGE_BUCKET_NAME_ENV,
    MINIO_ACCESS_URL_ENV,
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
    RABBITMQ_HOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    USE_S3_ENV,
    DEBUG_MODE,
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-mdcc-sd-dev-key-change-in-production"
DEBUG = DEBUG_MODE

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "drf_yasg",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",
    "posts_api.apps.PostsApiConfig",
    # Celery
    "django_celery_results",
    "django_celery_beat",
    "storages",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "posts_api.middleware.RequestLoggingMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_app.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": POSTGRES_DATABASE,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
        "CONN_MAX_AGE": 30,
        "CONN_HEALTH_CHECKS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_S3 = USE_S3_ENV

AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID_ENV
AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY_ENV
AWS_S3_ENDPOINT_URL = AWS_S3_ENDPOINT_URL_ENV
MINIO_ACCESS_URL = MINIO_ACCESS_URL_ENV

if USE_S3:
    # Define the URL prefix for static files
    STATIC_URL = f"{AWS_S3_ENDPOINT_URL_ENV}-static/"

    # Define the absolute path to the directory where all static files will be collected for deployment
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    # Define additional directories where Django will look for static files during development (optional)
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]

    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME_ENV
    AWS_FILE_OVERWRITE = True
    # AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }

else:
    STATIC_URL = "/staticfiles/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    # Disable CSRF for API endpoints (using JWT authentication)
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# Allow all origins for CORS
CORS_ALLOW_ALL_ORIGINS = True

# CSRF desabilitado completamente - API usa JWT authentication
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
# CSRF middleware removido, então esta configuração não é necessária
# Mas mantida para compatibilidade caso algum código ainda referencie
CSRF_TRUSTED_ORIGINS = []

# Allow CORS for media files
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=4),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=24),
    "ROTATE_REFRESH_TOKENS": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}


# Celery Configuration
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "default"
CELERY_BROKER_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}"
CELERY_RESULT_EXTENDED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TIMEZONE = "America/Sao_Paulo"

# Task Events and Monitoring
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_EVENTS = True
CELERY_SEND_EVENTS = True

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID_ENV,
            "secret_key": AWS_SECRET_ACCESS_KEY_ENV,
            "bucket_name": AWS_STORAGE_BUCKET_NAME_ENV,
            "endpoint_url": AWS_S3_ENDPOINT_URL_ENV,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID_ENV,
            "secret_key": AWS_SECRET_ACCESS_KEY_ENV,
            "bucket_name": f"{AWS_STORAGE_BUCKET_NAME_ENV}-static",
            "endpoint_url": AWS_S3_ENDPOINT_URL_ENV,
        },
    },
    "mediafiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": AWS_ACCESS_KEY_ID_ENV,
            "secret_key": AWS_SECRET_ACCESS_KEY_ENV,
            "bucket_name": f"{AWS_STORAGE_BUCKET_NAME_ENV}-media",
            "endpoint_url": AWS_S3_ENDPOINT_URL_ENV,
        },
    },
}
