from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Orders
from src.models import Extensions
from src.models import Reservations

from src.utils import login_required
from src.utils import return_order_early

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
        error = "Please submit an early return date for your order."
        response = make_response({"message": error}, 401)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, 500)
        return response

    order = Orders.get({"id": order_id})

    early_dt_end = datetime.fromtimestamp(early_dt_end_json)
    status = return_order_early(order, early_dt_end)

    if status.is_successful:
        email_data = get_early_return_email(order, early_reservation)
        send_async_email.apply_async(kwargs=email_data.to_dict())

        response = make_response({ "message": status.message }, 200)
        return response
    else:
        response = make_response({ "message": status.message }, 401)
        return response
