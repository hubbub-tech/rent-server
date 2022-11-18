from flask import Blueprint, make_response, request, g

from src.models import Addresses
from src.models import Logistics

from src.utils import login_required

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_FORBIDDEN,
    CODE_4_NOT_FOUND
)

bp = Blueprint("cancel", __name__)


# GET or PUT or DELETE request?
@bp.get("/delivery/cancel")
@login_required
def cancel_delivery():

    logistics_id = request.args.get("logsitics_id")
    logsitics = Logistics.get({"id": logistics_id})

    if logsitics is None:
        error = "Sorry, we could not find this delivery. Please, try again."
        response = make_response({ "message": error }, CODE_4_NOT_FOUND)
        return response

    if logsitics.receiver_id != g.user_id and logsitics.sender_id != g.user_id:
        error = "Sorry, you are not authorized to delete this delivery. Contact us if this seems wrong."
        response = make_response({ "message": error }, CODE_4_FORBIDDEN)
        return response

    if logsitics.is_canceled:
        error = "Your delivery has been canceled!"
        response = make_response({ "message": error }, CODE_2_OK)
        return response

    courier_ids = logsitics.get_courier_ids()
    order_ids = logistics.get_order_ids()
    to_addr_pkeys = logistics.to_query_address("to")
    from_addr_pkeys = logistics.to_query_address("from")

    logistics_to_dict = logistics.to_dict()

    # START CANCELATION SEQUENCE
    for courier_id in courier_ids:
        logsitics.remove_courier(courier_id)

    for order_id in order_ids:
        logsitics.remove_order(order_id)

    Logsitics.set({"id": logsitics.id}, {"is_canceled": True})
    # END CANCELATION SEQUENCE

    # NOTE: email all couriers that the delivery has been canceled
    # NOTE: email the user that their delivery has been canceled

    to_addr = Addresses.get(to_addr_pkeys)
    from_addr = Addresses.get(from_addr_pkeys)

    message = f"Your delivery from {from_addr.to_str()} to {to_addr.to_str()} has been canceled."
    response = make_response({"message": message}, CODE_2_OK)
    return response
