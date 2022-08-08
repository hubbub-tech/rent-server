from flask import Blueprint


bp = Blueprint("checkout", __name__)


@bp.post("/update/i/id=<int:item_id>")
@login_required
def update(item_id):
    flashes = []
    errors = []
    code = 406
    reservation = None
    item = Items.get({"id": item_id})
    if item:
        data = request.json
        if data.get("startDate") and data.get("endDate"):
            reservation = Reservations.unique({
                "item_id": item_id,
                "renter_id": g.user_id,
                "is_in_cart": True
            })
            if reservation: g.user.cart.remove(reservation)
            else: g.user.cart.remove_without_reservation(item)

            new_date_started = json_date_to_python_date(data["startDate"])
            new_date_ended = json_date_to_python_date(data["endDate"])
            rental_range = {
                "date_started": new_date_started,
                "date_ended": new_date_ended
            }
            form_check = validate_rental_bounds(item, rental_range)
            if form_check["is_valid"]:
                rental_data = {
                    "renter_id": g.user_id,
                    "item_id": item.id,
                    "date_started": new_date_started,
                    "date_ended": new_date_ended
                }
                reservation, action, waitlist_ad = create_reservation(rental_data)
                if reservation:
                    g.user.cart.add(reservation)
                    reservation = reservation.to_dict()
                    action = "Your reservation has been updated successfully!"
                    code = 200
                else:
                    g.user.cart.add_without_reservation(item)
                    flashes.append(waitlist_ad)
                flashes.append(action)
            else:
                g.user.cart.add_without_reservation(item)
                flashes.append(form_check["message"])
        else:
            flashes.append("There was an error getting the dates you set, make sure they're in 'MM/DD/YYYY'.")
        return {"flashes": flashes}, code
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404
