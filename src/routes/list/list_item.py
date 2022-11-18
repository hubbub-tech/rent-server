from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Users

from src.utils import create_item
from src.utils import create_address

from src.utils import validate_date_range
from src.utils import login_required

from src.utils import get_new_listing_email
from src.utils import send_async_email
from src.utils import upload_file_async

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_FORBIDDEN,
    CODE_4_BAD_REQUEST,
    CODE_4_NOT_FOUND,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("list", __name__)


@bp.post('/list')
@login_required
def list_item():

    try:
        item_data = {
            "name": request.json["item"]["name"],
            "retail_price": request.json["item"]["retailPrice"],
            "description": request.json["item"]["description"],
            "lister_id": g.user_id,
            "address_lat": None,
            "address_lng": None,
        }

        address_data = {
            "lat": request.json["address"]["lat"],
            "lng": request.json["address"]["lng"],
            "formatted": request.json["address"]["formatted"],
        }

        dt_started_json = request.json["calendar"]["dtStarted"]
        dt_ended_json = request.json["calendar"]["dtEnded"]

        image_base64s = request.json["imageBase64s"]
        tags = ["all"] # request.json["tags"]

    except KeyError:
        error = "Missing data to complete your listing! Please, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    dt_started = datetime.fromtimestamp(float(dt_started_json))
    dt_ended = datetime.fromtimestamp(float(dt_ended_json))

    calendar_data = { "dt_started": dt_started, "dt_ended": dt_ended }

    user = Users.get({ "id": g.user_id })
    if user.check_role(role="listers") == False:
        error = "Sorry, you don't have authorization to list on the platform."
        response = make_response({ "message": error }, CODE_4_FORBIDDEN)
        return response

    status = validate_date_range(
        dt_lbound=calendar_data["dt_started"],
        dt_ubound=calendar_data["dt_ended"]
    )

    if not status.is_successful:
        errors = status.message
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response

    address = create_address(address_data)

    item_data["address_lat"] = address.lat
    item_data["address_lng"] = address.lng

    new_item = create_item(item_data, calendar_data, tags)

    email_data = get_new_listing_email(new_item)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    i = 0
    for image_base64 in image_base64s:
        if i == 0:
            filename = f"items/{new_item.id}.jpg"
        else:
            filename = f"items/item-{new_item.id}/{i}.jpg"

        upload_file_async.apply_async(kwargs={
            "filename": filename,
            "file_base64": image_base64
        })
        i += 1

    message = "Thanks for listing on Hubbub!"

    response = make_response({ "message": message, "item_id": new_item.id }, CODE_2_OK)
    return response
