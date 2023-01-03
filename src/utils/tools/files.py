import os
import json
import base64
from datetime import datetime, date

from google.oauth2 import service_account
from google.cloud import storage

from botocore.exceptions import NoCredentialsError

from src.models import Items
from src.models import Users
from src.models import Addresses
from src.models import Logistics
from src.models import Reservations

from src.utils.settings import smtp_config, gcloud_config, aws_config


def base64_to_file(file_base64):
    file_format, file_base64_stripped = file_base64.split("base64")
    file = base64.b64decode(file_base64_stripped)
    return file, file_format


# Broken
def upload_to_gcloud(file, filename, file_format):
    credentials = service_account.Credentials.from_service_account_file(
        gcloud_config.ACCESS_CREDENTIALS_PRIVATE_JSON)

    scoped_credentials = credentials.with_scopes(
        ['https://www.googleapis.com/auth/cloud-platform'])

    bucket_name = gcloud_config.STORAGE_BUCKET

    source_file_name = file
    destination_blob_name = filename

    storage_client = storage.Client(
        project=gcloud_config.PROJECT,
        credentials=scoped_credentials,
    )
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(file, content_type=file_format)



def upload_to_awss3(file, filename, file_format=None):

    s3_resource = aws_config.get_s3_resource()

    try:
        s3_resource.Bucket(aws_config.S3_BUCKET).put_object(
            Key=filename,
            Body=file,
            ACL='public-read'
        )
    except FileNotFoundError as fnf_e:
        print(fnf_e)
    except NoCredentialsError as nce_e:
        print(nce_e)


def upload_email_data(email_data: dict, email_type: str=None):
    if email_type is None: email_type = "unspecified"

    cwd = os.getcwd()
    tmp_folder = "src/tmp/"
    upload_folder = "emails/queued/"

    email_to_dict = email_data.to_dict()

    dt_now = datetime.now()
    dt_now_str = dt_now.strftime("%Y%m%d_%H%M%S")
    
    filename = f"{email_type}#{dt_now_str}.json"
    path_to_save_local = os.path.join(cwd, tmp_folder, filename)
    path_to_save_s3 = upload_folder + filename

    email_json = open(path_to_save_local, "w")
    json.dump(email_to_dict, email_json)
    email_json.close()

    client = aws_config.get_s3()
    client.upload_file(
        path_to_save_local, aws_config.S3_BUCKET, path_to_save_s3, 
        ExtraArgs={'ACL': 'public-read-write'}
    )


def get_receipt(order):
    item = Items.get({"id": order.item_id})
    lister =  Users.get({"id": item.lister_id})

    reservation_pkeys = order.to_query_reservation()
    reservation = Reservations.get(reservation_pkeys)

    receipt_text = f"""
        Rental Invoice for {item.name}\n
        \n
        Hubbub Technologies, Inc\n
        {smtp_config.DEFAULT_RECEIVER}\n\n
        \n
        Downloaded on {date.today().strftime('%Y-%m-%d')}\n
        Order Placed on {order.dt_placed.strftime('%Y-%m-%d')}\n
        \n
        Details regarding your rental of {item.name}:\n
        * Rental start date: {order.res_dt_start.strftime('%Y-%m-%d')}\n
        * Rental end date: {order.ext_dt_end.strftime('%Y-%m-%d')}\n
        \n
        * Item name: {item.name}\n
        * Item lister: {lister.name}\n
        * Rental cost: {reservation.est_charge}\n
        * Rental deposit: {reservation.est_deposit}\n
        * Tax: {reservation.est_tax}\n
        """

    dropoff_id = order.get_dropoff_id()
    pickup_id = order.get_pickup_id()

    if dropoff_id:
        dropoff = Logistics.get({"id": dropoff_id})

        to_addr_pkeys = dropoff.to_query_address("to")
        to_address = Addresses.get(to_addr_pkeys)

        if dropoff.dt_received:
            dropoff_text = f"""
                \n
                * Dropoff date: {dropoff.dt_received.strftime('%Y-%m-%d')}\n
                * Dropoff address: {to_address.formatted}\n
                """
        else:
            dropoff_text = "* Dropoff has been scheduled.\n"
    else:
        dropoff_text = "* Dropoff has not been scheduled.\n"

    if pickup_id:
        pickup = Logistics.get({"id": pickup_id})

        from_addr_pkeys = dropoff.to_query_address("from")
        from_address = Addresses.get(from_addr_pkeys)

        if pickup.dt_received:
            pickup_text = f"""
                \n
                * Pickup date: {pickup.dt_sent.strftime('%Y-%m-%d')}\n
                * Pickup address: {from_address.formatted}\n
                """
        else:
            pickup_text = "* Pickup has been scheduled.\n"
    else:
        pickup_text = "* Pickup has not been scheduled.\n"

    receipt_text += dropoff_text
    receipt_text += pickup_text

    return receipt_text
