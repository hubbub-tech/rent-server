from flask import Blueprint


bp = Blueprint("orders", __name__)


@bp.post("/accounts/o/early/submit")
@login_required
def early_return_submit():
    code = 406
    flashes = []
    data = request.json
    if data:
        order_id = data["orderId"]
        order = Orders.get({"id": order_id})
        if order.ext_date_end > order.res_date_end:
            extension_keys = {
                "order_id": order.id,
                "res_date_end": order.ext_date_end
            }
            extension = Extensions.get(extension_keys)
            early_return_date_start = extension.res_date_start
        else:
            early_return_date_start = order.res_date_start
        early_return_date_end = json_date_to_python_date(data["earlyDate"])
        early_reservation_keys = {
            "renter_id": g.user_id,
            "item_id": order.item_id,
            "date_started": early_return_date_start, # will return order.res_date_end if no ext
            "date_ended": early_return_date_end
        }
        create_reservation(early_reservation_keys)
        early_reservation = Reservations.get(early_reservation_keys)
        response = process_early_return(order, early_reservation)
        if response["is_success"]:
            code = 200

            email_data = get_early_return_email(order, early_reservation)
            send_async_email.apply_async(kwargs=email_data)
        flashes.append(response["message"])
    else:
        flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, code
