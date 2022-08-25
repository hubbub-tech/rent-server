from flask import Blueprint, make_response, request

from blubber_orm import Orders
from blubber_orm import Items

bp = Blueprint("history", __name__)


@bp.post("/orders/history")
@login_required
def orders_history():

    dt_started = request.args.get("dt_started")
    # NOTE: convert to a datetime object

    if not isinstance(dt_started, datetime):
        errors = ["Invalid date entry. Try again."]
        response = make_response({"messages": errors}, 404)
        return response
    elif dt_started is None:
        orders = Orders.filter({
            "renter_id": g.user_id,
            "is_canceled": False
        })
    else:
        orders = Orders.filter({
            "res_dt_start": dt_started,
            "renter_id": g.user_id,
            "is_canceled": False
        })

    if orders == []:
        errors = ["No orders yet. Check out our shop and rent!"]
        response = make_response({"messages": errors}, 200)
        return response

    orders_to_dict = []
    for order in orders:
        item = Items.get({"id": order.item_id})

        order_to_dict = order.to_dict()
        order_to_dict["item_name"] = item.name

        orders_to_dict.append(order_to_dict)

    response = make_response({ "orders": orders_to_dict }, 200)
    return response
