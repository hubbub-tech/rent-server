from datetime import datetime
from flask import Blueprint, make_response, request

from src.models import Users

from src.utils import validate_login
from src.utils import gen_token
from src.utils import login_user

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_UNAUTHORIZED,
    CODE_5_SERVER_ERROR
)

bp = Blueprint('login', __name__)

@bp.post('/login')
def login():

    try:
        email = request.json["email"].lower()
        password = request.json["password"]
    except KeyError:
        error = "Please submit a username and password to log in."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    form_data = { "email": email, "password": password }
    status = validate_login(form_data)

    if status.is_successful == False:
        error = status.message
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response

    user = Users.unique({"email": email})
    status = login_user(user)

    if status.is_successful:
        session_key = gen_token()
        Users.set({"id": user.id}, {"dt_last_active": datetime.now(), "session_key": session_key["unhashed"]})

        data = {
            "user_id": user.id,
            "message": "Welcome back!",
            "session_token": session_key["hashed"]
        }
        response = make_response(data, CODE_2_OK)
        return response
    else:
        error = status.message
        response = make_response({ "message": error }, CODE_4_UNAUTHORIZED)
        return response


@bp.post('/login/callback')
def login_callback():
    pass
