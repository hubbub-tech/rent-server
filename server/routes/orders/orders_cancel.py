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
