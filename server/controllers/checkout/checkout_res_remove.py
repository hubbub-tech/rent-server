from flask import Blueprint


bp = Blueprint("checkout", __name__)


@bp.post("/remove/i/id=<int:item_id>")
@login_required
def remove_from_cart(item_id):
    flashes = []
    format = "%Y-%m-%d" # this format when taking dates thru url
    item = Items.get({"id": item_id})
    if item:
        data = request.json
        if data.get("startDate") and data.get("endDate"):
            reservation_keys = {
                "renter_id": g.user_id,
                "item_id": item_id,
                "date_started": datetime.strptime(data.get("startDate"), format).date(),
                "date_ended": datetime.strptime(data.get("endDate"), format).date(),
            }
            reservation = Reservations.get(reservation_keys)

            assert reservation is not None, "Reservation does not exist."

            g.user.cart.remove(reservation)
        else:
            g.user.cart.remove_without_reservation(item)
        flashes.append(f"The {item.name} has been removed from your cart.")
        data = {"flashes": flashes}
        response = make_response(data, 200)
        return response
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404
