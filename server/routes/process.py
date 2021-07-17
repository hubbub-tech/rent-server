import pytz
from datetime import datetime, date, timedelta
from flask import Blueprint, flash, g, redirect, request, session, Markup

from blubber_orm import Users, Orders, Reservations, Extensions
from blubber_orm import Items, Tags

from server.tools.settings import get_orders_for_dropoff, get_orders_for_pickup
from server.tools.settings import get_delivery_schedule, process_early_return
from server.tools.settings import lock_checkout, check_if_routed, exp_decay
from server.tools.settings import login_required, AWS, json_sort

from server.tools.build import create_order, create_logistics, create_reservation, create_extension
from server.tools.build import get_extension_email, get_early_return_email, get_cancellation_email
from server.tools.build import get_renter_receipt_email, get_lister_receipt_email
from server.tools.build import get_dropoff_email, get_pickup_email
from server.tools.build import send_async_email, set_async_timeout

from server.tools import blubber_instances_to_dict, json_date_to_python_date

bp = Blueprint('process', __name__)

@bp.post("/checkout/submit")
@login_required
def checkout_submit():
    flashes = []
    user = Users.get(g.user_id)
    cart_response = lock_checkout(user)
    if cart_response["is_valid"]:
        timeout_clock = datetime.now(tz=pytz.UTC) + timedelta(minutes=30)
        set_async_timeout.apply_async(eta=timeout_clock, kwargs={"user_id": user.id})

        transactions = []
        _cart_contents = user.cart.contents # need this because cart size changes
        for item in _cart_contents:
            _reservation = Reservations.filter({
                "renter_id": g.user_id,
                "item_id": item.id,
                "is_in_cart": True
            })
            reservation, = _reservation
            item.calendar.add(reservation)
            order_data = {
                "res_date_start": reservation.date_started,
                "res_date_end": reservation.date_ended,
                "renter_id": reservation.renter_id,
                "item_id": reservation.item_id,
                "is_online_pay": False,
                "lister_id": item.lister_id,
                "date_placed": date.today(),
            }
            order = create_order(order_data)
            transaction = {
                "item": item,
                "order": order,
                "renter": user,
                "reservation": reservation
            }
            #TODO: send email receipt to lister
            email_data = get_lister_receipt_email(transaction)
            send_async_email.apply_async(kwargs=email_data)
            transactions.append(transaction) # important for renters receipt
            user.cart.remove(reservation)
            item.unlock()
        #TODO: send email receipt to renter
        email_data = get_renter_receipt_email(transactions)
        send_async_email.apply_async(kwargs=email_data)
        session["cart_size"] = 0
        flashes.append("Successfully rented all items! Now, just let us know when we can drop them off.")
        return {"flashes": flashes}, 201
    else:
        flashes.append(cart_response["message"])
        return {"flashes": flashes}, 406

@bp.post("/accounts/u/orders")
@login_required
def order_history():
    photo_url = AWS.get_url("items")
    user = Users.get(g.user_id)
    order_history = Orders.filter({"renter_id": g.user_id})
    orders = []
    if order_history:
        for order in order_history:
            item = Items.get(order.item_id)
            item_to_dict = item.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            item_to_dict["details"] = item.details.to_dict()

            order_to_dict = order.to_dict()
            order_to_dict["is_extended"] = order.ext_date_end != order.res_date_end
            order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
            order_to_dict["reservation"] = order.reservation.to_dict()
            order_to_dict["lister"] = order.lister.to_dict()
            order_to_dict["item"] = item_to_dict

            orders.append(order_to_dict)
    json_sort(orders, "date_placed", reverse=True)
    return {
        "photo_url": photo_url,
        "orders": orders
    }

