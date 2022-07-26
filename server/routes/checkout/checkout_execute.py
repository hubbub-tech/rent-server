from flask import Blueprint


bp = Blueprint("checkout", __name__)


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
