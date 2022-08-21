from flask import Blueprint, make_response, request

from src.models import Items, Calendars
from src.utils import create_address


bp = Blueprint("edit", __name__)


@bp.post("/items/edit")
@login_required
def edit_item():

    item_id = request.args.get("id", None)
    item = Items.get({"id": item_id})

    if item is None:
        errors = ["We can't seem to find the item that you're looking for."]
        response = make_response({"messages": errors}, 404)
        return response

    if item.lister_id != g.user_id:
        errors = ["You are not authorized to edit this item."]
        response = make_response({"messages": errors}, 403)
        return response

    try:
        new_name = request.json["name"]
        new_address = request.json["address"]
    except KeyError:
        errors = ["Missing data in your attempt to edit. Try again."]
        response = make_response({"messages": errors}, 401)
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    address = create_address(new_address)

    Items.set({"id": item.id}, {
        "name": new_name,
        "address_line_1": address.line_1,
        "address_line_2": address.line_2,
        "address_country": address.country,
        "address_zip": address.zip,
    })

    messages = ["Your edit requests have been received. Thanks!"]
    response = make_response({"messages": messages}, 200)
    return response
