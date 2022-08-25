from flask import Blueprint, make_response, response

from src.models import Orders
from src.models import Extensions
from src.models import Reservations

from src.utils import create_reservation
from src.utils import return_order_early, return_extension_early

bp = Blueprint("early_return", __name__)


@bp.post("/orders/early-return")
@login_required
def orders_early_return():

    order_id = request.args.get("order_id")
    order = Orders.get({"id": order_id})

    try:
        early_dt_end = request.json["dtEnded"]
    except KeyError:
        errors = ["Please submit an early return date for your order."]
        response = make_response({"messages": errors}, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    early_reservation_keys = {
        "renter_id": g.user_id,
        "item_id": order.item_id,
        "dt_started": order.res_dt_start,
        "dt_ended": early_dt_end
    }

    create_reservation(early_reservation_keys)
    early_reservation = Reservations.get(early_reservation_keys)
    status = return_order_early(order, early_reservation)

    if status.is_successful:
        email_data = get_early_return_email(order, early_reservation)
        send_async_email.apply_async(kwargs=email_data)

        response = make_response({ "messages": status.messages }, 200)
        return response
    else:
        response = make_response({ "messages": status.messages }, 200)
        return response



@bp.post("/extensions/early-return")
@login_required
def extensions_early_return():

    order_id = request.args.get("order_id")
    res_dt_start = request.args.get("res_dt_start")

    extension = Extensions.get({"id": order_id, "res_dt_start": res_dt_start})

    try:
        early_dt_end = request.json["dtEnded"]
    except KeyError:
        errors = ["Please submit an early return date for your order."]
        response = make_response({"messages": errors}, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    early_reservation_keys = {
        "renter_id": g.user_id,
        "item_id": extension.item_id,
        "dt_started": extension.res_dt_start,
        "dt_ended": early_dt_end
    }

    create_reservation(early_reservation_keys)
    early_reservation = Reservations.get(early_reservation_keys)
    status = return_extension_early(extension, early_reservation)

    if status.is_successful:
        email_data = get_early_return_email(extension, early_reservation)
        send_async_email.apply_async(kwargs=email_data)

        response = make_response({ "messages": status.messages }, 200)
        return response
    else:
        response = make_response({ "messages": status.messages }, 200)
        return response
