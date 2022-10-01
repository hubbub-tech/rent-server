from flask import Blueprint, make_response, request, g


from src.utils import create_item
from src.utils import create_address

from src.utils import validate_date_range
from src.utils import login_required

bp = Blueprint("list", __name__)


@bp.post('/list')
@login_required
def list_item():

    try:
        item_data = {
            "name": request.json["item"]["name"],
            "retail_price": request.json["item"]["retailPrice"],
            "description": request.json["item"]["description"],
            "weight": request.json["item"].get("weight"),
            "weight_unit": request.json["item"].get("weightUnit"),
            "dim_height": request.json["item"].get("height"),
            "dim_length": request.json["item"].get("length"),
            "dim_width": request.json["item"].get("width"),
            "manufacturer_id": request.json["item"].get("manufacturerId"),
            "lister_id": g.user_id,
            "address_lat": None,
            "address_lng": None
        }

        address_formatted = request.json["address"]["formatted"]

        address_data = {
            "lat": request.json["address"]["lat"],
            "lng": request.json["address"]["lng"]
        }

        calendar_data = {
            "dt_started": request.json["calendar"]["dtStarted"],
            "dt_ended": request.json["calendar"]["dtEnded"]
        }

        tags = ["all"] + request.json.get("tags").split()
        is_from_lister_address = strtobool(request.json["isDefaultAddress"])

    except KeyError:
        error = "Missing data to complete your listing! Please, try again."
        response = make_response({ "message": error }, 401)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, 500)
        return response

    status = validate_date_range(
        dt_lbound=calendar_data["dt_started"],
        dt_ubound=calendar_data["dt_ended"]
    )

    if not status.is_successful:
        errors = status.message
        response = make_response({ "message": error }, 403)
        return response

    address = create_address(address_data)
    new_item = create_item(item_data, calandar_data)
    email_data = get_successful_listing_email(new_item)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    message = "Thanks for listing on Hubbub!"

    response = make_response({ "message": message }, 200)
    return response
