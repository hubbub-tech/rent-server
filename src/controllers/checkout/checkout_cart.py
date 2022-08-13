from flask import Blueprint, make_response, request

from blubber_orm import Reservations
from blubber_orm import Users, Carts
from blubber_orm import Items, Calendars

# src.utils.??? import gen_token

bp = Blueprint("cart", __name__)


# *0. send checkout_session_key to client. when this is NOT NULL on frontend, order now button shows
# 1. user clicks order now and client sends checkout_session_key back, server verifies it
# 2. server locks items then checks that reservations are valid, then tells client that they are (or are not)
# 3. client receives go ahead and maybe tells user that they have X mins to pay
# 4. client gets a transaction verification token from payment processor and sends back to server
# 5. server verifies using the token that the goods were paid for--then reserves items and unlocks
# 6. confetti



@bp.get("/cart")
@login_required
def cart():
    user_cart = Carts.get({"id": g.user_id})

    item_ids = user_cart.get_item_ids()
    reserved_item_ids = user_cart.get_item_ids(reserved_only=True)

    reserved_items_to_dict = []
    unreserved_items_to_dict = []
    for item_id in item_ids:
        if item_id in reserved_item_ids:
            item_calendar = Calendars.get({"id": item_id})
            reservation = Reservations.unique({
                "renter_id": g.user_id,
                "item_id": item_id,
                "is_in_cart": True
            })

            if item_calendar.scheduler(reservation) == False:
                user_cart.remove(reservation)
                user_cart.add_without_reservation(item)
            elif reservation.is_calendared == False:
                if item_calendar.scheduler(reservation) is None:
                    Items.set({"id": item_calendar.id}, {"is_available": False})
                    user_cart.remove(reservation)
                elif item_calendar.scheduler(reservation):
                    next_start, next_end = item_calendar.next_availability()

                    item_to_dict = item.to_dict()
                    item_to_dict["calendar"] = item_calendar.to_dict()
                    item_to_dict["reservation"] = reservation.to_dict()
                    item_to_dict["calendar"]["next_available_start"] = next_start.strftime("%Y-%m-%d")
                    item_to_dict["calendar"]["next_available_end"] = next_end.strftime("%Y-%m-%d")
                    reserved_items_to_dict.append(item_to_dict)
        else:
            item_to_dict = item.to_dict()
            item_to_dict["calendar"] = item_calendar.to_dict()
            item_to_dict["calendar"]["next_available_start"] = next_start.strftime("%Y-%m-%d")
            item_to_dict["calendar"]["next_available_end"] = next_end.strftime("%Y-%m-%d")
            unreserved_items_to_dict.append(item_to_dict)

    if len(unreserved_items_to_dict) == 0:
        checkout_token = gen_token()
        Carts.set({"id": user_cart.id}, {"checkout_session_key": checkout_token["unhashed"]})
    else:
        checkout_token = None

    data = {
        "checkout_session": checkout_token,
        "reserved_items": reserved_items_to_dict,
        "unreserved_items": unreserved_items_to_dict
    }

    response = make_response(data, 200)
    return response
