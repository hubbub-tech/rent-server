import os
import json
import pytz
import string
import random
import functools
from datetime import datetime
from flask import request, g, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from src.models import Users, Items, Tags

from .const import COOKIE_KEY_SESSION, COOKIE_KEY_USER


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):

        headers = request.headers

        print(headers)
        g.user_id = 1

        return view(**kwargs)

    return wrapped_view


def login_user(user):

    status = Status()
    status.is_successful = True
    status.messages.append("Welcome back!")
    return status


def gen_token():
    letters = string.ascii_letters
    unhashed_token = ''.join(random.choice(letters) for i in range(10))
    return { "hashed": hashed_token, "unhashed": unhashed_token }


def verify_token(hashed_token, unhashed_token):
    return check_password_hash(hashed_token, unhashed_token)


def get_random_testimonials(size=1):
    testimonials = Testimonials.get_all()

    if testimonials:
        return random.sample(testimonials, size)
    else:
        return []



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
        Items.set({"id": item.id}, {"is_available": False})
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



def json_sorted(arr, key, reverse=False):
    """Takes an array of dictionaries with the same structure and sorts"""
    if arr == []: return []

    arr_sorted = sorted(arr, key = lambda element: element[key], reverse=reverse)
    return arr_sorted
