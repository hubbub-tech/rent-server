import os
import datetime

from .files import base64_to_file
from .files import upload_to_awss3

from src.models import Carts
from src.utils.settings import celery

from .safe_txns import unlock_cart


@celery.task
def set_async_timeout(user_id):
    """Background task to unlock items if user does not transact."""

    from src import create_app
    app = create_app()

    try:
        with app.app_context():
            user_cart = Carts.get({"id": user_id})
            unlock_cart(user_cart)

        dt_now = datetime.now()
        print(f"[Epoch: {datetime.timestamp(dt_now)}] All items in cart with id: {user_cart.id} have been unlocked.") # TODO: log this
        return True

    except:
        #TODO: write a proper exception handling statement here
        print("The timeout failed.")
        return False


@celery.task
def upload_file_async(filename, file_base64):

    from src import create_app
    app = create_app()

    try:
        with app.app_context():
            file, file_format = base64_to_file(file_base64)
            upload_to_awss3(file, filename, file_format)

        return True
    except:
        print("There was an error.")
        return False