@bp.post("/accounts/o/id=<int:order_id>")
@login_required
def manage_order(order_id):
    photo_url = AWS.get_url("items")
    flashes = []
    user = Users.get(g.user_id)
    order = Orders.get(order_id)
    item = Items.get(order.item_id)
    is_extended = order.ext_date_end != order.res_date_end
    if g.user_id == order.renter_id:
        item_to_dict = item.to_dict()
        item_to_dict["calendar"] = item.calendar.to_dict()
        item_to_dict["details"] = item.details.to_dict()

        order_to_dict = order.to_dict()
        order_to_dict["is_extended"] = is_extended
        order_to_dict["ext_date_start"] = order.ext_date_start.strftime("%Y-%m-%d")
        order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
        order_to_dict["reservation"] = order.reservation.to_dict()
        order_to_dict["lister"] = order.lister.to_dict()
        order_to_dict["item"] = item_to_dict
        return {
            "order": order_to_dict,
            "photo_url": photo_url
        }
    else:
        flashes.append("You can only manage orders that you placed.")
        return {"flashes": flashes}, 406

@bp.post("/schedule/dropoffs/<date_str>")
@login_required
def schedule_dropoffs(date_str):
    format = "%Y-%m-%d"
    user = Users.get(g.user_id)
    res_date_start = datetime.strptime(date_str, format).date()
    orders = Orders.filter({
        "renter_id": g.user_id,
        "is_dropoff_sched": False,
        "res_date_start": res_date_start
    })
    orders_to_dropoff = []
    for order in orders:
        order_to_dict = order.to_dict()
        item = Items.get(order.item_id)
        order_to_dict["item"] = item.to_dict()
        order_to_dict["reservation"] = order.reservation.to_dict()
        orders_to_dropoff.append(order_to_dict)
    return {
        "address": user.address.to_dict(),
        "orders_to_dropoff": orders_to_dropoff
    }

@bp.post("/schedule/dropoffs/submit")
@login_required
def schedule_dropoffs_submit():
    format = "%Y-%m-%d"
    user = Users.get(g.user_id)
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
                "address_num": data["address"]["num"],
                "address_street": data["address"]["street"],
                "address_apt": data["address"]["apt"],
                "address_zip": data["address"]["zip_code"]
            },
            "address": {
                "num": data["address"]["num"],
                "street": data["address"]["street"],
                "apt": data["address"]["apt"],
                "city": data["address"]["city"],
                "state": data["address"]["state"],
                "zip": data["address"]["zip_code"]
            }
        }
        orders = [Orders.get(order["id"]) for order in data["orders"]]
        dropoff_date = datetime.strptime(data["dropoffDate"], format).date()
        if date.today() < dropoff_date:
            dropoff_logistics = create_logistics(logistics_data, orders, dropoff=dropoff_date)

            #TODO: async send availability details to user
            email_data = get_dropoff_email(dropoff_logistics)
            send_async_email.apply_async(kwargs=email_data)
            #TODO: send return procedure email

            flashes.append("You have successfully scheduled your rental dropoffs!")
            return {"flashes": flashes}, 201
        else:
            flashes.append("You can't schedule a dropoff because the rental has already started. Email us at hubbubcu@gmail.com to manually schedule one.")
            return {"flashes": flashes}, 406
    else:
        flashes.append("Please, provide availabilities for dropoff.")
        return {"flashes": flashes}, 406

@bp.post("/schedule/pickups/<date_str>")
@login_required
def schedule_pickups(date_str):
    format = "%Y-%m-%d"
    user = Users.get(g.user_id)
    res_date_end = datetime.strptime(date_str, format).date()
    orders = Orders.filter({"renter_id": g.user_id, "is_pickup_sched": False})
    orders_to_pickup = []
    for order in orders:
        if order.ext_date_end == res_date_end:
            order_to_dict = order.to_dict()
            item = Items.get(order.item_id)
            order_to_dict["item"] = item.to_dict()
            order_to_dict["reservation"] = order.reservation.to_dict()
            orders_to_pickup.append(order_to_dict)
    return {
        "address": user.address.to_dict(),
        "orders_to_pickup": orders_to_pickup
    }

