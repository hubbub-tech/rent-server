import os
from flask import Blueprint, g, request
from flask_cors import CORS
from blubber_orm import Orders, Users, Reservations
from blubber_orm import Items, Details, Calendars, Tags
from blubber_orm import Dropoffs, Pickups

from server.tools.settings import login_required
from server.tools.settings import Config, AWS
from server.tools.settings import json_sort

bp = Blueprint('manage_items', __name__)
CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_ADMIN],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)

@bp.get("/operations/items")
@login_required
def item_dashboard():
    items_to_dict = []
    items = Items.get_all()

    for item in items:
        lister = Users.get({"id": item.lister_id})
        tags = Tags.by_item(item)
        item_to_dict = item.to_dict()
        next_start, next_end = item.calendar.next_availability()
        item_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
        item_to_dict["details"] = item.details.to_dict()
        item_to_dict["calendar"] = item.calendar.to_dict()

        item_to_dict["lister"] = lister.to_dict()
        item_to_dict["lister"]["name"] = lister.name
        item_to_dict["tags"] = [tag.name for tag in tags]
        items_to_dict.append(item_to_dict)
    json_sort(items, "dt_created")
    return { "items": items_to_dict }

@bp.get("/operations/i/id=<int:item_id>")
def item_history(item_id):
    photo_url = AWS.get_url("items")
    item = Items.get({"id": item_id})
    lister = Users.get({"id": item.lister_id})

    item_to_dict = item.to_dict()
    item_to_dict["lister"] = lister.to_dict()
    item_to_dict["lister"]["name"] = lister.name
    next_start, next_end = item.calendar.next_availability()
    item_to_dict["address"] = item.address.to_dict()
    item_to_dict["details"] = item.details.to_dict()
    item_to_dict["calendar"] = item.calendar.to_dict()
    item_to_dict["calendar"]["next_available_start"] = next_start.strftime("%Y-%m-%d")
    item_to_dict["calendar"]["next_available_end"] = next_end.strftime("%Y-%m-%d")

    orders = Orders.filter({ "item_id": item.id })
    orders_to_dict = []
    for order in orders:
        renter = Users.get({"id": order.renter_id})
        order_to_dict = order.to_dict()
        order_to_dict["renter"] = renter.to_dict()
        order_to_dict["renter"]["name"] = renter.name
        order_to_dict["reservation"] = order.reservation.to_dict()
        order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
        orders_to_dict.append(order_to_dict)
    item_to_dict["orders"] = orders_to_dict
    return {
        "item": item_to_dict,
        "photo_url": photo_url
    }

@bp.post("/operations/i/hide/id=<int:item_id>")
@login_required
def hide_item(item_id):
    data = request.json

    if data is None: return {"flashes": ["No data was sent! Try again."]}, 406

    is_available_updated = data["toggle"]
    Items.set(
        {"id": item_id},
        {"is_available": is_available_updated}
    )
    if is_available_updated:
        message = "Item has been revealed. Others can now see it in inventory."
    else:
        message = "Item has been hidden. Come back when you are ready to reveal it."

    return {"flashes": [message]}, 200


@bp.post("/operations/i/feature/id=<int:item_id>")
@login_required
def feature_item(item_id):
    data = request.json

    if data is None: return {"flashes": ["No data was sent! Try again."]}, 406

    is_featured_updated = data["toggle"]
    Items.set(
        {"id": item_id},
        {"is_featured": is_featured_updated}
    )
    if is_featured_updated:
        message = "Item has been featured. It has risen to the top of the inventory page on shop."
    else:
        message = "Item has been unfeatured. Come back when you are ready to feature it again."

    return {"flashes": [message]}, 200
