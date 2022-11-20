from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Carts
from src.models import Items
from src.models import Calendars
from src.models import Reservations

from src.utils import validate_rental
from src.utils import login_required
from src.utils import create_reservation

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_FORBIDDEN,
    CODE_4_UNAUTHORIZED,
    CODE_4_NOT_FOUND,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("add", __name__)


@bp.post("/cart/add/no-reservation")
@login_required
def add_without_reservation():

    try:
        item_id = request.json["itemId"]
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

    if user_cart.id == item.lister_id:
        error = "Sorry, you cannot order your own item."
        response = make_response({ "message": error }, CODE_4_FORBIDDEN)
        return response

    if user_cart.contains(item):
        message = "Your cart already contains this item."
        response = make_response({ "message": message }, CODE_2_OK)
        return response

    user_cart.add_without_reservation(item)
    message = "The item has been added to your cart!"
    response = make_response({ "message": message }, CODE_2_OK)
    return response


@bp.post("/cart/add")
@login_required
def add():

    try:
        item_id = request.json["itemId"]
        dt_started_json = request.json["dtStarted"]
        dt_ended_json = request.json["dtEnded"]
    except KeyError:
        error = "No item added to cart. Please, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    dt_started = datetime.fromtimestamp(float(dt_started_json))
    dt_ended = datetime.fromtimestamp(float(dt_ended_json))

    item = Items.get({"id": item_id})
    user_cart = Carts.get({"id": g.user_id})

    if item is None:
        error = "Sorry, this item does not exist."
        response = make_response({ "message": error }, CODE_4_NOT_FOUND)
        return response

    if dt_started < datetime.now():
        error = "Reservations can't start in the past."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response

    if user_cart.id == item.lister_id:
        error = "Sorry, you cannot order your own item."
        response = make_response({ "message": error }, CODE_4_FORBIDDEN)
        return response

    if user_cart.contains(item):
        reserved_item_ids = user_cart.get_item_ids(reserved_only=True)
        if item.id in reserved_item_ids:
            reservation = Reservations.unique({
                "is_in_cart": True,
                "item_id": item.id,
                "renter_id": g.user_id
            })
            user_cart.remove(reservation)
        else:
            user_cart.remove_without_reservation(item)

    item_calendar = Calendars.get({"id": item.id})
    status = validate_rental(item_calendar, dt_started, dt_ended)

    reservation_data = {
        "renter_id": user_cart.id,
        "item_id": item.id,
        "dt_started": dt_started,
        "dt_ended": dt_ended
    }
    reservation = create_reservation(reservation_data)

    if status.is_successful == False:
        user_cart.add_without_reservation(item)

        error = status.message
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response

    user_cart.add(reservation)
    message = "The item has been added to your cart!"
    response = make_response({ "message": message, "est_charge": reservation.est_charge }, CODE_2_OK)
    return response
