from flask import Blueprint, make_response, request

from src.models import Carts
from src.models import Items
from src.models import Calendars
from src.models import Reservations

from src.utils import validate_rental
from src.utils import login_required
from src.utils import create_reservation

bp = Blueprint("edit", __name__)


@bp.post("/checkout/edit")
@login_required
def edit():

    try:
        item_id = request.json["itemId"]
        new_dt_started = request.json["newDtStarted"]
        new_dt_ended = request.json["newDtEnded"]
    except KeyError:
        errors = ["No item added to cart. Please, try again."]
        response = make_response({ "messages": errors }, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    item = Items.get({"id": item_id})
    user_cart = Carts.get({"id": g.user_id})

    if item is None:
        errors = ["Sorry, this item does not exist."]
        response = make_response({ "messages": errors }, 404)
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
        errors = status.messages
        response = make_response({ "messages": errors }, 401)
        return response

    user_cart.add(reservation)
    messages = ["The item has been added to your cart!"]
    response = make_response({ "messages": messages }, 200)
    return response
