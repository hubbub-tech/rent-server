import string
import random
import functools
from datetime import datetime
from flask import request, g, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from src.models import Users, Items, Tags

from src.utils.classes import Status


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = request.cookies.get("userId")
        session_key_hashed = request.cookies.get("sessionToken")

        if user_id:
            user = Users.get({"id": user_id})
            if user:
                is_authorized = verify_token(session_key_hashed, user.session_key)
            else:
                is_authorized = False
        else:
            is_authorized = False

        if is_authorized == False:
            error = "Login first to continue using this page."
            response = make_response({ "message": error }, 403)
            return response

        g.user_id = user.id
        g.user_email = user.email
        g.user_session_key = user.session_key

        return view(**kwargs)
    return wrapped_view


def login_optional(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user_id = request.cookies.get("userId")
        session_key_hashed = request.cookies.get("sessionToken")

        if user_id:
            user = Users.get({"id": user_id})
            if user:
                is_authorized = verify_token(session_key_hashed, user.session_key)
            else:
                is_authorized = False
        else:
            is_authorized = False

        if is_authorized == False:
            g.user_id = None
            g.user_email = None
            g.user_session_key = None
        else:
            g.user_id = user.id
            g.user_email = user.email
            g.user_session_key = user.session_key

        return view(**kwargs)
    return wrapped_view


def handle_preflight_only(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        print("Request Method", request.method)
        is_preflight_request = check_for_preflight(request)
        if is_preflight_request:
            response = make_response(204)
            # response.access_control_allow_origin = FlaskConfig.CORS_ALLOW_ORIGIN
            # response.access_control_allow_methods = ["GET", "POST", "HEAD"]
            print("Preflight path")
            return response
        else:
            return view(**kwargs)
    return wrapped_view



def check_for_preflight(req):
    is_options_method = req.method == "OPTIONS"
    has_origin_header = req.origin is not None
    has_request_method = req.access_control_request_method is not None

    is_preflight_request = is_options_method and has_origin_header and has_request_method

    return is_preflight_request


def login_user(user):

    status = Status()

    if user.is_blocked:
        status.is_successful = False
        status.message = "Sorry, your account has been blocked. Contact us at hello@hubbub.shop if this seems wrong."
    else:
        status.is_successful = True
        status.message = "Welcome back!"
    return status


def gen_token():
    letters = string.ascii_letters
    unhashed_token = ''.join(random.choice(letters) for i in range(10))
    hashed_token = generate_password_hash(unhashed_token)
    return { "hashed": hashed_token, "unhashed": unhashed_token }


def verify_token(hashed_token, unhashed_token):
    return check_password_hash(hashed_token, unhashed_token)
