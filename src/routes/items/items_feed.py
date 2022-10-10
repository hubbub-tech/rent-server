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

bp = Blueprint('feed', __name__)


@bp.get("/items/feed")
@login_optional
def item_feed():

    search_term = request.args.get("search", None)
    page_limit = request.args.get("limit", 50) # Not in use right now
    page_number = request.args.get("page", 1) # Not in use right now

    if search_term:
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

            items_to_dict.append(item_to_dict)
        else:
            Items.set({ "id": item.id }, { "is_transactable": False })

            email_data = get_item_expiration_email(item) # WARNING
            send_async_email.apply_async(kwargs=email_data.to_dict())

    items_to_dict_sorted = json_sorted(items_to_dict, "next_available_start")
    items_to_dict_sorted = json_sorted(items_to_dict_sorted, "is_featured")

    if g.user_id:
        user = Users.get({ "id": g.user_id })
        if user.address_lat:
            address = Addresses.get({ "lat": user.address_lat, "lng": user.address_lng })
            zip_code = address.get_zip_code()
        else:
            zip_code = None
    else:
        zip_code = None

    data = { "items": items_to_dict_sorted, "zip_code": zip_code }
    response = make_response(data, 200)
    return response
