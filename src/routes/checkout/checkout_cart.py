from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Users
from src.models import Carts
from src.models import Items
from src.models import Calendars
from src.models import Reservations

from src.utils import gen_token
from src.utils import login_required

from src.utils.settings import aws_config

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
        item = Items.get({"id": item_id})
        item_calendar = Calendars.get({"id": item.id})

        if item_id in reserved_item_ids:
            res = Reservations.unique({
                "renter_id": g.user_id,
                "item_id": item_id,
                "is_in_cart": True
            })

            if item_calendar.check_reservation(res.dt_started, res.dt_ended) == False:
                user_cart.remove(res)
                user_cart.add_without_reservation(item)

                next_start, next_end = item_calendar.next_availability()

                item_to_dict = item.to_dict()
                item_to_dict["calendar"] = item_calendar.to_dict()
                item_to_dict["calendar"]["next_available_start"] = datetime.timestamp(next_start)
                item_to_dict["calendar"]["next_available_end"] = datetime.timestamp(next_end)

                item_to_dict["image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"
                unreserved_items_to_dict.append(item_to_dict)

            elif res.is_calendared == False:
                if item_calendar.check_reservation(res.dt_started, res.dt_ended) is None:
                    Items.set({"id": item_calendar.id}, {"is_available": False})
                    user_cart.remove(res)
                elif item_calendar.check_reservation(res.dt_started, res.dt_ended):
                    next_start, next_end = item_calendar.next_availability()

                    item_to_dict = item.to_dict()
                    item_to_dict["calendar"] = item_calendar.to_dict()
                    item_to_dict["reservation"] = res.to_dict()
                    item_to_dict["calendar"]["next_available_start"] = datetime.timestamp(next_start)
                    item_to_dict["calendar"]["next_available_end"] = datetime.timestamp(next_end)

                    item_to_dict["image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"
                    reserved_items_to_dict.append(item_to_dict)
        else:
            next_start, next_end = item_calendar.next_availability()

            item_to_dict = item.to_dict()
            item_to_dict["calendar"] = item_calendar.to_dict()
            item_to_dict["calendar"]["next_available_start"] = datetime.timestamp(next_start)
            item_to_dict["calendar"]["next_available_end"] = datetime.timestamp(next_end)

            item_to_dict["image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"
            unreserved_items_to_dict.append(item_to_dict)

    if len(unreserved_items_to_dict) == 0:
        checkout_token = gen_token()
        checkout_token_unhashed = checkout_token["unhashed"]
        Carts.set({"id": user_cart.id}, {"checkout_session_key": checkout_token_unhashed})
    else:
        checkout_token_unhashed = None

    cart_to_dict = user_cart.to_dict()
    cart_to_dict["checkout_session_key"] = checkout_token_unhashed
    data = {
        "cart": cart_to_dict,
        "reserved_items": reserved_items_to_dict,
        "unreserved_items": unreserved_items_to_dict
    }

    response = make_response(data, 200)
    return response
