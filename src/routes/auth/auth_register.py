

import requests
from flask import Blueprint, make_response, request
from werkzeug.security import generate_password_hash

from src.models import Users

from src.utils import create_user
from src.utils import get_welcome_email
from src.utils import upload_email_data
from src.utils import validate_registration
from src.utils import strip_non_numericals
from src.utils import CaptchaConfig
from src.utils import gen_token
from src.utils import login_user

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_FORBIDDEN,
    CODE_4_UNAUTHORIZED,
    CODE_5_SERVER_ERROR
)

bp = Blueprint('register', __name__)

@bp.post('/register')
def register():

    # Frontend takes care of individual checks, bulking them here instead
    try:
        first_name = request.json["user"]["firstName"]
        last_name = request.json["user"]["lastName"]

        phone = request.json["user"]["phone"]

        phone_stripped = strip_non_numericals(phone)

        user_data = {
            "email": request.json["user"]["email"].lower(),
            "password": request.json["user"]["password"],
            "name": f"{first_name}+{last_name}",
            "phone": phone_stripped,
            "bio": "I love Hubbub!",
            "profile_pic": False,
            "is_blocked": False
        }

        recaptcha_token = request.json["recaptchaToken"]

    except KeyError:
        error = "Missing data to complete your sign up! Please, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    recaptcha_data = {
        "secret": CaptchaConfig.ReCAPTCHA_SERVER_APIKEY,
        "response": recaptcha_token
    }

    captcha_response = requests.post(CaptchaConfig.ReCAPTCHA_VERIFY_URL, data=recaptcha_data)
    captcha_response.raise_for_status()
    captcha = captcha_response.json()

    if not captcha["success"]:
        error = "Sorry, registration failed! Try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response

    user_data["password"] = generate_password_hash(user_data["password"])
    status = validate_registration(user_data)

    if status.is_successful == False:
        error = status.message
        response = make_response({ "message": error }, CODE_4_FORBIDDEN)
        return response

    new_user = create_user(user_data)

    email_data = get_welcome_email(new_user)

    upload_email_data(email_data, email_type="auth_register")

    status = login_user(new_user)

    if status.is_successful:
        session_key = gen_token()
        Users.set({"id": new_user.id}, {"session_key": session_key["unhashed"]})

        data = {
            "user_id": new_user.id,
            "message": "Welcome to the Hubbub community!",
            "session_token": session_key["hashed"]
        }
        response = make_response(data, CODE_2_OK)
        return response
    else:
        errors = status.message
        response = make_response({ "message": error }, CODE_4_UNAUTHORIZED)
        return response
