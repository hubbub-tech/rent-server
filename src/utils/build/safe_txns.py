from datetime import datetime

from src.models import Users
from src.models import Carts
from src.models import Items
from src.models import Calendars
from src.models import Reservations


def unlock_cart(cart: Carts, specified_items=None):
    if specified_items:
        for item in specified_items:
            item.unlock()
    else:
        item_ids = cart.get_item_ids()
        for item_id in item_ids:
            item = Items.get({"id": item_id})
            item.unlock()


def lock_cart(cart: Carts):
    """check that reservations don't overlap and that item is unlocked."""

    locked_items = []

    item_ids = cart.get_item_ids()

    for item_id in item_ids:
        item = Items.get({"id": item_id})

        res = Reservations.unique({
            "item_id": item.id,
            "renter_id": cart.id,
            "is_in_cart": True
        })

        if reservation is None:
            unlock_cart(cart, specified_items=locked_items)

            status = Status()
            status.is_successful = False
            status.messages.append("Seems like someone got to an item before you. Check your rental periods.")
            return status

        item_calendar = Calendars.get({"id": item.id})
        if item_calendar.check_reservation(res) and item.is_locked == False:
            user = Users.get({"id": cart.id})

            item.lock(user)
            locked_items.append(item)
        else:
            unlock_cart(user, specified_items=locked_items)

            status = Status()
            status.is_successful = False
            status.messages.append("Seems like someone got to an item before you. Check your rental periods.")
            return status

    status = Status()
    status.is_successful = True
    status.messages.append("All items in cart have been locked successfully.")
    return status


def _validate_early_return(txn, early_reservation):
    if early_reservation.dt_ended < txn.res_date_end:
        status = Status()
        status.is_successful = False
        status.messages.append("Early returns must be earlier than the current return date.")
        return status

    if early_reservation.item_id != txn.item_id:
        status = Status()
        status.is_successful = False
        status.messages.append("The reservation is not tied to the same item as the original order.")
        return status

    if early_reservation.renter_id != txn.renter_id:
        status = Status()
        status.is_successful = False
        status.messages.append("The reservation is not tied to the same renter.")
        return status

    status = Status()
    status.is_successful = True
    return status


def _safe_early_return(txn, item, user, early_reservation):
    if item.is_locked == False:
        item.lock(user)

        curr_reservation_pkeys = txn.to_query_reservation()
        Reservations.set(curr_reservation_pkeys, {"is_calendared": False})

        curr_reservation = Reservations.get(curr_reservation_pkeys)
        curr_reservation.archive()
        archive_reservation = curr_reservation

        if isinstance(txn, Extensions):
            Extensions.set({"order_id": txn.order_id, "res_dt_start": txn.res_dt_start}, {
                "item_id": early_reservation.item_id,
                "renter_id": early_reservation.renter_id,
                "res_dt_end": early_reservation.dt_ended,
            })

            is_extended = True
        elif isinstance(txn, Orders):
            Orders.set({"id": txn.id}, {
                "item_id": early_reservation.item_id,
                "renter_id": early_reservation.renter_id,
                "res_dt_start": early_reservation.res_dt_start,
                "res_dt_end": early_reservation.dt_ended,
            })

            is_extended = True
        else:
            item.unlock()
            raise Exception("Transaction does not match valid object types.")

        Reservations.set({
            "item_id": early_reservation.item_id,
            "renter_id": early_reservation.renter_id,
            "dt_started": early_reservation.dt_started,
            "dt_ended": early_reservation.dt_ended,
        }, {
            "is_calendared": True,
            "is_extended": is_extended,
            "est_charge": archive_reservation.est_charge,
            "est_deposit": archive_reservation.est_deposit,
            "est_tax": archive_reservation.est_tax
        })

        item.unlock()

        status = Status()
        status.is_successful = True
        status.messages.append("The early return process succeeded!")
        return status

    else:
        status = Status()
        status.is_successful = False
        status.messages.append("Someone else is processing the item right now. Try again in a few minutes.")
        return status


def return_order_early(order, early_reservation):

    status = _validate_early_return(order, early_reservation)
    if status.is_successful == False: return status

    assert order.ext_date_end >= order.res_date_end, "This order has already been extended."

    item = Items.get(order.item_id)
    renter = Users.get(order.renter_id)
    status = _safe_early_return(order, item, renter, early_reservation)
    return status


def return_extension_early(extension, early_return_reservation):

    status = _validate_early_return(extension, early_return_reservation)
    if status.is_successful == False: return status

    item = Items.get(order.item_id)
    renter = Users.get(order.renter_id)
    status = _safe_early_return(order, item, renter, early_reservation)
    return status
