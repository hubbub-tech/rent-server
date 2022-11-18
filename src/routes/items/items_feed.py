from datetime import datetime
from flask import Blueprint, make_response, request, g

from src.models import Items, Calendars
from src.models import Users
from src.models import Addresses

from src.utils import json_sorted
from src.utils import login_optional
from src.utils.classes import Recommender

from src.utils import send_async_email
from src.utils import get_item_expiration_email

from src.utils.settings import aws_config

bp = Blueprint('feed', __name__)


@bp.get("/items/feed")
@login_optional
def item_feed():

    ts_start_json = request.args.get("ts_start", None)
    ts_end_json = request.args.get("ts_end", None)

    search_term = request.args.get("search", None)
    page_limit = request.args.get("limit", 50) # Not in use right now
    page_number = request.args.get("page", 1) # Not in use right now

    if ts_start_json and ts_end_json:
        try:
            dt_start = datetime.fromtimestamp(int(ts_start_json))
            dt_end = datetime.fromtimestamp(int(ts_end_json))

            availability = { "dt_lbound": dt_start, "dt_ubound": dt_end }
            items = Items.get_by(availability)

            if search_term:
                recommender = Recommender()
                items = recommender.match(search_term, items)
        except:
            # log an error here
            items = Items.filter({"is_visible": True, "is_transactable": True})
    elif search_term:
        recommender = Recommender()
        items = recommender.search_for(search_term)
    else:
        items = Items.filter({"is_visible": True, "is_transactable": True})

    items_to_dict = []
    for item in items:
        tags = item.get_tags()
        item_calendar = Calendars.get({"id": item.id})
        next_start, next_end  = item_calendar.next_availability()

        if next_start and next_end:
            item_to_dict = item.to_dict()
            item_to_dict["next_available_start"] = datetime.timestamp(next_start)
            item_to_dict["next_available_end"] = datetime.timestamp(next_end)
            item_to_dict["tags"] = tags

            item_to_dict["image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"

            items_to_dict.append(item_to_dict)
        else:
            Items.set({ "id": item.id }, { "is_transactable": False })

            email_data = get_item_expiration_email(item) # WARNING
            send_async_email.apply_async(kwargs=email_data.to_dict())

    items_to_dict_sorted = json_sorted(items_to_dict, "next_available_start")
    items_to_dict_sorted = json_sorted(items_to_dict_sorted, "is_featured", reverse=True)

    if g.user_id:
        user = Users.get({ "id": g.user_id })
        lat = user.address_lat
        lng = user.address_lng
    else:
        lat = None
        lng = None

    data = { "items": items_to_dict_sorted, "user_address_lat": lat, "user_address_lng": lng }
    response = make_response(data, 200)
    return response
