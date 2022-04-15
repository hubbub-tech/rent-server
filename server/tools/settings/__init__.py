from celery import Celery

from .transact import exp_decay
from .transact import get_orders_for_dropoff, get_orders_for_pickup, get_delivery_schedule
from .transact import create_rental_token, verify_rental_token
from .transact import lock_checkout, check_if_routed
from .transact import process_early_return

from .utils import login_required, login_user
from .utils import create_auth_token, verify_auth_token
from .utils import generate_proposed_period
from .utils import append_sort, json_sort
from .utils import search_items, get_recommendations, get_random_testimonials

from .config import AWSConfig, MailConfig, Config, TestConfig

from .const import *

AWS = AWSConfig.get_instance()
SG = MailConfig.get_instance()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
