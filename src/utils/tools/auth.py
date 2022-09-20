import string
import random
import functools
from datetime import datetime
from flask import request, g, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from src.models import Users, Items, Tags

from src.utils.classes import Status
from src.utils.settings import COOKIE_KEY_SESSION, COOKIE_KEY_USER


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = request.cookies.get("userId")
        session_key_hashed = request.cookies.get("sessionToken")

        user = Users.get({"id": user_id})

        is_authorized = verify_token(session_key_hashed, user.session_key)

        if is_authorized == False:
            errors = ["Sorry, you're not authorized for this page."]
            response = make_response({ "messages": errors }, 403)
            return response

        g.user_id = user.id
        g.user_email = user.email
        g.user_session_key = user.session_key
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
    hashed_token = generate_password_hash(unhashed_token)
    return { "hashed": hashed_token, "unhashed": unhashed_token }


def verify_token(hashed_token, unhashed_token):
    return check_password_hash(hashed_token, unhashed_token)
