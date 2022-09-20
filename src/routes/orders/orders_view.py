from flask import Blueprint, make_response, request, g

from src.models import Users
from src.models import Addresses
from src.models import Items
from src.models import Calendars
from src.models import Orders, Extensions
from src.models import Reservations

from src.utils import login_required

from src.utils.settings import AWS
from src.utils.classes import Recommender

bp = Blueprint("view", __name__)

@bp.get("/order/<int:order_id>")
@login_required
def view_order(order_id):

    order = Orders.get({"id": order_id})

    if order is None:
        errors = ["This order does not exist."]
        response = make_response({"messages": errors}, 200)
        return response

    if order.renter_id != g.user_id:
        errors = ["You're not authorized to view this order."]
        response = make_response({"messages": errors}, 403)
        return response

    order_to_dict = order.to_dict()

    order_to_dict["extensions"] = []
    extensions_pkeys = order.get_extensions()
    for order_id, _, _, res_dt_start, _ in extensions_pkeys:
        extension = Extensions.get({
            "order_id": order_id,
            "res_dt_start": res_dt_start
        })
        ext_to_dict = extension.to_dict()
        order_to_dict["extensions"].append(ext_to_dict)

    item = Items.get({ "id": order.item_id })
    item_calendar = Calendars.get({"id": item.id})

    res_pkeys = order.to_query_reservation()
    res = Reservations.get(res_pkeys)

    order_to_dict["item"] = item.to_dict()
    order_to_dict["item"]["calendar"] = item_calendar.to_dict()
    order_to_dict["ext_dt_start"] = order.ext_dt_start.strftime("%Y-%m-%d")
    order_to_dict["ext_dt_end"] = order.ext_dt_end.strftime("%Y-%m-%d")
    order_to_dict["reservation"] = res.to_dict()

    data = { "order": order_to_dict }
    response = make_response(data, 200)
    return response
