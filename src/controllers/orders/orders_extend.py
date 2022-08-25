from flask import Blueprint, make_response, request

from src.models import Users
from src.models import Orders
from src.models import Calendars
from src.models import Reservations

from src.utils import validate_rental
from src.utils import create_reservation
from src.utils import create_extension

from src.utils import get_lister_receipt_email, get_renter_receipt_email
from src.utils import send_async_email

bp = Blueprint("extend", __name__)


@bp.post("/orders/extend/validate")
@login_required
def validate_extend_order():

    order_id = request.args.get("order_id")
    order = Orders.get({"id": order_id})
    user = Users.get({"id": g.user_id})

    if order is None:
        errors = ["We could not find the rental you're looking for."]
        response = make_response({"messages": errors}, 404)
        return response

    if order.renter_id != order.id:
        errors = ["You're not authorized to view this receipt."]
        response = make_response({"messages": errors}, 403)
        return response

    new_ext_dt_end = request.json["dtEnded"]

    item = Items.get({"id": order.item_id})
    item_calendar = Calendars.get({"id": item.id})
    form_check = validate_rental(item_calendar, order.ext_dt_end, new_ext_dt_end)

    reservation_data = {
        "renter_id": user.id,
        "item_id": item.id,
        "dt_started": order.ext_dt_end,
        "dt_ended": new_ext_dt_end
    }

    reservation = create_reservation(reservation_data)

    if status.is_successful == False:
        errors = status.messages
        response = make_response({ "messages": errors }, 401)
        return response

    if item.is_locked == False:
        item.lock(user)

        timeout_clock = datetime.now(tz=pytz.UTC) + timedelta(minutes=30)
        set_async_timeout.apply_async(eta=timeout_clock, kwargs={"user_id": user_cart.id})
    else:
        errors = ["Sorry seems like someone else is ordering this item. Try again in a few minutes."]
        response = make_response({"messages": errors}, 403)
        return response

    messages = ["Thank you! Now waiting on next steps to complete your order..."]
    response = make_response({ "messages": messages }, 200)
    # NOTE: user must pay? through processor
    return response


@bp.get("/orders/extend")
@login_required
def extend_order():

    # NOTE: make sure that these are all NOT NULL
    txn_token = request.args.get(TXN_KEY)
    order_id = request.args.get("order_id")
    new_ext_dt_end = request.args.get("dt_ended")

    order = Orders.get({"id": order_id})
    user = Users.get({"id": g.user_id})

    if order is None:
        errors = ["We could not find the rental you're looking for."]
        response = make_response({"messages": errors}, 404)
        return response

    if order.renter_id != order.id:
        errors = ["You're not authorized to view this receipt."]
        response = make_response({"messages": errors}, 403)
        return response

    reservation = Reservations.get({
        "dt_started": order.ext_dt_end,
        "dt_ended": new_ext_dt_end,
        "renter_id": user.id,
        "item_id": item.id
    })


    # test that the amount paid is accurate
    total_paid = get_charge_from_stripe(txn_token)

    est_total_paid = reservation.total()
    if total_paid != est_total_paid:
        errors = [
            "It seems that you paid the wrong amount.",
            f"You paid ${total_paid} instead of ${est_total_paid}."
        ]
        response = make_response({"messages": errors}, 401)
        return response


    item_calendar = Calendars.get({ "id": order.item_id })
    item_calendar.add(reservation)

    extension_data = {
        "res_dt_start": reservation.dt_started,
        "res_dt_end": reservation.dt_ended,
        "renter_id": reservation.renter_id,
        "item_id": reservation.item_id,
        "order_id": order.id
    }
    extension = create_extension(extension_data)

    item.unlock()
    user_cart.remove(reservation)

    email_data = get_lister_receipt_email(extension) # WARNING
    send_async_email.apply_async(kwargs=email_data)

    email_data = get_renter_receipt_email(extension)
    send_async_email.apply_async(kwargs=email_data)

    messages = ["Successfully extended your order!"]
    response = make_response({"messages": messages}, 200)
    return response
