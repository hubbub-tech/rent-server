from flask import Blueprint, make_response, request, g

from src.models import Items

from src.utils import create_address
from src.utils import login_required


bp = Blueprint("edit", __name__)


@bp.post("/items/edit")
@login_required
def edit_item():

    item_id = request.args.get("id", None)
    item = Items.get({"id": item_id})

    if item is None:
        error = "We can't seem to find the item that you're looking for."
        response = make_response({"message": error}, 404)
        return response

    if item.lister_id != g.user_id:
        error = "You are not authorized to edit this item."
        response = make_response({"message": error}, 403)
        return response

    try:
        new_name = request.json["name"]

        new_address_formatted = request.json["address"]["formatted"]
        new_address_lat = request.json["address"]["lat"]
        new_address_lng = request.json["address"]["lng"]
    except KeyError:
        error = "Missing data in your attempt to edit. Try again."
        response = make_response({"message": error}, 401)
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, 500)
        return response

    # NOTE: parse for address data
    address = create_address(new_address)

    Items.set({"id": item.id}, {
        "name": new_name,
        "address_lat": address.lat,
        "address_lng": address.lng
    })

    message = "Your edit requests have been received. Thanks!"
    response = make_response({"message": message}, 200)
    return response
