from flask import Blueprint, make_response, request

from src.models import Items, Calendars
# from src.utils import json_sort
# from src.utils import search_items

bp = Blueprint('feed', __name__)


@bp.get("/items/feed")
def item_feed():

    search_term = requests.args.get("search", None)
    page_limit = requests.args.get("limit", 50) # Not in use right now
    page_number = requests.args.get("page", 1) # Not in use right now

    if search_term:
        items = search_items(search_term)
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

    items_to_dict_sorted = json_sort(items_to_dict, "next_available_start")
    items_to_dict_sorted = json_sort(items_to_dict_sorted, "is_featured")

    data = { "items": items_to_dict_sorted, "photo_url": photo_url }
    response = make_response(data, 200)
    return response
