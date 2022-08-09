from flask import Blueprint, make_response

from src.models import Users
from src.models import Addresses
from src.models import Items, Calendars

bp = Blueprint("view", __name__)


@bp.get("/items/view/id=<int:item_id>")
def view_item(item_id):
    photo_url = AWS.get_url(dir="items")
    item = Items.get({"id": item_id})

    if item is None:
        errors = ["This item does not exist at the moment."]
        response = make_response({"messages": errors}, 404)
        return response

    lister = Users.get({"id": item.lister_id})

    item_calendar = Calendars.get({"id": item.id})
    next_start, next_end = item_calendar.next_availability(days_offset=1)

    item_addr_dict = item.to_query_address()
    item_address = Addresses.get(item_addr_dict)

    item_to_dict = item.to_dict()
    item_to_dict["lister_name"] = lister.name
    item_to_dict["address"] = item_address.to_dict()
    item_to_dict["calendar"] = item_calendar.to_dict()
    item_to_dict["calendar"]["next_avail_date_start"] = next_start.strftime("%Y-%m-%d")
    item_to_dict["calendar"]["next_avail_date_end"] = next_end.strftime("%Y-%m-%d")

    recommendations = get_recommendations(item.name)
    recs_to_dict = []
    for rec in recommendations:
        if rec.id == item.id: continue

        rec_addr_dict = rec.to_query_address()
        rec_address = Addresses.get(rec_addr_dict)

        rec_calendar = Calendars.get({"id": rec.id})
        next_start, next_end = rec_calendar.next_availability(days_offset=1)

        rec_to_dict = rec.to_dict()
        rec_to_dict["next_avail_date_start"] = next_start.strftime("%Y-%m-%d")
        rec_to_dict["next_avail_date_end"] = next_end.strftime("%Y-%m-%d")

        recs_to_dict.append(rec_to_dict)

    data = { "item": item_to_dict, "photo_url": photo_url, "recommendations": recs_to_dict }
    response = make_response(data, 200)
    return response
