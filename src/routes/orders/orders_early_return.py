from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Items
from src.models import Orders
from src.models import Extensions
from src.models import Reservations

from src.utils import login_required
from src.utils import return_order_early

from src.utils import get_early_return_email
from src.utils import upload_email_data

from src.utils.settings import aws_config

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_FORBIDDEN,
    CODE_4_NOT_FOUND,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("early_return", __name__)


@bp.post("/orders/early-return")
@login_required
def orders_early_return():

    try:
        order_id = request.json["orderId"]
        early_dt_end_json = request.json["dtEnded"]
    except KeyError:
        error = "Please submit an early return date for your order."
        response = make_response({"message": error}, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    order = Orders.get({"id": order_id})

    early_dt_end = datetime.fromtimestamp(early_dt_end_json)
    status = return_order_early(order, early_dt_end)

    if status.is_successful:
        early_reservation = Reservations.unique({
            "renter_id": order.renter_id,
            "item_id": order.item_id,
            "dt_ended": early_dt_end,
            "is_calendared": True
        })

        email_data = get_early_return_email(order, early_reservation)
        upload_email_data(email_data, email_type="order_early_return")

        item = Items.get({ "id": order.item_id })
        item_to_dict = item.to_dict()
        item_to_dict["image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"

        data = {
            "message": status.message,
            "early_dt_end": early_dt_end_json,
            "item": item_to_dict
        }
        response = make_response(data, CODE_2_OK)
        return response
    else:
        response = make_response({ "message": status.message }, CODE_4_BAD_REQUEST)
        return response
