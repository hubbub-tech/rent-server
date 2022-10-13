import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from google.oauth2 import service_account
from google.cloud import storage

from .files import base64_to_file
from src.utils.settings import celery, smtp_config, gcloud_config

from .safe_txns import unlock_cart


# NOTE: not in use
def get_available_workers():
    i = celery.control.inspect()
    available_workers = i.ping()
    return available_workers


@celery.task
def send_async_email(subject, to, body, error=None):
    msg = Mail(
        from_email=smtp_config.DEFAULT_SENDER,
        to_emails=to,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(smtp_config.SENDGRID_API_KEY)
        response = sg.send(msg)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as e:
        print(e.message)


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
def upload_file_async(uid, file_base64):

    from src import create_app
    app = create_app()

    try:
        with app.app_context():

            credentials = service_account.Credentials.from_service_account_file(
                gcloud_config.ACCESS_CREDENTIALS)

            scoped_credentials = credentials.with_scopes(
                ['https://www.googleapis.com/auth/cloud-platform'])

            bucket_name = gcloud_config.STORAGE_BUCKETS["items"]

            file, file_format = base64_to_file(file_base64)

            source_file_name = file
            destination_blob_name = f"/test/item-{uid}.jpg"

            storage_client = storage.Client(
                project=gcloud_config.PROJECT,
                credentials=scoped_credentials,
            )
            bucket = storage_client.bucket(bucket_name)
            print(bucket.name)

            blob = bucket.blob(destination_blob_name)

            blob.upload_from_string(file, content_type=file_format)
    except Exception as e:
        print(e)

    # print(file)
    return 'done!'
