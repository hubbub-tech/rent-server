from flask import Blueprint


bp = Blueprint("checkout", __name__)


@bp.post("/add/i/id=<int:item_id>")
@login_required
def add_to_cart(item_id):
    item = Items.get({"id": item_id})
    if item:
        data = request.json
        if g.user.id != item.lister_id:
            if data.get("startDate") and data.get("endDate"):
                date_started = json_date_to_python_date(data["startDate"])
                date_ended = json_date_to_python_date(data["endDate"])
                if g.user.cart.contains(item):
                    message = "The item is already in your cart."
                else:
                    reservation_keys = {
                        "renter_id": g.user_id,
                        "item_id": item_id,
                        "date_started": date_started,
                        "date_ended": date_ended
                    }
                    reservation = Reservations.get(reservation_keys)

                    assert reservation is not None, "Reservation does not exist."

                    g.user.cart.add(reservation)
                    message = "The item has been added to your cart!"
            else:
                if g.user.cart.contains(item):
                    message = "The item is already in your cart."
                else:
                    g.user.cart.add_without_reservation(item)
                    message = "The item has been added to your cart!"
            return {"flashes": [message]}, 200
        else:
            return {"flashes": ["Sorry, you cannot rent an item from yourself."]}, 406
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404
