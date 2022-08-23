import pytz
from datetime import datetime, date, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

from blubber_orm import Reservations, Items, Orders, Users, Extensions


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
