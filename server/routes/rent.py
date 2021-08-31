import random
from distutils.util import strtobool
from datetime import datetime, date, timedelta
from flask import Blueprint, g, request, session, make_response

from blubber_orm import Users, Orders, Reservations
from blubber_orm import Items, Tags, Details, Calendars

from server.tools.settings import login_required, AWS
from server.tools.settings import create_rental_token, json_sort
from server.tools.settings import get_recommendations, search_items

from server.tools.build import create_reservation, validate_rental_bounds
from server.tools import blubber_instances_to_dict, json_date_to_python_date, is_item_in_itemlist

bp = Blueprint('rent', __name__)

@bp.get("/inventory", defaults={"search": None})
@bp.get("/inventory/search=<search>")
def inventory(search):
    photo_url = AWS.get_url("items")
    if search:
        listings = search_items(search)
    else:
        listings = Items.filter({"is_available": True})
    listings_to_dict = []
    featured_to_dict = []
    for item in listings:
        lister = Users.get(item.lister_id)
        tags = Tags.by_item(item)
        item_to_dict = item.to_dict()
        next_start, next_end  = item.calendar.next_availability()
        item_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
        item_to_dict["details"] = item.details.to_dict()
        item_to_dict["lister"] = lister.to_dict()
        item_to_dict["lister"]["name"] = lister.name
        item_to_dict["tags"] = [tag.name for tag in tags]
        if item.is_featured:
            featured_to_dict.append(item_to_dict)
        else:
            listings_to_dict.append(item_to_dict)
    json_sort(listings_to_dict, "next_available_start")
    for item in listings_to_dict:
        featured_to_dict.append(item)
    return {
        "items": featured_to_dict,
        "photo_url": photo_url
        }

