from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Orders
from src.models import Logistics
from src.models import Reservations


from src.utils import get_cancellation_email
from src.utils import send_async_email

from src.utils import login_required

bp = Blueprint("cancel", __name__)


@bp.get("/orders/cancel")
@login_required
def cancel_order():

    order_id = request.args.get("order_id")
    order = Orders.get({"id": order_id})

    if order is None:
        errors = ["Sorry, we could not find this order. Please, try again."]
        response = make_response({ "messages": errors }, 404)
        return response

    if order.renter_id != g.user_id:
        errors = ["Sorry, you are not authorized to cancel this order. Contact us if this seems wrong."]
        response = make_response({ "messages": errors }, 403)
        return response

    if order.res_dt_start <= datetime.now():
        errors = ["Sorry, your rental has already started. If this seems wrong, contact us."]
        response = make_response({ "messages": errors }, 401)
        return response

    if order.is_canceled:
        errors = ["Your order has been cancelled!"]
        response = make_response({ "messages": errors }, 200)
        return response

    dropoff_id = order.get_dropoff_id()
    pickup_id = order.get_pickup_id()

    # START ORDER CANCELLATION SEQUENCE
    if dropoff_id:
        dropoff = Logistics.get({"id": dropoff_id})
        if dropoff.dt_sent and dropoff.dt_received is None:
            messages = ["It seems like your order is being delivered already. If this sounds wrong please contact us."]
            response = make_response({"messages": messages}, 200)
            return response
        else:
            dropoff.remove_order(order.id)
            if dropoff.get_order_ids() == []:
                Logsitics.set({"id": dropoff.id}, {"is_canceled": True})
                # WARNING: what happens if only one order is on the delivery?

    if pickup_id:
        pickup = Logistics.get({"id": pickup_id})
        if dropoff.dt_sent and dropoff.dt_received is None:
            messages = ["It seems like your order is being delivered already. If this sounds wrong please contact us."]
            response = make_response({"messages": messages}, 200)
            return response
        else:
            pickup.remove_order(order.id)
            if pickup.get_order_ids() == []:
                Logsitics.set({"id": pickup.id}, {"is_canceled": True})
                # WARNING: what happens if only one order is on the delivery?

    res_pkeys = order.to_query_reservation()
    reservation = Reservations.get(res_pkeys)

    reservation.archive(notes="Order canceled.")
    Reservations.set(res_pkeys, {"is_calendared": False})
    Orders.set({"id": order.id}, {"is_canceled": True})
    # END ORDER CANCELLATION SEQUENCE

    email_data = get_cancellation_email(order)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    messages = ["Your order was successfully cancelled!"]
    response = make_response({"messages": messages}, 200)
    return response


@bp.post("/extensions/cancel")
@login_required
def cancel_extension():

    order_id = request.args.get("order_id")
    res_dt_start = request.args.get("res_dt_start")

    extension = Extensions.get({"id": order_id, "res_dt_start": res_dt_start})

    if extension is None:
        errors = ["Sorry, we could not find this order. Please, try again."]
        response = make_response({ "messages": errors }, 404)
        return response

    if extension.renter_id != g.user_id:
        errors = ["Sorry, you are not authorized to cancel this order. Contact us if this seems wrong."]
        response = make_response({ "messages": errors }, 403)
        return response

    if extension.res_dt_start <= datetime.now():
        errors = ["Sorry, your rental has already started. If this seems wrong, contact us."]
        response = make_response({ "messages": errors }, 401)
        return response

    res_pkeys = extension.to_query_reservation()

    reservation = Reservations.get(res_pkeys)
    if reservation.is_calendared == False:
        errors = ["Your order has been cancelled!"]
        response = make_response({ "messages": errors }, 200)
        return response

    order = Orders.get({"id": extension.order_id})
    pickup_id = order.get_pickup_id()

    # START EXTENSION CANCELLATION SEQUENCE
    if pickup_id:
        pickup = Logistics.get({"id": pickup_id})
        if dropoff.dt_sent and dropoff.dt_received is None:
            messages = ["It seems like your order is being delivered already. If this sounds wrong please contact us."]
            response = make_response({"messages": messages}, 200)
            return response
        else:
            pickup.remove_order(order.id)
            if pickup.get_order_ids() == []:
                Logsitics.set({"id": pickup.id}, {"is_canceled": True})
                # WARNING: what happens if only one order is on the delivery?

    reservation.archive(notes="Extension Canceled.")
    Reservations.set(res_pkeys, {"is_calendared": False})
    # END ORDER CANCELLATION SEQUENCE

    email_data = get_cancellation_email(extension)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    messages = ["Your extension was successfully cancelled!"]
    response = make_response({"messages": messages}, 200)
    return response
