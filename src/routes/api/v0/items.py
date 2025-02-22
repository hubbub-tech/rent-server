from flask import Blueprint, make_response, request

from src.models import Items
from src.models import Calendars

from src.utils import login_required

from src.utils.settings import CODE_2_OK

bp = Blueprint("items", __name__)


@bp.post("/items/create")
@login_required
def create_item():
    pass

@bp.get("/items")
@login_required
def get_items():
    item_ids = request.json["ids"]

    items_to_dict = []
    for item_id in item_ids:
        item = Items.get({"id": item_id})

        if item is None: continue

        item_calendar = Calendars.get({"id": item.id})

        item_to_dict = item.to_dict()
        item_to_dict["calendar"] = item_calendar.to_dict()
        items_to_dict.append(item_to_dict)

    data = { "items": items_to_dict }
    response = make_response(data, CODE_2_OK)
    return response
