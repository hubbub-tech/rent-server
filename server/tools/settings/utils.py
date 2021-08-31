import json
import pytz
import string
import random
import functools
from datetime import datetime
from flask import session, request, flash, g, make_response
from blubber_orm import Users, Items, Details, Tags
from werkzeug.security import check_password_hash, generate_password_hash

from .const import COOKIE_KEY_SESSION, COOKIE_KEY_USER

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if request.method == 'POST':
            if request.json: data = request.json
            elif request.form: data = request.form
            else: return {"flashes": "No data was sent, try again."}, 403

            session = data.get(COOKIE_KEY_SESSION)
            user_id = data.get(COOKIE_KEY_USER)
        else:
            session = request.cookies.get(COOKIE_KEY_SESSION)
            user_id = request.cookies.get(COOKIE_KEY_USER)

        is_authenticated = verify_auth_token(session, user_id)
        if is_authenticated:
            g.user_id = int(user_id)
            g.user = Users.get(user_id)
            return view(**kwargs)
        else:
            data = {"flashes": ["Your login session has ended. Login again."]}
            response = make_response(data, 403)
            return response
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
    letters = string.ascii_letters
    new_session = ''.join(random.choice(letters) for i in range(10))
    user.session = new_session
    hashed_token = generate_password_hash(new_session)
    return hashed_token

def verify_auth_token(hashed_token, user_id):
    if user_id and hashed_token:
        user = Users.get(user_id)
        if user.session:
            return check_password_hash(hashed_token, user.session)
    return False

def get_recommendations(item_name):
    # Split the item name by spaces
    item_name_components = item_name.split(" ")

    # Take the last word in the name--this is likely to be an identifier as to what it is
    searchable = f"%{item_name_components[-1]}%"

    items = Items.like("name", searchable)
    details = Details.like("description", searchable)
    unfiltered_items = [detail.item for detail in details]

    # remove duplicates
    filtered_items = []
    id_tracker = []
    for item in unfiltered_items:
        if item.is_available and item.id not in id_tracker:
            id_tracker.append(item.id)
            filtered_items.append(item)

    # get recommendations
    size = 3
    recommendations = []
    if len(filtered_items) > size:
        recommendations = random.sample(filtered_items, size)
    else:
        recommendations = filtered_items
    return recommendations

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
    waitlist_message = "You can also join the waitlist for this item in the form at the bottom of the page, and we will get back to you ASAP!"

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

def append_sort(arr, element, key):
    """element should be type dictionary containing the passed key"""
    if len(arr) == 0:
        arr.append(element)
    else:
        i = 0
        while i < len(arr):
            if arr[i][key] >= element[key]:
                arr.insert(i, element)
                break
            elif i == len(arr) - 1:
                arr.append(element)
                break
            i += 1

def json_sort(arr, key, reverse=False):
    """Takes an array of dictionaries with the same structure and sorts"""
    arr.sort(key = lambda element: element[key], reverse=reverse)
