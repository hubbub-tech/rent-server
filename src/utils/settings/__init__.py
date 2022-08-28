from celery import Celery

from .config import SMTPConfig
from .config import AWSS3Config
from .config import FlaskConfig, TestFlaskConfig

from .const import *

AWS = AWSS3Config.get_instance()
SMTP = SMTPConfig.get_instance()

celery = Celery(__name__, broker=FlaskConfig.CELERY_BROKER_URL)
