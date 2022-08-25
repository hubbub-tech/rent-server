from celery import Celery

from .config import AWSConfig, SMTPConfig, FlaskConfig, TestFlaskConfig
from .const import *

AWS = AWSS3Config.get_instance()
SMTP = SMTPConfig.get_instance()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
