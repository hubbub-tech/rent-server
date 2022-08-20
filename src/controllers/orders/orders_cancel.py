from flask import Blueprint, make_response, request
from datetime import datetime



bp = Blueprint("cancel", __name__)


@bp.post("/orders/cancel")
@login_required
def cancel_order():

    order_id = request.args.get("order_id")
    order = Orders.get({"id": order_id})

    if order is None:
        errors = ["Sorry, we could not find this order. Please, try again."]
        response = make_response({ "messages": errors }, 404)
        return response

    if order.renter_id != g.user_id:
        errors = ["Sorry, you are not authorized to delete this order. Contact us if this seems wrong."]
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
            dropoff.remove_order_by_id(order.id)
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
            pickup.remove_order_by_id(order.id)
            if pickup.get_order_ids() == []:
                Logsitics.set({"id": pickup.id}, {"is_canceled": True})
                # WARNING: what happens if only one order is on the delivery?

    res_pkeys = order.to_query_reservation()
    reservation = Reservations.get(res_pkeys)

    reservation.archive()
    Reservations.set(res_pkeys, {"is_calendared": False})
    Orders.set({"id": order.id}, {"is_canceled": True})
    # END ORDER CANCELLATION SEQUENCE

    email_data = get_cancellation_email(order)
    send_async_email.apply_async(kwargs=email_data)

    messages = ["Your order was successfully cancelled!"]
    response = make_response({"messages": messages}, 200)
    return response
