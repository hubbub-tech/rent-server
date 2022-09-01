from flask import Blueprint, make_response, request, g

from src.models import Addresses
from src.models import Logistics

from src.utils import login_required

bp = Blueprint("cancel", __name__)


# GET or PUT or DELETE request?
@bp.get("/delivery/cancel")
@login_required
def cancel_delivery():

    logistics_id = request.args.get("logsitics_id")
    logsitics = Logistics.get({"id": logistics_id})

    if logsitics is None:
        errors = ["Sorry, we could not find this delivery. Please, try again."]
        response = make_response({ "messages": errors }, 404)
        return response

    if logsitics.receiver_id != g.user_id and logsitics.sender_id != g.user_id:
        errors = ["Sorry, you are not authorized to delete this delivery. Contact us if this seems wrong."]
        response = make_response({ "messages": errors }, 403)
        return response

    if logsitics.is_canceled:
        errors = ["Your delivery has been cancelled!"]
        response = make_response({ "messages": errors }, 403)
        return response

    courier_ids = logsitics.get_courier_ids()
    order_ids = logistics.get_order_ids()
    to_addr_pkeys = logistics.to_query_address("to")
    from_addr_pkeys = logistics.to_query_address("from")

    logistics_to_dict = logistics.to_dict()

    # START CANCELLATION SEQUENCE
    for courier_id in courier_ids:
        logsitics.remove_courier(courier_id)

    for order_id in order_ids:
        logsitics.remove_order(order_id)

    Logsitics.set({"id": logsitics.id}, {"is_canceled": True})
    # END CANCELLATION SEQUENCE

    # NOTE: email all couriers that the delivery has been cancelled
    # NOTE: email the user that their delivery has been cancelled

    to_addr = Addresses.get(to_addr_pkeys)
    from_addr = Addresses.get(from_addr_pkeys)

    messages = [f"Your delivery from {from_addr.to_str()} to {to_addr.to_str()} has been cancelled."]
    response = make_response({"messages": messages}, 200)
    return response