@bp.get("/inventory/i/id=<int:item_id>")
def view_item(item_id):
    photo_url = AWS.get_url("items")
    item = Items.get(item_id)
    if item:
        lister = Users.get(item.lister_id)
        item_to_dict = item.to_dict()
        item_to_dict["lister_name"] = lister.name
        next_start, next_end = item.calendar.next_availability()
        item_to_dict["address"] = item.address.to_dict()
        item_to_dict["details"] = item.details.to_dict()
        item_to_dict["calendar"] = item.calendar.to_dict()
        item_to_dict["calendar"]["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["calendar"]["next_available_end"] = next_end.strftime("%Y-%m-%d")

        recommendations = get_recommendations(item.name)
        recs_to_dict = []
        for rec in recommendations:
            lister = Users.get(rec.lister_id)
            rec_to_dict = rec.to_dict()
            next_start, next_end  = rec.calendar.next_availability()
            rec_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
            rec_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
            rec_to_dict["details"] = rec.details.to_dict()
            rec_to_dict["lister"] = lister.to_dict()
            rec_to_dict["lister"]["name"] = lister.name
            recs_to_dict.append(rec_to_dict)
        return {
            "item": item_to_dict,
            "photo_url": photo_url,
            "recommendations": recs_to_dict
        }
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404

@bp.post("/validate/i/id=<int:item_id>")
@login_required
def validate(item_id):
    flashes = []
    code = 406
    reservation = None
    item = Items.get(item_id)
    if item:
        data = request.json
        if data.get("startDate") and data.get("endDate"):
            date_started = json_date_to_python_date(data["startDate"])
            date_ended = json_date_to_python_date(data["endDate"])

            rental_range = {
                "date_started": date_started,
                "date_ended": date_ended
            }
            form_check = validate_rental_bounds(item, rental_range)
            if form_check["is_valid"]:
                rental_data = {
                    "renter_id": g.user_id,
                    "item_id": item.id,
                    "date_started": date_started,
                    "date_ended": date_ended
                }
                discount = data.get("isDiscounted", False)
                reservation, action, waitlist_ad = create_reservation(rental_data, discount)
                if reservation:
                    reservation = reservation.to_dict()
                    code = 200
                else:
                    flashes.append(waitlist_ad)
                flashes.append(action)
            else:
                flashes.append(form_check["message"])
        else:
            flashes.append("There was an error getting the dates you set, make sure they're in 'MM/DD/YYYY'.")
        return { "reservation": reservation, "flashes": flashes }, code
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404

@bp.post("/add/i/id=<int:item_id>")
@login_required
def add_to_cart(item_id):
    item = Items.get(item_id)
    if item:
        data = request.json
        if g.user.id != item.lister_id:
            if data.get("startDate") and data.get("endDate"):
                date_started = json_date_to_python_date(data["startDate"])
                date_ended = json_date_to_python_date(data["endDate"])
                if g.user.cart.contains(item):
                    message = "The item is already in your cart."
                else:
                    reservation_keys = {
                        "renter_id": g.user_id,
                        "item_id": item_id,
                        "date_started": date_started,
                        "date_ended": date_ended
                    }
                    reservation = Reservations.get(reservation_keys) #NOTE: assumes res exists
                    g.user.cart.add(reservation)
                    message = "The item has been added to your cart!"
            else:
                if g.user.cart.contains(item):
                    message = "The item is already in your cart."
                else:
                    g.user.cart.add_without_reservation(item)
                    message = "The item has been added to your cart!"
            return {"flashes": [message]}, 200
        else:
            return {"flashes": ["Sorry, you cannot rent an item from yourself."]}, 406
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404

#TODO: in the new version of the backend, user must propose new dates to reset
#takes data from changed reservation by deleting the temporary res created previously
@bp.post("/update/i/id=<int:item_id>")
@login_required
def update(item_id):
    flashes = []
    errors = []
    code = 406
    reservation = None
    item = Items.get(item_id)
    if item:
        data = request.json
        if data.get("startDate") and data.get("endDate"):
            #NOTE: filter always returns a list but should only have 1 item this time
            _reservation = Reservations.filter({
                "item_id": item_id,
                "renter_id": g.user_id,
                "is_in_cart": True
            })
            if _reservation:
                old_reservation, *_ = _reservation
                g.user.cart.remove(old_reservation)
            else:
                g.user.cart.remove_without_reservation(item)

            new_date_started = json_date_to_python_date(data["startDate"])
            new_date_ended = json_date_to_python_date(data["endDate"])
            rental_range = {
                "date_started": new_date_started,
                "date_ended": new_date_ended
            }
            form_check = validate_rental_bounds(item, rental_range)
            if form_check["is_valid"]:
                rental_data = {
                    "renter_id": g.user_id,
                    "item_id": item.id,
                    "date_started": new_date_started,
                    "date_ended": new_date_ended
                }
                reservation, action, waitlist_ad = create_reservation(rental_data)
                if reservation:
                    g.user.cart.add(reservation)
                    reservation = reservation.to_dict()
                    action = "Your reservation has been updated successfully!"
                    code = 200
                else:
                    g.user.cart.add_without_reservation(item)
                    flashes.append(waitlist_ad)
                flashes.append(action)
            else:
                g.user.cart.add_without_reservation(item)
                flashes.append(form_check["message"])
        else:
            flashes.append("There was an error getting the dates you set, make sure they're in 'MM/DD/YYYY'.")
        return {"flashes": flashes}, code
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404

@bp.post("/remove/i/id=<int:item_id>")
@login_required
def remove_from_cart(item_id):
    flashes = []
    format = "%Y-%m-%d" # this format when taking dates thru url
    item = Items.get(item_id)
    if item:
        data = request.json
        if data.get("startDate") and data.get("endDate"):
            reservation_keys = {
                "renter_id": g.user_id,
                "item_id": item_id,
                "date_started": datetime.strptime(data.get("startDate"), format).date(),
                "date_ended": datetime.strptime(data.get("endDate"), format).date(),
            }
            reservation = Reservations.get(reservation_keys)
            g.user.cart.remove(reservation)
        else:
            g.user.cart.remove_without_reservation(item)
        flashes.append(f"The {item.name} has been removed from your cart.")
        data = {"flashes": flashes}
        response = make_response(data, 200)
        return response
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404

@bp.get("/checkout")
@login_required
def checkout():
    photo_url = AWS.get_url("items")
    items = [] #for json
    is_ready = g.user.cart.size() > 0
    ready_to_order_items = g.user.cart.get_reserved_contents()
    _cart_contents = g.user.cart.contents
    for item in _cart_contents:
        if is_item_in_itemlist(item, ready_to_order_items):
            reservation, *_ = Reservations.filter({
                "renter_id": g.user_id,
                "item_id": item.id,
                "is_in_cart": True
            })
            #FUNC: has someone ordered the item since you've added it to cart?
            if item.calendar.scheduler(reservation) == False:
                g.user.cart.remove(reservation)
                g.user.cart.add_without_reservation(item)
            elif not reservation.is_calendared:
                if item.calendar.scheduler(reservation) is None:
                    Items.set(item.id, {"is_available": False})
                    g.user.cart.remove(reservation)
                elif item.calendar.scheduler(reservation):
                    item_to_dict = item.to_dict()
                    item_to_dict["reservation"] = reservation.to_dict()
        else:
            is_ready = False
            item_to_dict = item.to_dict()
            item_to_dict["reservation"] = ''
        item_to_dict["details"] = item.details.to_dict()
        item_to_dict["calendar"] = item.calendar.to_dict()
        next_start, next_end = item.calendar.next_availability()
        item_to_dict["calendar"]["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["calendar"]["next_available_end"] = next_end.strftime("%Y-%m-%d")
        items.append(item_to_dict)
    return {
        "is_ready": is_ready,
        "photo_url": photo_url,
        "user": g.user.to_dict(),
        "cart": g.user.cart.to_dict(),
        "items": items
    }
