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
