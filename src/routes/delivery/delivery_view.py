from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Addresses
from src.models import Logistics
from src.models import Orders
from src.models import Items

from src.utils import login_required
from src.utils.settings import aws_config

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("view", __name__)


@bp.get("/dropoffs")
@login_required
def view_dropoffs():

    dropoffs = Logistics.filter({ "receiver_id": g.user_id })

    dropoffs_to_dict = []
    for dropoff in dropoffs:
        order_ids = dropoff.get_order_ids()

        to_addr_dict = dropoff.to_query_address("to")
        to_addr = Addresses.get(to_addr_dict)

        from_addr_dict = dropoff.to_query_address("from")
        from_addr = Addresses.get(from_addr_dict)

        orders_to_dict = []
        for order_id in order_ids:
            order = Orders.get({ "id": order_id })
            item = Items.get({ "id": order.item_id })

            order_to_dict = order.to_dict()
            order_to_dict["item_name"] = item.name
            order_to_dict["item_image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"
            order_to_dict["ext_dt_end"] = datetime.timestamp(order.ext_dt_end)

            orders_to_dict.append(order_to_dict)

        dropoff_to_dict = dropoff.to_dict()
        dropoff_to_dict["orders"] = orders_to_dict

        dropoff_to_dict["to"] = to_addr.to_dict()
        dropoff_to_dict["from"] = from_addr.to_dict()

        dropoffs_to_dict.append(dropoff_to_dict)

    data = { "dropoffs": dropoffs_to_dict }
    response = make_response(data, CODE_2_OK)
    return response


@bp.get("/pickups")
@login_required
def view_pickups():

    pickups = Logistics.filter({ "sender_id": g.user_id })

    pickups_to_dict = []
    for pickup in pickups:
        order_ids = pickup.get_order_ids()

        to_addr_dict = pickup.to_query_address("to")
        to_addr = Addresses.get(to_addr_dict)

        from_addr_dict = pickup.to_query_address("from")
        from_addr = Addresses.get(from_addr_dict)

        orders_to_dict = []
        for order_id in order_ids:
            order = Orders.get({ "id": order_id })
            item = Items.get({ "id": order.item_id })

            order_to_dict = order.to_dict()
            order_to_dict["item_name"] = item.name
            order_to_dict["item_image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"
            order_to_dict["ext_dt_end"] = datetime.timestamp(order.ext_dt_end)

            orders_to_dict.append(order_to_dict)

        pickup_to_dict = pickup.to_dict()
        pickup_to_dict["orders"] = orders_to_dict

        pickup_to_dict["to"] = to_addr.to_dict()
        pickup_to_dict["from"] = from_addr.to_dict()

        pickups_to_dict.append(pickup_to_dict)

    data = { "pickups": pickups_to_dict }
    response = make_response(data, CODE_2_OK)
    return response
