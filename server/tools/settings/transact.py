import pytz
from math import log, exp
from datetime import datetime, date, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

from blubber_orm import Reservations, Items, Orders, Users, Extensions

def exp_decay(retail_price, time_now, discount=.50, time_total=28):
    #Where discount is issued at time_total
    base_price = retail_price / 10
    if time_now > 180:
        time_total = 56
    compound = retail_price / 90
    a = compound * 10 ** (-log((1 - discount), 10) / (time_total - 1))
    r = 1 - (compound / a)
    y = a * (1 - r) ** time_now #per_day_price_now
    #calculate the cost of the rental to the user
    integ_time = y / log(1 - r)
    integ_0 = a * (1 - r) / log(1 - r)
    cost_to_date = base_price + integ_time - integ_0
    if cost_to_date < base_price:
        return base_price
    return cost_to_date

def create_rental_token(shopper_id, cost):
    unhashed_token = f"hubbubble-{shopper_id}-{cost}"
    hashed_token = generate_password_hash(unhashed_token)
    return hashed_token

def verify_rental_token(hashed_token, shopper_id, cost):
    unhashed_token = f"hubbubble-{shopper_id}-{cost}"
    is_valid = check_password_hash(hashed_token, unhashed_token)
    return is_valid

def unlock_checkout(user, specified_items=None):
    if specified_items:
        for item in specified_items:
            item.unlock()
    else:
        for item in user.cart.contents:
            item.unlock()

def lock_checkout(user):
    locked_items = []
    #check that reservations don't overlap and that item is unlocked
    for item in user.cart.contents:
        _reservation = Reservations.filter({
            "item_id": item.id,
            "renter_id": user.id,
            "is_in_cart": True
        })
        if _reservation:
            reservation, = _reservation
            if item.calendar.scheduler(reservation) and item.is_locked == False:
                item.lock(user)
                locked_items.append(item)
            else:
                unlock_checkout(user, specified_items=locked_items)
                return {
                    "is_valid" : False,
                    "message" : "Seems like someone got to an item before you. Check your rental periods."
                    }
        else:
            unlock_checkout(user, specified_items=locked_items)
            return {
                "is_valid" : False,
                "message" : "Not all of your items had reservations set for checkout."
                }
    return {
        "is_valid" : True,
        "message" : "All items in cart have been locked successfully."
        }

def check_if_routed(user):
    routed_items = []
    for item in user.cart.contents:
        if item.is_locked and item.last_locked == user.id:
            if item.is_routed:
                routed_items.append(item)
            else:
                unlock_checkout(user, specified_items=routed_items)
                return {
                    "is_valid" : False,
                    "message" : "You are not authorized to complete this transaction. Could not route your cart, try again."
                    }
        else:
            unlock_checkout(user, specified_items=routed_items)
            return {
                "is_valid" : False,
                "message" : "Sorry, we could not lock your transaction. Please try again."
                }
    return {
        "is_valid" : True,
        "message" : "All items in cart have been routed correctly."
        }

def get_orders_for_dropoff(renter_id):
    orders = Orders.filter({"is_dropoff_sched": False, "renter_id": renter_id})
    if orders:
        group_orders = {}
        group_by_date = []
        orders.sort(key=lambda order: order.res_date_start)
        comparitor_date_str = orders[0].res_date_start.strftime("%Y-%m-%d")
        for order in orders:
            date_str = order.res_date_start.strftime("%Y-%m-%d")
            if date_str == comparitor_date_str:
                group_by_date.append(order)
                group_orders[comparitor_date_str] = group_by_date
            else:
                group_by_date = []
                group_by_date.append(order)
                group_orders[date_str] = group_by_date
                comparitor_date_str = date_str
    else:
        group_orders = None
    return group_orders

def get_orders_for_pickup(renter_id):
    orders = Orders.filter({"is_dropoff_sched": True, "is_pickup_sched": False, "renter_id": renter_id})
    if orders:
        group_orders = {}
        group_by_date = []
        orders.sort(key=lambda order: order.ext_date_end)
        comparitor_date_str = orders[0].ext_date_end.strftime("%Y-%m-%d")
        for order in orders:
            date_str = order.ext_date_end.strftime("%Y-%m-%d")
            if date_str == comparitor_date_str:
                group_by_date.append(order)
                group_orders[comparitor_date_str] = group_by_date
            else:
                group_by_date = []
                group_by_date.append(order)
                group_orders[date_str] = group_by_date
                comparitor_date_str = date_str
    else:
        group_orders = None
    return group_orders

def get_delivery_schedule(availabilities):
    """Takes a list of availabilities formatted as `TIME@DATE`"""
    availabilities.sort(key = lambda entry: entry[-10:-1])
    delivery_schedule = {}
    for entry in availabilities:
        delivery_time, delivery_date = entry.split("@")

        if delivery_schedule.get(delivery_date, None):
            delivery_schedule[delivery_date].append(delivery_time)
        else:
            delivery_schedule[delivery_date] = [delivery_time]
    return delivery_schedule

def process_early_return(order, early_return_reservation):
    is_success = False
    extension_keys = {}
    if early_return_reservation.date_ended < order.ext_date_end:
        if early_return_reservation.item_id == order.item_id:
            if early_return_reservation.renter_id == order.renter_id:
                renter = Users.get(order.renter_id)
                item = Items.get(order.item_id)
                if order.ext_date_end == order.res_date_end:
                    date_started = order.res_date_start
                    date_ended = order.res_date_end
                    is_extended = False
                else:
                    extension_keys = {
                        "order_id": order.id,
                        "res_date_end": order.ext_date_end
                    }
                    extension = Extensions.get(extension_keys)
                    date_started = extension.res_date_start
                    date_ended = extension.res_date_end
                    is_extended = True
                old_res_keys = {
                    "renter_id": order.renter_id,
                    "item_id": order.item_id,
                    "date_started": date_started,
                    "date_ended": date_ended
                }
                if item.is_locked == False:
                    item.lock(renter) # if someone else hasn't locked it already, lock it
                    Reservations.set(old_res_keys, {"is_calendared": False})
                    new_res_keys = {
                        "renter_id": early_return_reservation.renter_id,
                        "item_id": early_return_reservation.item_id,
                        "res_date_start": early_return_reservation.date_started,
                        "res_date_end": early_return_reservation.date_ended
                    }
                    if is_extended:
                        Extensions.delete(extension_keys)
                        insert_data = {**new_res_keys, **{"order_id": order.id}}
                        new_extension = Extensions.insert(insert_data)
                    else:
                        Orders.set(order.id, new_res_keys)
                    new_res_keys = {
                        "renter_id": early_return_reservation.renter_id,
                        "item_id": early_return_reservation.item_id,
                        "date_started": early_return_reservation.date_started,
                        "date_ended": early_return_reservation.date_ended
                    }
                    old_reservation = Reservations.get(old_res_keys)
                    Reservations.set(new_res_keys, {
                        "is_calendared": True,
                        "is_extended": is_extended,
                        "charge": old_reservation._charge,
                        "deposit": old_reservation._deposit,
                        "tax": old_reservation._tax
                    })
                    item.unlock()
                    is_success = True
                    message = "The early return process succeeded!"
                else:
                    message = "Someone else is processing the item right now. Try again in a few minutes."
            else:
                message = "The reservation is not tied to the same renter."
        else:
            message = "Error: The reservation is not tied to the same item as the original order."
    else:
        message = "Early returns must be earlier than the current return date."
    return {
        "is_success": is_success,
        "message": message
    }
