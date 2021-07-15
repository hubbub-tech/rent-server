import json
import pytz
import functools
from datetime import datetime
from flask import session, request, flash, g
from blubber_orm import Users, Items, Details, Tags
from werkzeug.security import check_password_hash, generate_password_hash

from .transact import verify_rental_token

# NOTE: ONLY COMPATIBLE WITH POST METHOD ROUTES****
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        flashes = []
        if request.json:
            data = request.json
        elif request.form:
            data = request.form
        else:
            return {"flashes": flashes}, 405
        id = data["userId"]
        token = data["auth"]
        print("id", id)
        print("token", token)
        is_authenticated = verify_auth_token(token, id)
        print("is_authenticated", is_authenticated)
        if not is_authenticated:
            flashes.append('Login first to join the fun!')
            return {"flashes": flashes}, 405
        else:
            g.user_id = int(id)
            return view(**kwargs)
    return wrapped_view

def login_user(user):
    is_valid = True
    if user.is_blocked:
        is_valid = False
        message = "The admin has decided to block your account. Contact hubbubcu@gmail.com for more info."
    else:
        session.clear()
        session["user_id"] = user.id
        session["cart_size"] = user.cart.size()
        message = "You're logged in, welcome back!"
    Users.set(user.id, {"dt_last_active": datetime.now(tz=pytz.UTC)})
    return {
        "is_valid" : is_valid,
        "message" : message
        }

def create_auth_token(user):
    hashed_token = generate_password_hash(str(user.id))
    return hashed_token

def verify_auth_token(hashed_token, user_id):
    is_valid = check_password_hash(hashed_token, user_id)
    return is_valid

def search_items(search_key):
    searchable = f"%{search_key}%"
    if search_key != 'all':
        # search by tag
        unfiltered_items = []
        tags = Tags.like("tag_name", searchable)
        for tag in tags:
            unfiltered_items += Items.by_tag(tag)

        # search by item details description
        details = Details.like("description", searchable)
        unfiltered_items += [detail.item for detail in details]

        # search by item name
        unfiltered_items += Items.like("name", searchable)

        # remove duplicates
        filtered_items = []
        id_tracker = []
        for item in unfiltered_items:
            if item.is_available and item.id not in id_tracker:
                id_tracker.append(item.id)
                filtered_items.append(item)
    else:
        filtered_items = Items.filter({"is_available": True})
    return filtered_items

def generate_proposed_period(item, input_message):
    status_message = None
    waitlist_message = "You can also join the waitlist for this item <a href='https://docs.google.com/forms/d/e/1FAIpQLSflErYv4mNyPlAlPmSEO_q1xmOIYOMmafoI1-te_fx44VvKhw/viewform' target='_blank' class='alert-link'>here</a> and we will get back to you ASAP!"

    proposed_start, proposed_end = item.calendar.next_availability()
    proposed_start_str = proposed_start.strftime("%B %-d, %Y")
    proposed_end_str = proposed_end.strftime("%B %-d, %Y")
    if proposed_start < proposed_end:
        if proposed_end_str == 'December 31, 9999':
            status_message = f"{input_message} The item is free after {proposed_start_str}."
        else:
            status_message = f"{input_message} {proposed_start_str} to {proposed_end_str} is currently free."
    #if the calendar is full, item is taken off inventory
    elif proposed_start == proposed_end:
        Items.set(item.id, {"is_available": False})
        status_message = "Sorry, the item is no longer available."
    return status_message, waitlist_message
