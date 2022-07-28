from flask import Blueprint

bp = Blueprint("account", __name__)


@bp.get("/accounts/u/id=<int:id>")
@login_required
def account(id):
    searched_user = Users.get({"id": id})
    user_url = AWS.get_url(dir="users")
    item_url = AWS.get_url(dir="items")
    if searched_user:
        user_to_dict = searched_user.to_dict()
        user_to_dict["name"] = searched_user.name
        user_to_dict["cart"] = searched_user.cart.to_dict()
        user_to_dict["profile"] = searched_user.profile.to_dict()
        listings = Items.filter({"lister_id": searched_user.id})
        listings_to_dict = []
        for item in listings:
            item_to_dict = item.to_dict()
            next_start, next_end  = item.calendar.next_availability()
            item_to_dict["calendar"] = item.calendar.to_dict()
            item_to_dict["lister"] = user_to_dict
            item_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
            item_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
            item_to_dict["details"] = item.details.to_dict()
            listings_to_dict.append(item_to_dict)
        return {
            "photo_url": {"user": user_url, "item": item_url},
            "user": user_to_dict,
            "listings": listings_to_dict
        }
    else:
        return {"flashes": ["this user does not exist at the moment."]}, 404


@bp.post("/accounts/u/address/submit")
@login_required
def edit_address_submit():
    flashes = []
    data = request.json
    form_data = {
        "line_1": data["address"]["line_1"],
        "line_2": data["address"]["line_2"],
        "zip": data["address"]["zip"],
        "city": data["address"]["city"],
        "state": data["address"]["state"]
    }
    address = Addresses.filter(form_data)
    if not address: address = Addresses.insert(form_data)

    Users.set({"id": g.user_id}, {
        "address_line_1": form_data["line_1"],
        "address_line_2": form_data["line_2"],
        "address_zip": form_data["zip"]
    })
    flashes.append("You successfully changed your address!")
    return {"flashes": flashes}, 200
