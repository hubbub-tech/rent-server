import pytz
from datetime import datetime, timedelta
from flask import Blueprint, make_response, request, g, redirect

from src.models import Carts
from src.models import Items
from src.models import Orders
from src.models import Calendars
from src.models import Reservations

from src.utils import lock_cart
from src.utils import unlock_cart
from src.utils import check_lock_access
from src.utils import verify_token
from src.utils import create_order
from src.utils import login_required

from src.utils import get_stripe_checkout_session
from src.utils import send_async_email, set_async_timeout
from src.utils import get_lister_receipt_email, get_renter_receipt_email


bp = Blueprint("execute", __name__)

# 0. send checkout_session_key to client. when this is NOT NULL on frontend, order now button shows
# *1. user clicks order now and client sends checkout_session_key back, server verifies it
# *2. server locks items then checks that reservations are valid, then tells client that they are (or are not)
# 3. client receives go ahead and maybe tells user that they have X mins to pay
# 4. client gets a transaction verification token from payment processor and sends back to server
# 5. server verifies using the token that the goods were paid for--then reserves items and unlocks
# 6. confetti

@bp.post("/checkout/validate")
@login_required
def validate_checkout():

    user_cart = Carts.get({"id": g.user_id})

    checkout_session_key = request.json["checkoutSession"]
    txn_method = request.json["txnMethod"]

    if user_cart.checkout_session_key != checkout_session_key:
        error = "Your cart is not prepared for checkout."
        response = make_response({ "message": error }, 401)
        return response

    reserved_items = user_cart.get_item_ids(reserved_only=True)
    if len(reserved_items) != len(user_cart):
        error = "Your cart is not prepared for checkout."
        response = make_response({ "message": error }, 401)
        return response

    status = lock_cart(user_cart)
    if status.is_successful == False:
        error = status.message
        response = make_response({ "message": error }, 401)
        return response

    timeout_clock = datetime.now(tz=pytz.UTC) + timedelta(minutes=30)
    set_async_timeout.apply_async(eta=timeout_clock, kwargs={"user_id": user_cart.id})

    if txn_method == "in-person":
        message = "Thank you! Now waiting on next steps to complete your order..."
        response = make_response({ "message": message }, 200)
        return response
    else:
        checkout_session = get_stripe_checkout_session(user_cart, g.user_email)
        response = make_response({ "redirect_url": checkout_session.url }, 200)
        return response


@bp.get("/checkout")
@login_required
def checkout():

    # I think there are two ways to do this:
    # 1. receive token from client and verify validity of token then transact
    # 2. receive token from payment processor directly and verify amount paid matches

    user_cart =  Carts.get({ "id": g.user_id })

    # NOTE: test that the amount paid is accurate

    item_ids = user_cart.get_item_ids(reserved_only=True)
    has_checkout_authorization = check_lock_access(g.user_id, item_ids)

    if has_checkout_authorization == False:
        error = "You don't have permission to checkout your cart."
        response = make_response({ "message": error }, 403)
        return response

    if len(item_ids) == 0:
        print(item_ids)
        error = "You don't have any items that are ready for checkout."
        response = make_response({ "message": error }, 403)
        return response

    dt_placed = datetime.now()
    ts_placed = datetime.timestamp(dt_placed)
    checkout_session_key = f"{user_cart.checkout_session_key}-{ts_placed}"

    for item_id in item_ids:
        item = Items.get({"id": item_id})
        item_calendar = Calendars.get({ "id": item.id })

        reservation = Reservations.unique({
            "renter_id": user_cart.id,
            "item_id": item_id,
            "is_in_cart": True
        })

        item_calendar.add(reservation)

        order_data = {
            "dt_placed": dt_placed,
            "res_dt_start": reservation.dt_started,
            "res_dt_end": reservation.dt_ended,
            "renter_id": reservation.renter_id,
            "item_id": reservation.item_id,
            "checkout_session_key": checkout_session_key
        }
        order = create_order(order_data)

        item.unlock()
        user_cart.remove(reservation)

        email_data = get_lister_receipt_email(order) # WARNING
        send_async_email.apply_async(kwargs=email_data.to_dict())

    orders = Orders.filter({
        "renter_id": user_cart.id,
        "checkout_session_key": checkout_session_key
    })

    email_data = get_renter_receipt_email(orders)
    send_async_email.apply_async(kwargs=email_data.to_dict())

    response = make_response({ "message": "Success!" }, 200)
    return response


@bp.get("/checkout/cancel")
@login_required
def cancel_checkout():

    user_cart = Carts.get({ "id": g.user_id })

    item_ids = user_cart.get_item_ids()

    unlock_cart(user_cart)

    response = make_response({ "message": "Your order was cancelled." }, 200)
    return response
