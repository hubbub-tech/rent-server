from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Users
from src.models import Items
from src.models import Orders
from src.models import Extensions
from src.models import Addresses

from src.utils import get_receipt
from src.utils import login_required

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_FORBIDDEN,
    CODE_4_NOT_FOUND,
)

bp = Blueprint("manage", __name__)


@bp.get('/orders/receipt')
@login_required
def download_receipt():

    order_id = request.args.get("order_id")
    order = Orders.get({"id": order_id})

    if order is None:
        error = "We could not find the rental you're looking for."
        response = make_response({"message": error}, CODE_4_NOT_FOUND)
        return response

    if order.renter_id != g.user_id:
        error = "You're not authorized to view this receipt."
        response = make_response({"message": error}, CODE_4_FORBIDDEN)
        return response

    receipt = get_receipt(order)
    response = make_response({ "receipt": receipt }, CODE_2_OK)
    return response


@bp.get('/orders/schedule')
@login_required
def get_orders_by_date():

    dt_started_json = request.args.get("dt_started")
    dt_started = None

    dt_ended_json = request.args.get("dt_ended")
    dt_ended = None

    if dt_started_json:
        dt_started = datetime.fromtimestamp(int(dt_started_json))
    elif dt_ended_json:
        dt_ended = datetime.fromtimestamp(int(dt_ended_json))
    else:
        raise Exception("Invalid date entry.")

    try:
        pass
    except:
        error = "No start or end date was provided to look up orders."
        response = make_response({"message": error}, CODE_4_BAD_REQUEST)
        return response

    orders_to_dict = []
    if dt_started:
        orders = Orders.filter({"renter_id": g.user_id, "res_dt_start": dt_started})

        for order in orders:
            item = Items.get({"id": order.item_id})

            order_to_dict = order.to_dict()
            order_to_dict["item_name"] = item.name
            order_to_dict["item_description"] = item.description
            orders_to_dict.append(order_to_dict)

    elif dt_ended:
        orders = Orders.filter({"renter_id": g.user_id, "res_dt_end": dt_ended})

        for order in orders:
            if order.res_dt_end == order.ext_dt_end:
                item = Items.get({"id": order.item_id})

                order_to_dict = order.to_dict()
                order_to_dict["item_name"] = item.name
                order_to_dict["item_description"] = item.description
                orders_to_dict.append(order_to_dict)

        extensions = Extensions.filter({ "renter_id": g.user_id, "res_dt_end": dt_ended })
        for extension in extensions:
            order = Orders.get({ "id": extension.order_id })
            if order.ext_dt_end == extension.res_dt_end:
                item = Items.get({"id": order.item_id})

                order_to_dict = order.to_dict()
                order_to_dict["item_name"] = item.name
                order_to_dict["item_description"] = item.description
                orders_to_dict.append(order_to_dict)

    data = { "orders": orders_to_dict }
    response = make_response(data, CODE_2_OK)
    return response
