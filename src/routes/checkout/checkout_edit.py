from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Carts
from src.models import Items
from src.models import Calendars
from src.models import Reservations

from src.utils import validate_rental
from src.utils import login_required
from src.utils import create_reservation

from src.utils import JSON_DT_FORMAT

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_FORBIDDEN,
    CODE_4_UNAUTHORIZED,
    CODE_4_NOT_FOUND,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("edit", __name__)


@bp.post("/cart/edit")
@login_required
def edit():

    try:
        item_id = request.json["itemId"]
        new_dt_started_json = request.json["dtStarted"]
        new_dt_ended_json = request.json["dtEnded"]
    except KeyError:
        error = "No item added to cart. Please, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    item = Items.get({"id": item_id})
    user_cart = Carts.get({"id": g.user_id})

    if item is None:
        error = "Sorry, this item does not exist."
        response = make_response({ "message": error }, CODE_4_NOT_FOUND)
        return response

    curr_reservation = Reservations.unique({
        "item_id": item.id,
        "renter_id": user_cart.id,
        "is_in_cart": True
    })

    if curr_reservation:
        user_cart.remove(curr_reservation)
    else:
        user_cart.remove_without_reservation(item)

    new_dt_started = datetime.fromtimestamp(float(new_dt_started_json))
    new_dt_ended = datetime.fromtimestamp(float(new_dt_ended_json))

    item_calendar = Calendars.get({"id": item.id})
    status = validate_rental(item_calendar, new_dt_started, new_dt_ended)

    reservation_data = {
        "renter_id": user_cart.id,
        "item_id": item.id,
        "dt_started": new_dt_started,
        "dt_ended": new_dt_ended
    }
    new_reservation = create_reservation(reservation_data)

    if status.is_successful == False:
        user_cart.add_without_reservation(item)

        error = status.message
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response

    user_cart.add(new_reservation)
    message = "The item has been added to your cart!"
    response = make_response({ "message": message }, CODE_2_OK)
    return response
