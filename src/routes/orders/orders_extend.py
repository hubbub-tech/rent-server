import pytz

from datetime import datetime, timedelta
from flask import Blueprint, make_response, request, g

from src.models import Users
from src.models import Items
from src.models import Orders
from src.models import Calendars
from src.models import Reservations

from src.utils import validate_rental
from src.utils import create_reservation
from src.utils import create_extension

from src.utils import get_lister_receipt_email, get_extension_receipt_email
from src.utils import send_async_email, set_async_timeout
from src.utils import login_required, get_stripe_extension_session

from src.utils import JSON_DT_FORMAT

bp = Blueprint("extend", __name__)


@bp.post("/orders/extend/validate")
@login_required
def validate_extend_order():

    order_id = request.json["orderId"]
    new_ext_dt_end_json = request.json["dtEnded"]

    new_ext_dt_end = datetime.fromtimestamp(new_ext_dt_end_json)

    order = Orders.get({"id": order_id})
    user = Users.get({"id": g.user_id})

    if order is None:
        error = "We could not find the rental you're looking for."
        response = make_response({"message": error}, 404)
        return response

    if order.renter_id != g.user_id:
        error = "You're not authorized to extend this rental."
        response = make_response({"message": error}, 403)
        return response

    item = Items.get({"id": order.item_id})
    item_calendar = Calendars.get({"id": item.id})
    status = validate_rental(item_calendar, order.ext_dt_end, new_ext_dt_end)

    reservation_data = {
        "renter_id": user.id,
        "item_id": item.id,
        "dt_started": order.ext_dt_end,
        "dt_ended": new_ext_dt_end
    }

    reservation = create_reservation(reservation_data)

    if status.is_successful == False:
        error = status.message
        response = make_response({ "message": error }, 401)
        return response

    if item.is_locked == False:
        item.lock(user)

        timeout_clock = datetime.now(tz=pytz.UTC) + timedelta(minutes=30)
        set_async_timeout.apply_async(eta=timeout_clock, kwargs={"user_id": user.id})
    else:
        error = "Sorry seems like someone else is ordering this item. Try again in a few minutes."
        response = make_response({"message": error}, 403)
        return response

    Reservations.set(reservation_data, {"is_extension": True})
    reservation.is_extension = True

    checkout_session = get_stripe_extension_session(reservation, g.user_email)

    res_to_dict = reservation.to_dict()

    data = {
        "message": "Thank you! Now waiting on next steps to complete your order...",
        "order_id": order_id,
        "ext_dt_end": new_ext_dt_end_json,
        "redirect_url": checkout_session.url
    }

    response = make_response(data, 200)
    return response


@bp.post("/orders/extend")
@login_required
def extend_order():

    order_id = request.json["orderId"]
    ext_dt_end_json = request.json["dtEnded"]

    ext_dt_end = datetime.fromtimestamp(ext_dt_end_json)

    order = Orders.get({"id": order_id})
    if order is None:
        error = "We could not find the rental you're looking for."
        response = make_response({"message": error}, 404)
        return response

    if order.renter_id != g.user_id:
        error = "You're not authorized to view this receipt."
        response = make_response({"message": error}, 403)
        return response

    reservation = Reservations.get({
        "dt_started": order.ext_dt_end,
        "dt_ended": ext_dt_end,
        "renter_id": g.user_id,
        "item_id": order.item_id
    })

    item = Items.get({"id": order.item_id})
    item_calendar = Calendars.get({ "id": item.id })

    if reservation is None:
        if item.locker_id == g.user_id:
            item.unlock()
        error = f"Could not find the requested extension. Please contact us at {'hello@hubbub.shop'}."
        response = make_response({"message": error}, 404)
        return response

    if item.is_locked and item.locker_id == g.user_id:
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
    else:
        error = "Looks like someone else got to this one before you."
        response = make_response({"message": error}, 403)
        return response

    email_data = get_lister_receipt_email(extension) # WARNING
    send_async_email.apply_async(kwargs=email_data.to_dict())

    email_data = get_extension_receipt_email(extension)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    message = "Successfully extended your order!"
    response = make_response({"message": message}, 200)
    return response


@bp.get("/orders/extend/cancel")
@login_required
def cancel_extend_order():

    items = Items.filter({ "is_locked": True, "locker_id": g.user_id })
    for item in items:
        item.unlock()

    response = make_response({ "message": "Your extension was canceled." }, 200)
    return response
