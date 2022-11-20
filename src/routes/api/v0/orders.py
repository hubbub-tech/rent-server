from datetime import datetime
from flask import Blueprint, make_response, request

from src.models import Items
from src.models import Calendars
from src.models import Orders
from src.models import Reservations

from src.utils import login_required

from src.utils.settings import CODE_2_OK

bp = Blueprint("orders", __name__)


@bp.get("/orders")
@login_required
def get_orders():
    order_ids = request.json["ids"]

    orders_to_dict = []
    for order_id in order_ids:
        order = Orders.get({"id": order_id})

        if order is None: continue

        order_to_dict = order.to_dict()
        orders_to_dict.append(order_to_dict)

    data = { "orders": orders_to_dict }
    response = make_response(data, CODE_2_OK)
    return response


@bp.get("/order")
@login_required
def get_order():
    order_id = request.args.get("id")

    order = Orders.get({"id": order_id})

    if order is None:
        errors = ["This order does not exist."]
        response = make_response({"messages": errors}, CODE_2_OK)
        return response

    order_to_dict = order.to_dict()

    item = Items.get({ "id": order.item_id })
    item_calendar = Calendars.get({"id": item.id})

    res_pkeys = order.to_query_reservation()
    res = Reservations.get(res_pkeys)

    order_to_dict["item"] = item.to_dict()
    order_to_dict["item"]["calendar"] = item_calendar.to_dict()
    order_to_dict["ext_dt_start"] = datetime.timestamp(order.ext_dt_start)
    order_to_dict["ext_dt_end"] = datetime.timestamp(order.ext_dt_end)
    order_to_dict["reservation"] = res.to_dict()

    data = { "order": order_to_dict }
    response = make_response(data, CODE_2_OK)
    return response
