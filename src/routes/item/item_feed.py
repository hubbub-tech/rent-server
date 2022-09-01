from flask import Blueprint, make_response, request

from src.models import Items, Calendars

from src.utils import json_sorted
from src.utils.classes import Recommender

from src.utils.settings import AWS

bp = Blueprint('feed', __name__)


@bp.get("/inventory")
def item_feed():

    search_term = request.args.get("search", None)
    page_limit = request.args.get("limit", 50) # Not in use right now
    page_number = request.args.get("page", 1) # Not in use right now

    if search_term:
        recommender = Recommender()
        items = recommender.search_for(search_term)
    else:
        items = Items.filter({"is_visible": True, "is_transactable": True})

    photo_url = AWS.get_url(dir="items")

    items_to_dict = []
    for item in items:
        tags = item.get_tags()
        item_calendar = Calendars.get({"id": item.id})
        next_start, next_end  = item_calendar.next_availability()

        item_to_dict = item.to_dict()
        item_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
        item_to_dict["tags"] = tags

        items_to_dict.append(item_to_dict)

    items_to_dict_sorted = json_sorted(items_to_dict, "next_available_start")
    items_to_dict_sorted = json_sorted(items_to_dict_sorted, "is_featured")

    data = { "items": items_to_dict_sorted, "photo_url": photo_url }
    response = make_response(data, 200)
    return response
