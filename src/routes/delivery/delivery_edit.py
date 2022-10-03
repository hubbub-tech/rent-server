from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.utils import get_edit_dropoff_request_email
from src.utils import get_edit_pickup_request_email

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
        response = make_response({ "message": error }, 406)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, 500)
        return response

    order = Orders.get({ "id": order_id })
    date_dropoff = datetime.fromtimestamp(float(date_dropoff_json))
    to_address = create_address(to_address_data)

    email_data = get_edit_dropoff_request_email(order, to_address.formatted, date_dropoff, timeslots)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    message = "Your edit request has been noted! We'll reach out to you shortly with more details."
    response = make_response({ "message": message }, 200)
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
        response = make_response({ "message": error }, 406)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, 500)
        return response

    order = Orders.get({ "id": order_id })
    date_pickup = datetime.fromtimestamp(float(date_pickup_json))
    from_address = create_address(from_address_data)

    email_data = get_edit_pickup_request_email(order, from_address.formatted, date_pickup, timeslots)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    message = "Your edit request has been noted! We'll reach out to you shortly with more details."
    response = make_response({ "message": message }, 200)
    return response
