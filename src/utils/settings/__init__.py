import os
from celery import Celery

from .config import SMTPConfig
from .config import AWSConfig
from .config import GCloudConfig
from .config import CaptchaConfig
from .config import FlaskConfig, TestFlaskConfig

from .const import *
from .codes import *

smtp_config = SMTPConfig.get_instance()
aws_config = AWSConfig.get_instance()
gcloud_config = GCloudConfig.get_instance()

celery = Celery(__name__, broker=FlaskConfig.CELERY_BROKER_URL)

SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")
CLIENT_DOMAIN = os.getenv("CORS_ALLOW_ORIGIN")

TASK_SESSION_KEY = os.getenv("TASK_SESSION_KEY")

STRIPE_APIKEY = os.getenv("STRIPE_APIKEY")
STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET")
