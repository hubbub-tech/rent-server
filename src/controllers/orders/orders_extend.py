from flask import Blueprint


bp = Blueprint("orders", __name__)


@bp.post("/accounts/o/extend/submit")
@login_required
def extend_submit():
    code = 406
    flashes = []
    data = request.json
    if data:
        item_id = data["itemId"]
        item = Items.get({"id": item_id})
        if item.is_locked == False:
            item.lock(g.user)
            order_id = data["orderId"]
            order = Orders.get(order_id)
            ext_date_end = json_date_to_python_date(data["extendDate"])
            ext_reservation_keys = {
                "renter_id": g.user_id,
                "item_id": item.id,
                "date_started": order.ext_date_end, # will return order.res_date_end if no ext
                "date_ended": ext_date_end
            }
            ext_reservation = Reservations.get(ext_reservation_keys)
            if item.calendar.scheduler(ext_reservation):
                item.calendar.add(ext_reservation)
                ext_data = {
                    "res_date_end": ext_reservation.date_ended,
                    "res_date_start": ext_reservation.date_started,
                    "renter_id": order.renter_id,
                    "item_id": order.item_id,
                    "order_id": order_id
                }
                code = 200
                extension = create_extension(ext_data)
                flashes.append(f"Your {item.name} was successfully extended!")
            else:
                flashes.append(f"Sorry, you cannot extend this rental. It seems someone just got to the {item.name} before you.")
            item.unlock()
            if code == 200:
                email_data = get_extension_email(order, ext_reservation)
                send_async_email.apply_async(kwargs=email_data)
        else:
            flashes.append("It looks like someone else is ordering the item right now.")
    else:
        flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, code
