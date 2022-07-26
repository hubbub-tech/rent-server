from flask import Blueprint


bp = Blueprint("schedule", __name__)


@bp.get("/schedule/dropoffs/<date_str>")
@login_required
def schedule_dropoffs(date_str):
    format = "%Y-%m-%d"
    res_date_start = datetime.strptime(date_str, format).date()
    orders = Orders.filter({
        "renter_id": g.user_id,
        "is_dropoff_sched": False,
        "res_date_start": res_date_start
    })
    if orders:
        orders_to_dropoff = []
        for order in orders:
            order_to_dict = order.to_dict()
            item = Items.get({"id": order.item_id})
            order_to_dict["item"] = item.to_dict()
            order_to_dict["reservation"] = order.reservation.to_dict()
            orders_to_dropoff.append(order_to_dict)
        return {
            "address": g.user.address.to_dict(),
            "orders_to_dropoff": orders_to_dropoff
        }
    else:
        return {"flashes": ["This dropoff date does not exist at the moment."]}, 404

@bp.post("/schedule/dropoffs/submit")
@login_required
def schedule_dropoffs_submit():
    format = "%Y-%m-%d"
    flashes = []
    data = request.json
    if data:
        logistics_data = {
            "logistics" : {
                "notes": data["notes"],
                "referral": data["referral"],
                "timeslots": ",".join(data["timesChecked"]),
                "renter_id": g.user_id,
                "chosen_time": None,
                "address_line_1": data["address"]["line_1"],
                "address_line_2": data["address"]["line_2"],
                "address_zip": data["address"]["zip"]
            },
            "address": {
                "line_1": data["address"]["line_1"],
                "line_2": data["address"]["line_2"],
                "city": data["address"]["city"],
                "state": data["address"]["state"],
                "zip": data["address"]["zip"]
            }
        }

        orders = []
        for order in data["orders"]:
            order = Orders.get({"id": order["id"]})
            orders.append(order)

        dropoff_date = datetime.strptime(data["dropoffDate"], format).date()
        if date.today() < dropoff_date:
            dropoff_logistics = create_logistics(logistics_data, orders, dropoff=dropoff_date)

            email_data = get_dropoff_email(dropoff_logistics)
            send_async_email.apply_async(kwargs=email_data)

            flashes.append("You have successfully scheduled your rental dropoffs!")
            return {"flashes": flashes}, 200
        else:
            flashes.append("You can't schedule a dropoff because the rental has already started. Email us at hubbubcu@gmail.com to manually schedule one.")
            return {"flashes": flashes}, 406
    else:
        flashes.append("Please, provide availabilities for dropoff.")
        return {"flashes": flashes}, 406
