import os
from celery import Celery

from .config import SMTPConfig
from .config import AWSConfig
from .config import GCloudConfig
from .config import CaptchaConfig
from .config import FlaskConfig, TestFlaskConfig

from .const import *

smtp_config = SMTPConfig.get_instance()
aws_config = AWSConfig.get_instance()
gcloud_config = GCloudConfig.get_instance()

celery = Celery(__name__, broker=FlaskConfig.CELERY_BROKER_URL)

STRIPE_APIKEY = os.getenv("STRIPE_APIKEY")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN")
CLIENT_DOMAIN = os.getenv("CORS_ALLOW_ORIGIN")
STRIPE_ENDPOINT_SECRET = 'whsec_6a6e5a060ab28544e922a7c452d0e4a851af010e2487f1309f48f2eff50fd33b'
