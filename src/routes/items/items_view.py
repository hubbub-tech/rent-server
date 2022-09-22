from datetime import datetime
from flask import Blueprint, make_response

from src.models import Users
from src.models import Addresses
from src.models import Items
from src.models import Calendars

from src.utils import login_required

from src.utils.settings import AWS
from src.utils.classes import Recommender

bp = Blueprint("view", __name__)


@bp.get("/item/<int:item_id>")
def view_item(item_id):

    item = Items.get({"id": item_id})

    if item is None:
        errors = ["This item does not exist at the moment."]
        response = make_response({"messages": errors}, 404)
        return response

    lister = Users.get({"id": item.lister_id})

    item_calendar = Calendars.get({"id": item.id})
    next_start, next_end = item_calendar.next_availability(days_buffer=1)

    item_addr_dict = item.to_query_address()
    item_address = Addresses.get(item_addr_dict)

    item_to_dict = item.to_dict()
    item_to_dict["lister_name"] = lister.name
    item_to_dict["address"] = item_address.to_dict()
    item_to_dict["calendar"] = item_calendar.to_dict()
    item_to_dict["calendar"]["next_avail_date_start"] = datetime.timestamp(next_start)
    item_to_dict["calendar"]["next_avail_date_end"] = datetime.timestamp(next_end)

    item_to_dict["calendar"]["available_days_in_next_90"] = item_calendar.available_days_in_next(90)

    item_to_dict["tags"] = item.get_tags()

    recommender = Recommender()
    recommendations = recommender.on(item)

    recs_to_dict = []
    for rec in recommendations:
        if rec.id == item.id: continue

        rec_addr_dict = rec.to_query_address()
        rec_address = Addresses.get(rec_addr_dict)

        rec_calendar = Calendars.get({"id": rec.id})
        next_start, next_end = rec_calendar.next_availability(days_buffer=1)

        rec_to_dict = rec.to_dict()
        rec_to_dict["calendar"] = rec_calendar.to_dict()
        rec_to_dict["calendar"]["next_avail_date_start"] = datetime.timestamp(next_start)
        rec_to_dict["calendar"]["next_avail_date_end"] = datetime.timestamp(next_end)

        recs_to_dict.append(rec_to_dict)

    data = { "item": item_to_dict, "recommendations": recs_to_dict }

    response = make_response(data, 200)
    return response
