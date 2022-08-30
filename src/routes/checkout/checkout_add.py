from flask import Blueprint, make_response, request

from src.models import Carts
from src.models import Items
from src.models import Calendars

from src.utils import validate_rental
from src.utils import login_required
from src.utils import create_reservation

bp = Blueprint("add", __name__)


@bp.post("/cart/add/no-reservation")
@login_required
def add_without_reservation():

    try:
        item_id = request.json["itemId"]
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

    if user_cart.id == item.lister_id:
        errors = ["Sorry, you cannot order your own item."]
        response = make_response({ "messages": errors }, 403)
        return response

    if user_cart.contains(item):
        messages = ["Your cart already contains this item."]
        response = make_response({"messages": messages}, 200)
        return response

    user_cart.add_without_reservation(item)
    messages = ["The item has been added to your cart!"]
    response = make_response({ "messages": messages }, 200)
    return response

@bp.post("/cart/add")
@login_required
def add():

    try:
        item_id = request.json["itemId"]
        dt_started = request.json["dtStarted"]
        dt_ended = request.json["dtEnded"]
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

    if user_cart.id == item.lister_id:
        errors = ["Sorry, you cannot order your own item."]
        response = make_response({ "messages": errors }, 403)
        return response

    if user_cart.contains(item):
        reserved_item_ids = user_cart.get_item_ids(reserved_only=True)
        if item.id in reserved_item_ids:
            messages = [
                "Your cart already contains this item.",
                "Go to your cart to edit your last reservation."
            ]
            response = make_response({"messages": messages}, 200)
            return response
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
        errors = status.messages
        response = make_response({ "messages": errors }, 401)
        return response

    user_cart.add(reservation)
    messages = ["The item has been added to your cart!"]
    response = make_response({ "messages": messages }, 200)
    return response
