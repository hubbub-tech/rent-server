from flask import Blueprint, make_response, request, g

from src.models import Items

from src.utils import create_address
from src.utils import login_required

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_UNAUTHORIZED,
    CODE_4_NOT_FOUND,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("edit", __name__)


@bp.post("/items/edit")
@login_required
def edit_item():

    item_id = request.args.get("id", None)
    item = Items.get({"id": item_id})

    if item is None:
        error = "We can't seem to find the item that you're looking for."
        response = make_response({"message": error}, CODE_4_NOT_FOUND)
        return response

    if item.lister_id != g.user_id:
        error = "You are not authorized to edit this item."
        response = make_response({"message": error}, CODE_4_UNAUTHORIZED)
        return response

    try:
        new_name = request.json["name"]

        new_address_formatted = request.json["address"]["formatted"]
        new_address_lat = request.json["address"]["lat"]
        new_address_lng = request.json["address"]["lng"]
    except KeyError:
        error = "Missing data in your attempt to edit. Try again."
        response = make_response({"message": error}, CODE_4_BAD_REQUEST)
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    address_data = {
        "name": new_name,
        "address_lat": new_address_lat,
        "address_lng": new_address_lng
    }

    address = create_address(address_data)

    Items.set({"id": item.id}, address_data)

    message = "Your edit requests have been received. Thanks!"
    response = make_response({"message": message}, CODE_2_OK)
    return response
