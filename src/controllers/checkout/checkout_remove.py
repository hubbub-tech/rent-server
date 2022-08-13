from flask import Blueprint, make_response, request

from blubber_orm import Reservations
from blubber_orm import Carts
from blubber_orm import Items, Calendars


bp = Blueprint("remove", __name__)


@bp.post("/cart/remove")
@login_required
def remove():

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

    reservation = Reservations.unique({
        "renter_id": g.user_id,
        "item_id": item.id,
        "is_in_cart": True
    })

    if reservation:
        user_cart.remove(reservation)
    else:
        user_cart.remove_without_reservation(item)

    messages = ["This item has successfully been removed from your cart!"]
    response = make_response({"messages": messages}, 200)
    return response
