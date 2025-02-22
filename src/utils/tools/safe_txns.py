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

from .factories import create_reservation


def unlock_cart(cart: Carts, specified_items=None):
    assert cart.table_name == 'carts', "must be of type Carts."
    
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
    assert cart.table_name == 'carts', "must be of type Carts."

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
        if item_calendar.check_reservation(res.dt_started, res.dt_ended) and (item.is_locked == False or item.locker_id == cart.id):
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


def check_lock_access(accessor_id: int, item_ids: list):
    assert isinstance(accessor_id, int), "Accessor_id must be an int."
    assert isinstance(item_ids, list), "Must receive a list of item ids."

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



def return_order_early(order, early_res_dt_end):

    status = _validate_early_return(order, early_res_dt_end)
    if status.is_successful == False: return status

    status = _safe_early_return(order, early_res_dt_end)
    return status


def _validate_early_return(order, early_res_dt_end):
    if early_res_dt_end > order.ext_dt_end:
        status = Status()
        status.is_successful = False
        status.message = "Early returns must be earlier than the current return date."
        return status

    status = Status()
    status.is_successful = True
    return status


def _safe_early_return(order, early_res_dt_end):
    item = Items.get({ "id": order.item_id })
    user = Users.get({ "id": order.renter_id })

    if item.is_locked == False:
        item.lock(user)

        extensions = order.get_extensions()
        if extensions:
            res_dt_start_index = -2
            res_dt_end_index = -1
            extensions.sort(key = lambda ext: ext[res_dt_start_index], reverse=True)

            i = 0
            est_refund = 0
            while early_res_dt_end <= extensions[i][res_dt_start_index]:
                reservation_data = {
                    "item_id": order.item_id,
                    "renter_id": order.renter_id,
                    "dt_started": extensions[i][res_dt_start_index],
                    "dt_ended": extensions[i][res_dt_end_index]
                }

                reservation = Reservations.get(reservation_data)
                est_refund += reservation.est_charge

                Reservations.set(reservation_data, { "is_calendared": False })

                Extensions.delete({
                    "order_id": order.id,
                    "res_dt_start": extensions[i][res_dt_start_index]
                })
                i += 1

                if i >= len(extensions): break

            extensions = order.get_extensions()
            extensions.sort(key = lambda ext: ext[res_dt_start_index])
            if extensions:
                reservation = Reservations.get({
                    "item_id": item.id,
                    "renter_id": user.id,
                    "dt_started": extensions[-1][res_dt_start_index],
                    "dt_ended": extensions[-1][res_dt_end_index]
                })

                reservation_data = reservation.to_dict(serializable=False)

                Reservations.set(reservation_data, { "is_calendared": False })
                reservation.archive(notes="Early Return.")

                early_reservation_data = reservation_data
                early_reservation_data["dt_ended"] = early_res_dt_end
                early_reservation = create_reservation(early_reservation_data)

                Reservations.set(early_reservation_data, { "is_calendared": True })
                Extensions.set({"order_id": order.id, "res_dt_start": early_reservation.dt_started }, {
                    "res_dt_end": early_res_dt_end
                })

        extensions = order.get_extensions()
        if extensions == []:
            reservation = Reservations.get({
                "item_id": order.item_id,
                "renter_id": order.renter_id,
                "dt_started": order.res_dt_start,
                "dt_ended": order.res_dt_end
            })

            reservation_data = reservation.to_dict(serializable=False)

            Reservations.set(reservation_data, { "is_calendared": False })
            reservation.archive(notes="Early Return.")

            early_reservation_data = reservation_data
            early_reservation_data["dt_ended"] = early_res_dt_end
            early_reservation = create_reservation(early_reservation_data)

            Reservations.set(early_reservation_data, { "is_calendared": True })

            Orders.set({ "id": order.id }, {
                "res_dt_start": early_reservation.dt_started,
                "res_dt_end": early_reservation.dt_ended
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
