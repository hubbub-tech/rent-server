@bp.get("/schedule/pickups/<date_str>")
@login_required
def schedule_pickups(date_str):
    format = "%Y-%m-%d"
    res_date_end = datetime.strptime(date_str, format).date()
    orders = Orders.filter({"renter_id": g.user_id, "is_pickup_sched": False})
    if orders:
        orders_to_pickup = []
        for order in orders:
            if order.ext_date_end == res_date_end:
                order_to_dict = order.to_dict()
                item = Items.get({"id": order.item_id})
                order_to_dict["item"] = item.to_dict()
                order_to_dict["reservation"] = order.reservation.to_dict()
                orders_to_pickup.append(order_to_dict)
        if orders_to_pickup:
            return {
                "address": g.user.address.to_dict(),
                "orders_to_pickup": orders_to_pickup
            }
    return {"flashes": ["This pickup date does not exist at the moment."]}, 404

@bp.post("/schedule/pickups/submit")
@login_required
def schedule_pickups_submit():
    format = "%Y-%m-%d"
    flashes = []
    data = request.json
    if data:
        logistics_data = {
            "logistics" : {
                "notes": data["notes"],
                "referral": "N/A",
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
        orders = [Orders.get({"id": order["id"]}) for order in data["orders"]]
        pickup_date = datetime.strptime(data["pickupDate"], format).date()
        if date.today() < pickup_date:
            pickup_logistics = create_logistics(logistics_data, orders, pickup=pickup_date)

            #TODO: async send availability details to user
            email_data = get_pickup_email(pickup_logistics)
            send_async_email.apply_async(kwargs=email_data)
            #TODO: send return procedure email

            flashes.append("You have successfully scheduled your rental pickup!")
            return {"flashes": flashes}, 200
        else:
            flashes.append("You can't schedule a pickup because the rental has already ended. Email us at hubbubcu@gmail.com to manually schedule one.")
            return {"flashes": flashes}, 406
    else:
        flashes.append("Please, provide availabilities for pickup.")
        return {"flashes": flashes}, 406
