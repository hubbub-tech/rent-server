from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Orders
from src.models import Extensions
from src.models import Reservations

from src.utils import login_required
from src.utils import create_reservation
from src.utils import return_order_early, return_extension_early

from src.utils import get_early_return_email
from src.utils import send_async_email

from src.utils import JSON_DT_FORMAT

bp = Blueprint("early_return", __name__)


@bp.post("/orders/early-return")
@login_required
def orders_early_return():

    try:
        order_id = request.json["orderId"]
        early_dt_end_json = request.json["dtEnded"]
    except KeyError:
        errors = ["Please submit an early return date for your order."]
        response = make_response({"messages": errors}, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    order = Orders.get({"id": order_id})

    early_dt_end = datetime.strptime(early_dt_end_json, JSON_DT_FORMAT)

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
        send_async_email.apply_async(kwargs=email_data.to_dict())

        response = make_response({ "messages": status.messages }, 200)
        return response
    else:
        response = make_response({ "messages": status.messages }, 401)
        return response



@bp.post("/extensions/early-return")
@login_required
def extensions_early_return():

    try:
        order_id = request.json["orderId"]
        res_dt_start_json = request.json["dtStarted"]
        early_dt_end_json = request.json["dtEnded"]
    except KeyError:
        errors = ["Please submit an early return date for your order."]
        response = make_response({"messages": errors}, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    print(res_dt_start_json)
    res_dt_start = datetime.strptime(res_dt_start_json, '%Y-%m-%d %H:%M:%S.%f')
    early_dt_end = datetime.strptime(early_dt_end_json, JSON_DT_FORMAT)

    extension = Extensions.get({"order_id": order_id, "res_dt_start": res_dt_start})

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
        send_async_email.apply_async(kwargs=email_data.to_dict())

        response = make_response({ "messages": status.messages }, 200)
        return response
    else:
        response = make_response({ "messages": status.messages }, 200)
        return response
