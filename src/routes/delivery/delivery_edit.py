from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Orders

from src.utils import get_edit_dropoff_request_email
from src.utils import get_edit_pickup_request_email
from src.utils import upload_email_data

from src.utils import create_address

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_FORBIDDEN,
    CODE_4_NOT_FOUND,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("edit", __name__)


@bp.post("/dropoff/edit")
def edit_dropoff_request():

    try:
        order_id = request.json["orderId"]
        date_dropoff_json = request.json["dateDropoff"]
        timeslots = request.json["timeslots"]

        to_address_data = {
            "lat": request.json["address"]["lat"],
            "lng": request.json["address"]["lng"],
            "formatted": request.json["address"]["formatted"]
        }

        notes = request.json.get("notes")
    except KeyError:
        error = "Sorry, you didn't send anything in the form, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    order = Orders.get({ "id": order_id })
    date_dropoff = datetime.fromtimestamp(float(date_dropoff_json))
    to_address = create_address(to_address_data)

    email_data = get_edit_dropoff_request_email(order, to_address.formatted, date_dropoff, timeslots)
    upload_email_data(email_data, email_type="dropoff_request_edit")

    message = "Your edit request has been noted! We'll reach out to you shortly with more details."
    response = make_response({ "message": message }, CODE_2_OK)
    return response



@bp.post("/pickup/edit")
def edit_pickup_request():

    try:
        order_id = request.json["orderId"]
        date_pickup_json = request.json["datePickup"]
        timeslots = request.json["timeslots"]

        from_address_data = {
            "lat": request.json["address"]["lat"],
            "lng": request.json["address"]["lng"],
            "formatted": request.json["address"]["formatted"]
        }

        notes = request.json.get("notes")
    except KeyError:
        error = "Sorry, you didn't send anything in the form, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    order = Orders.get({ "id": order_id })
    date_pickup = datetime.fromtimestamp(float(date_pickup_json))
    from_address = create_address(from_address_data)

    email_data = get_edit_pickup_request_email(order, from_address.formatted, date_pickup, timeslots)
    upload_email_data(email_data, email_type="pickup_request_edit")

    message = "Your edit request has been noted! We'll reach out to you shortly with more details."
    response = make_response({ "message": message }, CODE_2_OK)
    return response
