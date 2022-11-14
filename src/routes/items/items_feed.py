import json
from datetime import datetime
from flask import Blueprint, make_response, request, g, redirect, stream_with_context,Response

from src.models import Items, Calendars
from src.models import Users
from src.models import Addresses

from src.utils import json_sorted
from src.utils import login_optional
from src.utils.classes import Recommender

from src.utils import send_async_email
from src.utils import get_item_expiration_email

from src.utils.settings import aws_config, CLIENT_DOMAIN

from src.utils.settings import (
    CODE_2_OK,
    CODE_3_REDIRECT,
    CODE_4_BAD_REQUEST,
    CODE_5_SERVER_ERROR
)

bp = Blueprint('feed', __name__)


@bp.get('/items/stream')
def item_stream():
    prefix = request.args.get("prefix", None)
    count = request.args.get("count", None)
    streaming_still = True

    def stream_messages_to_client():
        i = 0
        while i < int(count):
            try:
                message = f"data: {prefix}-the bird is the word, num: {i}\n\n"
                i += 1
            except:
                message = "data: something is going wrong...\n\n"
                i += 1

            streaming_still = True
            yield message

    response = Response(stream_with_context(
        stream_messages_to_client()
    ), content_type='text/event-stream')

    # print(response.data)
    return response


@bp.get("/items/feed")
@login_optional
def item_feed():

    ts_started = request.args.get("start", None) # TIMESTAMP in seconds
    ts_ended = request.args.get("end", None) # TIMESTAMP in seconds
    search_term = request.args.get("search", None)

    # page_limit = request.args.get("limit", 50) # Not in use right now
    # page_number = request.args.get("page", 1) # Not in use right now

    try:
        if ts_started:
            dt_started = datetime.fromtimestamp(ts_started)
        else:
            dt_started = datetime.min

        if ts_ended:
            dt_ended = datetime.fromtimestamp(ts_ended)
        else:
            dt_ended = datetime.max
    except:
        dt_started = datetime.min
        dt_ended = datetime.max

    live_items = Items.filter({ "is_transactable": True, "is_visible": True })
    item_ids = Reservations.get_item_id_by_bounds({ "lower": dt_started, "upper": dt_ended })

    for item in live_items:
        if item.id not in item_ids:
            pass

    recommender = Recommender()
    if search_term:
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
        elif item.is_transactable or item.is_visible:
            Items.set({ "id": item.id }, { "is_transactable": False, "is_visible": False })

            email_data = get_item_expiration_email(item) # WARNING
            send_async_email.apply_async(kwargs=email_data.to_dict())

    items_to_dict_sorted = json_sorted(items_to_dict, "next_available_start")
    items_to_dict_sorted = json_sorted(items_to_dict_sorted, "is_featured")

    if g.user_id:
        user = Users.get({ "id": g.user_id })
        lat = user.address_lat
        lng = user.address_lng
    else:
        lat = None
        lng = None

    data = { "items": items_to_dict_sorted, "user_address_lat": lat, "user_address_lng": lng }
    response = make_response(data, CODE_2_OK)
    return response



@bp.post("/items/feed/dates")
@login_optional
def item_feed_date_search():


    search_term = request.json.get("search", None)

    if not ts_started and not ts_ended:
        redirect_url = f"{CLIENT_DOMAIN}/items/feed"
        if search_term:
            redirect_url += f"?search={search_term}"
        return redirect(redirect_url, code=CODE_3_REDIRECT)

    try:
        if ts_started:
            dt_started = datetime.fromtimestamp(ts_started)
        else:
            dt_started = None
        if ts_ended:
            dt_ended = datetime.fromtimestamp(ts_ended)
        else:
            dt_ended = None
    except KeyError:
        error = "Your dates couldn't be processed. Try again."
        response = make_response({"message": error}, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    recommender = Recommender()
    items = recommender.search_by_dates(dt_started, dt_ended, search_term)

    items_to_dict = []
    for item in items:
        tags = item.get_tags()
        item_calendar = Calendars.get({"id": item.id})
        next_start, next_end = item_calendar.next_availability()

        if next_start and next_end:
            item_to_dict = item.to_dict()
            item_to_dict["next_available_start"] = datetime.timestamp(next_start)
            item_to_dict["next_available_end"] = datetime.timestamp(next_end)
            item_to_dict["tags"] = tags

            item_to_dict["image_url"] = aws_config.get_base_url() + f"/items/{item.id}.jpg"

            items_to_dict.append(item_to_dict)
        elif item.is_transactable or item.is_visible:
            Items.set({ "id": item.id }, { "is_transactable": False, "is_visible": False })

            email_data = get_item_expiration_email(item) # WARNING
            send_async_email.apply_async(kwargs=email_data.to_dict())

    if g.user_id:
        user = Users.get({ "id": g.user_id })
        lat = user.address_lat
        lng = user.address_lng
    else:
        lat = None
        lng = None

    data = { "items": items_to_dict, "user_address_lat": lat, "user_address_lng": lng }
    response = make_response(data, CODE_2_OK)
    return response
