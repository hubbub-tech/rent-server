from flask import Blueprint, make_response, request, g

from src.models import Carts
from src.models import Items
from src.models import Calendars
from src.models import Reservations

from src.utils import login_required

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_NOT_FOUND,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("remove", __name__)


@bp.post("/cart/remove")
@login_required
def remove():

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

    reservation = Reservations.unique({
        "renter_id": g.user_id,
        "item_id": item.id,
        "is_in_cart": True
    })

    if reservation:
        user_cart.remove(reservation)
    else:
        user_cart.remove_without_reservation(item)

    message = "This item has successfully been removed from your cart!"
    response = make_response({"message": message}, CODE_2_OK)
    return response
