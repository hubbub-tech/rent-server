import pytz
from datetime import datetime, date, timedelta
from flask import Blueprint, flash, g, redirect, request, session, Markup
from flask_cors import CORS

from blubber_orm import Users, Orders, Reservations, Extensions
from blubber_orm import Items, Tags

from server.tools.settings import get_orders_for_dropoff, get_orders_for_pickup
from server.tools.settings import get_delivery_schedule, process_early_return
from server.tools.settings import lock_checkout, check_if_routed, exp_decay
from server.tools.settings import login_required, AWS, json_sort
from server.tools.settings import Config

from server.tools.build import create_order, create_logistics, create_reservation, create_extension
from server.tools.build import get_extension_email, get_early_return_email, get_cancellation_email
from server.tools.build import get_renter_receipt_email, get_lister_receipt_email
from server.tools.build import get_dropoff_email, get_pickup_email
from server.tools.build import send_async_email, set_async_timeout

from server.tools import blubber_instances_to_dict, json_date_to_python_date

bp = Blueprint('process', __name__)
CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)

@bp.get("/checkout/submit")
@login_required
def checkout_submit():
    flashes = []
    cart_response = lock_checkout(g.user)

    if cart_response["is_valid"]:
        timeout_clock = datetime.now(tz=pytz.UTC) + timedelta(minutes=30)

        set_async_timeout.apply_async(eta=timeout_clock, kwargs={"user_id": g.user_id})

        transactions = []
        cart_contents = g.user.cart.contents.copy()
        for item in cart_contents:
            reservation = Reservations.unique({
                "renter_id": g.user_id,
                "item_id": item.id,
                "is_in_cart": True
            })
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
                "renter": g.user,
                "reservation": reservation
            }

            email_data = get_lister_receipt_email(transaction)
            send_async_email.apply_async(kwargs=email_data)
            transactions.append(transaction)
            g.user.cart.remove(reservation)
            item.unlock()

        email_data = get_renter_receipt_email(transactions)
        send_async_email.apply_async(kwargs=email_data)

        flashes.append("Successfully rented all items! Now, just let us know when we can drop them off.")
        return {"flashes": flashes}, 200
    else:
        flashes.append(cart_response["message"])
        return {"flashes": flashes}, 406

@bp.get("/accounts/u/orders")
@login_required
def order_history():
    photo_url = AWS.get_url(dir="items")
    order_history = Orders.filter({"renter_id": g.user_id})
    orders = []
    if order_history:
        for order in order_history:

            item = Items.get({"id": order.item_id})
            item_to_dict = item.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            item_to_dict["details"] = item.details.to_dict()

            order_to_dict = order.to_dict()
            order_to_dict["is_extended"] = order.ext_date_end != order.res_date_end
            order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
            order_to_dict["reservation"] = order.reservation.to_dict()

            lister = Users.get({"id": order.lister_id})
            order_to_dict["lister"] = lister.to_dict()
            order_to_dict["item"] = item_to_dict

            orders.append(order_to_dict)
        json_sort(orders, "date_placed", reverse=True)
    return {
        "photo_url": photo_url,
        "orders": orders
    }

@bp.get("/accounts/o/id=<int:order_id>")
@login_required
def manage_order(order_id):
    photo_url = AWS.get_url(dir="items")
    flashes = []
    order = Orders.get({"id": order_id})
    if order:
        item = Items.get({"id": order.item_id})
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

            lister = Users.get({"id": order.lister_id})
            order_to_dict["lister"] = lister.to_dict()
            order_to_dict["item"] = item_to_dict
            return {
                "order": order_to_dict,
                "photo_url": photo_url
            }
        else:
            flashes.append("You can only manage orders that you placed.")
            return {"flashes": flashes}, 406
    else:
        return {"flashes": ["This order does not exist at the moment."]}, 404

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

@bp.post("/accounts/o/cancel/submit")
@login_required
def cancel_order():
    code = 406
    flashes = []
    data = request.json
    if data:
        order_id = data["orderId"]
        order = Orders.get({"id": order_id})
        if g.user_id == order.renter_id:
            if not order.is_dropoff_sched:
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
                code = 200

                send_async_email.apply_async(kwargs=email_data)
            else:
                flashes.append("We could not cancel your order, as it has been/is being delivered. Consider an early return instead.")
        else:
            flashes.append("This isn't your order, so you can't cancel it...")
    else:
        flashes.append("Nothing was sent... try again.")
    return {"flashes": flashes}, code