@bp.post("/schedule/pickups/submit")
@login_required
def schedule_pickups_submit():
    format = "%Y-%m-%d"
    user = Users.get(g.user_id)
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
                "address_num": data["address"]["num"],
                "address_street": data["address"]["street"],
                "address_apt": data["address"]["apt"],
                "address_zip": data["address"]["zip_code"]
            },
            "address": {
                "num": data["address"]["num"],
                "street": data["address"]["street"],
                "apt": data["address"]["apt"],
                "city": data["address"]["city"],
                "state": data["address"]["state"],
                "zip": data["address"]["zip_code"]
            }
        }
        print(type(data["timesChecked"]))
        orders = [Orders.get(order["id"]) for order in data["orders"]]
        pickup_date = datetime.strptime(data["pickupDate"], format).date()
        if date.today() < pickup_date:
            pickup_logistics = create_logistics(logistics_data, orders, pickup=pickup_date)

            #TODO: async send availability details to user
            email_data = get_pickup_email(pickup_logistics)
            send_async_email.apply_async(kwargs=email_data)
            #TODO: send return procedure email

            flashes.append("You have successfully scheduled your rental pickup!")
            return {"flashes": flashes}, 201
        else:
            flashes.append("You can't schedule a pickup because the rental has already ended. Email us at hubbubcu@gmail.com to manually schedule one.")
            return {"flashes": flashes}, 406
    else:
        flashes.append("Please, provide availabilities for pickup.")
        return {"flashes": flashes}, 406

@bp.post("/accounts/o/early/submit")
@login_required
def early_return_submit():
    code = 406
    flashes = []
    user = Users.get(g.user_id)
    data = request.json
    if data:
        order_id = data["orderId"]
        order = Orders.get(order_id)
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
            code = 201

            email_data = get_early_return_email(order, early_reservation)
            send_async_email.apply_async(kwargs=email_data)
        flashes.append(response["message"])
    else:
        flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, code

@bp.post("/accounts/o/extend/submit")
@login_required
def extend_submit():
    code = 406
    flashes = []
    user = Users.get(g.user_id)
    data = request.json
    if data:
        item_id = data["itemId"]
        item = Items.get(item_id)
        if item.is_locked == False:
            item.lock(user)
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
                code = 201
                extension = create_extension(ext_data)
                flashes.append(f"Your {item.name} was successfully extended!")
            else:
                flashes.append(f"Sorry, you cannot extend this rental. It seems someone just got to the {item.name} before you.")
            item.unlock()
            if code == 201:
                email_data = get_extension_email(order, ext_reservation)
                send_async_email.apply_async(kwargs=email_data)
        else:
            flashes.append("It looks like someone else is ordering the item right now.")
    else:
        flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, code

@bp.post("/accounts/o/cancel/submit")
@login_required
def cancel_order():
    code = 406
    flashes = []
    user = Users.get(g.user_id)
    data = request.json
    if data:
        order_id = data["orderId"]
        order = Orders.get(order_id)
        if g.user_id == order.renter_id:
            if not order.is_dropoff_scheduled:
                reservation_to_delete = order.reservation
                res_keys = {
                    "date_started": reservation_to_delete.date_started,
                    "date_ended": reservation_to_delete.date_ended,
                    "renter_id": reservation_to_delete.renter_id,
                    "item_id": reservation_to_delete.item_id
                }
                #Need to generate email before deletion
                email_data = get_cancellation_email(order)

                Reservations.delete(res_keys)
                flashes.append("Your order was successfully cancelled. Hopefully we'll see you again!")
                code = 201

                send_async_email.apply_async(kwargs=email_data)
            else:
                flashes.append("We could not cancel your order, as it has been/is being delivered. Consider an early return instead.")
        else:
            flashes.append("This isn't your order, so you can't cancel it...")
    else:
        flashes.append("Nothing was sent... try again.")
    return {"flashes": flashes}, code
