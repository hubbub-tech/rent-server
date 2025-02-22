from flask import Blueprint, make_response, request

from src.models import Users
from src.models import Items
from src.models import Addresses

from src.utils.settings import CODE_2_OK, CODE_4_NOT_FOUND

bp = Blueprint("view", __name__)


@bp.get("/accounts/u/id=<int:user_id>")
def view_account(user_id):
    user = Users.get({"id": user_id})

    if user is None:
        errors = ["Sorry, we cannot find this user!"]
        response = make_response({"messages": errors}, CODE_4_NOT_FOUND)
        return response

    address_pkeys = user.to_query_address()
    address = Addresses.get(address_pkeys)

    user_to_dict = user.to_dict()
    user_to_dict["address"] = address.to_dict()

    listed_items = Items.filter({"lister_id": user.id})

    listed_items_to_dict = []
    for item in listed_items:
        item_to_dict = item.to_dict()
        listed_items_to_dict.append(item_to_dict)

    data = {"user": user_to_dict, "photo_url": None, "listed_items": listed_items_to_dict}
    response = make_response(data, CODE_2_OK)
    return response
