from distutils.util import strtobool

from flask import Blueprint, flash, g, redirect, render_template, request, session

from blubber_orm import Users

from server.tools.settings import login_required, AWS
from server.tools.build import validate_listing, upload_image, create_item
from server.tools.build import get_new_listing_email, send_async_email
from server.tools import blubber_instances_to_dict, json_date_to_python_date

bp = Blueprint('list', __name__)

@bp.get('/list')
@login_required
def list():
    return {"address": g.user.address.to_dict()}


@bp.post('/list/submit')
@login_required
def list_submit():
    format = "%Y-%m-%d"
    flashes = []
    data = request.form
    if data:
        if data.get("startDate") and data.get("endDate"):
            new_date_started = json_date_to_python_date(data["startDate"])
            new_date_ended = json_date_to_python_date(data["endDate"])
            form_data = {
                "item": {
                    "lister_id": g.user_id,
                    "id": data.get("id"),
                    "name": data["name"],
                    "price": data["price"],
                    "address_num": data["num"],
                    "address_street": data["street"],
                    "address_apt": data["apt"],
                    "address_zip": data["zip"]
                },
                "details": {
                    "description": data["description"],
                    "condition": data["condition"],
                    "volume": data["volume"],
                    "weight": data["weight"],
                    "id": None
                },
                "calendar": {
                    "date_started": new_date_started,
                    "date_ended": new_date_ended,
                    "id": None
                },
                "address": {
                    "num": data["num"],
                    "street": data["street"],
                    "apt": data["apt"],
                    "city": data["city"],
                    "state": data["state"],
                    "zip": data["zip"]
                },
                "tags": ['all'] + data['tags'].split(","),
                "is_listed_from_user_address": strtobool(data["isDefaultAddress"])
            }
            image = request.files["image"]
            form_check = validate_listing(form_data) #validate `start` < `end` on frontend
            if form_check["is_valid"]:
                item = create_item(form_data)
                image_data = {
                    "self": item,
                    "image" : image,
                    "directory" : "items",
                    "bucket" : AWS.S3_BUCKET
                }
                upload_response = upload_image(image_data)
                if upload_response["is_valid"]:
                    email_data = get_new_listing_email(item)
                    send_async_email.apply_async(kwargs=email_data)
                    flashes.append(form_check["message"])
                    return {"flashes": flashes}, 200
                else:
                    flashes.append(upload_response["message"])
            else:
                flashes.append("There was an error getting the dates you set, make sure they're in 'MM/DD/YYYY'.")
        else:
            flashes.append("No data was sent.")
    else:
        flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, 406

#TODO: create static page for list/info
#TODO: create static page for list/complete or list/success
