import stripe
from datetime import datetime

from src.models import Users
from src.models import Carts
from src.models import Items
from src.models import Calendars

from src.models import Orders
from src.models import Extensions
from src.models import Reservations

from src.utils.classes import Status
from src.utils.settings import SERVER_DOMAIN, CLIENT_DOMAIN, STRIPE_APIKEY


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

        if res is None:
            unlock_cart(cart, specified_items=locked_items)

            status = Status()
            status.is_successful = False
            status.message = f"Your {item.name} was not ready for checkout."
            return status

        item_calendar = Calendars.get({"id": item.id})
        if item_calendar.check_reservation(res.dt_started, res.dt_ended) and item.is_locked == False:
            user = Users.get({"id": cart.id})

            item.lock(user)
            locked_items.append(item)
        else:
            unlock_cart(cart, specified_items=locked_items)

            status = Status()
            status.is_successful = False
            status.message = f"Seems like someone got to the {item.name} before you. Check your rental period."
            return status

    status = Status()
    status.is_successful = True
    status.message = "All items in cart have been locked successfully."
    return status


def check_lock_access(accessor_id, item_ids):
    for item_id in item_ids:
        item = Items.get({ "id": item_id })
        if item.locker_id != accessor_id:
            return False

    return True


def _get_line_items(cart_id, item_ids):

    line_items = []
    for item_id in item_ids:
        item = Items.get({ "id": item_id })
        reservation = Reservations.unique({
            "item_id": item_id,
            "renter_id": cart_id,
            "is_in_cart": True
        })

        unit_amount = int(round(reservation.total(), 2) * 100)
        line_item = {
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.name,
                    "description": item.description
                },
                "unit_amount": unit_amount,
                "tax_behavior": "inclusive"
            },
            "quantity": 1,
        }

        line_items.append(line_item)

    return line_items

def get_stripe_checkout_session(cart, email):
    stripe.api_key = STRIPE_APIKEY

    item_ids = cart.get_item_ids(reserved_only=True)
    line_items = _get_line_items(cart.id, item_ids)

    client_reference_id = f"orders_checkout_session_key:{cart.checkout_session_key}"

    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=client_reference_id,
            customer_email=email,
            line_items=line_items,
            mode='payment',
            success_url=CLIENT_DOMAIN + '/checkout/success',
            cancel_url=CLIENT_DOMAIN + '/checkout/cancel',
            automatic_tax={'enabled': True},
        )
    except Exception as e:
        return print(e)
    else:
        return checkout_session


def get_stripe_extension_session(order, reservation, email):
    stripe.api_key = STRIPE_APIKEY

    item = Items.get({ "id": reservation.item_id })
    unit_amount = int(round(reservation.total(), 2) * 100)
    line_item = {
        "price_data": {
            "currency": "usd",
            "product_data": {
                "name": item.name,
                "description": item.description
            },
            "unit_amount": unit_amount,
            "tax_behavior": "inclusive"
        },
        "quantity": 1,
    }

    line_items = [line_item]
    client_reference_id = f"orders_id:{order.id}"

    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=client_reference_id,
            customer_email=email,
            line_items=line_items,
            mode='payment',
            success_url=CLIENT_DOMAIN + '/extend/success',
            cancel_url=CLIENT_DOMAIN + '/extend/cancel',
            automatic_tax={'enabled': True},
        )
    except Exception as e:
        return print(e)
    else:
        return checkout_session



def return_order_early(order, early_reservation):

    status = _validate_early_return(order, early_reservation)
    if status.is_successful == False: return status

    assert order.ext_dt_end >= order.res_dt_end, "This order has already been extended."

    item = Items.get({"id": order.item_id})
    renter = Users.get({"id": order.renter_id})
    status = _safe_early_return(order, item, renter, early_reservation)
    return status



def return_extension_early(extension, early_reservation):

    status = _validate_early_return(extension, early_reservation)
    if status.is_successful == False: return status

    item = Items.get({"id": extension.item_id})
    renter = Users.get({"id": extension.renter_id})
    status = _safe_early_return(extension, item, renter, early_reservation)
    return status


def _validate_early_return(txn, early_reservation):
    if early_reservation.dt_ended > txn.res_dt_end:
        status = Status()
        status.is_successful = False
        status.message = "Early returns must be earlier than the current return date."
        return status

    if early_reservation.item_id != txn.item_id:
        status = Status()
        status.is_successful = False
        status.message = "The reservation is not tied to the same item as the original order."
        return status

    if early_reservation.renter_id != txn.renter_id:
        status = Status()
        status.is_successful = False
        status.message = "The reservation is not tied to the same renter."
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
        curr_reservation.archive(notes="Early Return.")
        archive_reservation = curr_reservation

        if isinstance(txn, Extensions):
            Extensions.set({"order_id": txn.order_id, "res_dt_start": txn.res_dt_start}, {
                "item_id": early_reservation.item_id,
                "renter_id": early_reservation.renter_id,
                "res_dt_end": early_reservation.dt_ended,
            })

            is_extension = True
        elif isinstance(txn, Orders):
            Orders.set({"id": txn.id}, {
                "item_id": early_reservation.item_id,
                "renter_id": early_reservation.renter_id,
                "res_dt_start": early_reservation.dt_started,
                "res_dt_end": early_reservation.dt_ended,
            })

            is_extension = False
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
            "is_extension": is_extension,
            "est_charge": archive_reservation.est_charge,
            "est_deposit": archive_reservation.est_deposit,
            "est_tax": archive_reservation.est_tax
        })

        item.unlock()

        status = Status()
        status.is_successful = True
        status.message = "The early return process succeeded!"
        return status

    else:
        status = Status()
        status.is_successful = False
        status.message = "Someone else is processing the item right now. Try again in a few minutes."
        return status
