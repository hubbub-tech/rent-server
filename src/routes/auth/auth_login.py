from flask import Blueprint, make_response, request

from src.models import Users

from src.utils import validate_login
from src.utils import gen_token
from src.utils import login_user
from src.utils import login_required

bp = Blueprint('login', __name__)

@bp.post('/login')
def login():

    try:
        email = request.json["email"].lower()
        password = request.json["password"]
    except KeyError:
        errors = ["Please submit a username and password to log in."]
        response = make_response({ "messages": errors }, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    form_data = { "email": email, "password": password }
    form_check = validate_login(form_data)

    if not form_check["is_valid"]:
        errors = form_check["messages"]
        response = make_response({ "messages": errors }, 403)
        return response

    user = Users.unique({"email": email})
    login_status = login_user(user)

    if login_status["is_valid"]:
        session_key = gen_token()
        Users.set({"id": user.id}, {"session": session_key["unhashed"]})
        response = make_response({ "id": user.id, "session_key": session_key["hashed"] }, 200)
        return response
    else:
        errors = login_status["messages"]
        response = make_response({ "messages": errors }, 403)
        return response


@bp.post('/login/callback')
def login_callback():
    pass
