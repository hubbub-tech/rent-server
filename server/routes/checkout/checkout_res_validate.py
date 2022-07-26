from flask import Blueprint


bp = Blueprint("checkout", __name__)


@bp.post("/validate/i/id=<int:item_id>")
@login_required
def validate(item_id):
    flashes = []
    code = 406
    reservation = None
    item = Items.get({"id": item_id})
    if item:
        data = request.json
        if data.get("startDate") and data.get("endDate"):
            date_started = json_date_to_python_date(data["startDate"])
            date_ended = json_date_to_python_date(data["endDate"])

            rental_range = {
                "date_started": date_started,
                "date_ended": date_ended
            }
            form_check = validate_rental_bounds(item, rental_range)
            if form_check["is_valid"]:
                rental_data = {
                    "renter_id": g.user_id,
                    "item_id": item.id,
                    "date_started": date_started,
                    "date_ended": date_ended
                }
                discount = data.get("isDiscounted", False)
                reservation, action, waitlist_ad = create_reservation(rental_data, discount)
                if reservation:
                    reservation = reservation.to_dict()
                    code = 200
                else:
                    flashes.append(waitlist_ad)
                flashes.append(action)
            else:
                flashes.append(form_check["message"])
        else:
            flashes.append("There was an error getting the dates you set, make sure they're in 'MM/DD/YYYY'.")
        return { "reservation": reservation, "flashes": flashes }, code
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404
