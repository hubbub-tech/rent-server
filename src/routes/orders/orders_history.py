from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Orders
from src.models import Items
from src.models import Reservations

from src.utils import login_required

from src.utils.settings import aws_config

bp = Blueprint("history", __name__)


@bp.get("/orders/history")
@login_required
def orders_history():

    dt_started_json = request.args.get("dt_started")

    try:
        dt_started = datetime.fromtimestamp(dt_started_json)
        orders = Orders.filter({
            "res_dt_start": dt_started,
            "renter_id": g.user_id,
            "is_canceled": False
        })
    except:
        dt_started = None
        orders = Orders.filter({
            "renter_id": g.user_id,
            "is_canceled": False
        })


    if orders == []:
        error = "No orders yet. Check out our shop and rent!"
        response = make_response({"message": error}, 200)
        return response

    orders_to_dict = []
    for order in orders:
        item = Items.get({"id": order.item_id})

        res_pkeys = order.to_query_reservation()
        res = Reservations.get(res_pkeys)

        order_to_dict = order.to_dict()

        order_to_dict["total_charge"] = order.get_total_charge()
        order_to_dict["total_deposit"] = order.get_total_deposit()

        order_to_dict["dropoff_id"] = order.get_dropoff_id()
        order_to_dict["pickup_id"] = order.get_pickup_id()

        order_to_dict["item_name"] = item.name
        order_to_dict["item_image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"
        order_to_dict["ext_dt_start"] = datetime.timestamp(order.ext_dt_start)
        order_to_dict["ext_dt_end"] = datetime.timestamp(order.ext_dt_end)
        order_to_dict["reservation"] = res.to_dict()

        orders_to_dict.append(order_to_dict)

    response = make_response({ "orders": orders_to_dict }, 200)
    return response
