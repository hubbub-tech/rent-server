from flask import Blueprint


bp = Blueprint("orders", __name__)


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


    if order.ext_date_end > order.res_date_end:
        extension_keys = {
            "order_id": order.id,
            "res_date_end": order.ext_date_end
        }
        extension = Extensions.get(extension_keys)
        early_return_date_start = extension.res_date_start
    else:
        early_return_date_start = order.res_date_start

    early_reservation_keys = {
        "renter_id": g.user_id,
        "item_id": order.item_id,
        "date_started": early_return_date_start, # will return order.res_date_end if no ext
        "date_ended": early_dt_end
    }

    create_reservation(early_reservation_keys)
    early_reservation = Reservations.get(early_reservation_keys)
    status = process_early_return(order, early_reservation)

    if status["is_successful"]:
        email_data = get_early_return_email(order, early_reservation)
        send_async_email.apply_async(kwargs=email_data)

        response = make_response({ "messages": status["messages"] }, 200)
        return response
    else:
        response = make_response({ "messages": status["messages"] }, 200)
        return response
