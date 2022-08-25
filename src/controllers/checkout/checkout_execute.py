from flask import Blueprint

from src.models import Carts
from src.models import Calendars
from src.models import Reservations

from src.utils import lock_cart
from src.utils import verify_token
from src.utils import create_order

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
    checkout_session_key = request.args.get("checkoutSession", "Failed")

    if checkout_session_key is None or verify_token(user_cart.checkout_session_key, checkout_session_key) == False:
        errors = ["Your cart is not prepared for checkout."]
        response = make_response({"messages": errors}, 401)
        return response

    status = lock_cart(user_cart)
    if status.is_successful == False:
        errors = ["Your cart is not prepared for checkout."]
        response = make_response({"messages": errors}, 401)
        return response


    timeout_clock = datetime.now(tz=pytz.UTC) + timedelta(minutes=30)
    set_async_timeout.apply_async(eta=timeout_clock, kwargs={"user_id": user_cart.id})

    messages = ["Thank you! Now waiting on next steps to complete your order..."]
    response = make_response({ "messages": messages }, 200)
    return response


@bp.post("/checkout")
@login_required
def checkout():

    # I think there are two ways to do this:
    # 1. receive token from client and verify validity of token then transact
    # 2. receive token from payment processor directly and verify amount paid matches

    user_cart =  Carts.get({ "id": g.user_id })

    # hand wavy~
    txn_token = request.args.get(TXN_KEY)

    # test that the amount paid is accurate
    total_paid = get_charge_from_stripe(txn_token)

    est_total_paid = user_cart.total()
    if total_paid != est_total_paid:
        errors = [
            "It seems that you paid the wrong amount.",
            f"You paid ${total_paid} instead of ${est_total_paid}."
        ]
        response = make_response({"messages": errors}, 401)
        return response


    item_ids = user_cart.get_item_ids()

    for item_id in item_ids:
        item_calendar = Calendars.get({ "id": item_id })

        reservation = Reservations.unique({
            "renter_id": user_cart.id,
            "item_id": item_id,
            "is_in_cart": True
        })

        item_calendar.add(reservation)

        order_data = {
            "res_dt_start": reservation.dt_started,
            "res_dt_end": reservation.dt_ended,
            "renter_id": reservation.renter_id,
            "item_id": reservation.item_id,
            "checkout_session_key": user_cart.checkout_session_key
        }
        order = create_order(order_data)

        item.unlock()
        user_cart.remove(reservation)

        email_data = get_lister_receipt_email(order) # WARNING
        send_async_email.apply_async(kwargs=email_data)


    email_data = get_renter_receipt_email(transactions)
    send_async_email.apply_async(kwargs=email_data)

    messages = [
        "Successfully rented all items!",
        "Now, just let us know when we can drop them off."
    ]
    response = make_response({"messages": messages}, 200)
    return response
