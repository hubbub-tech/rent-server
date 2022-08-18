from flask import Blueprint

from blubber_orm import Logistics
from blubber_orm import Orders
from blubber_orm import Items

bp = Blueprint("view", __name__)


@bp.get("/dropoffs")
def view_dropoffs():

    dropoffs = Logistics.filter({ "receive_id": g.user_id })

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

            orders_to_dict.append(order_to_dict)

        dropoff_to_dict = dropoff.to_dict()
        dropoff_to_dict["orders"] = orders_to_dict

        dropoff_to_dict["to"] = to_addr.to_dict()
        dropoff_to_dict["from"] = from_addr.to_dict()

        dropoffs_to_dict.append(dropoff_to_dict)

    data = { "dropoffs": dropoffs_to_dict }
    response = make_response(data, 200)
    return response



@bp.get("/pickups")
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

            orders_to_dict.append(order_to_dict)

        pickup_to_dict = pickup.to_dict()
        pickup_to_dict["orders"] = orders_to_dict

        pickup_to_dict["to"] = to_addr.to_dict()
        pickup_to_dict["from"] = from_addr.to_dict()

        pickups_to_dict.append(pickup_to_dict)

    data = { "pickups": pickups_to_dict }
    response = make_response(data, 200)
    return response
