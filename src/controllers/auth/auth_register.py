import requests
from flask import Blueprint, make_response, request

from src.models import Users

bp = Blueprint('register', __name__)

@bp.post('/register')
def register():

    # Frontend takes care of individual checks, bulking them here instead
    try:
        first_name = request.json["user"]["firstName"]
        last_name = request.json["user"]["lastName"]

        user_data = {
            "email": request.json["user"]["email"].lower(),
            "password": request.json["user"]["password"],
            "name": f"{last_name}+{first_name}",
            "phone": request.json["user"]["phone"],
            "address_line_1": request.json["address"]["lineOne"],
            "address_line_2": request.json["address"]["lineTwo"],
            "address_country": request.json["address"]["country"],
            "address_zip": request.json["address"]["zip"],
            "bio": "I love Hubbub!",
            "profile_pic": False,
            "is_blocked": False
        }

        address_data = {
            "line_1": request.json["address"]["lineOne"],
            "line_2": request.json["address"]["lineTwo"],
            "city": request.json["address"]["city"],
            "state": request.json["address"]["state"],
            "country": request.json["address"]["country"],
            "zip": request.json["address"]["zip"]
        }
    except KeyError:
        errors = ["Missing data to complete your sign up! Please, try again."]
        response = make_response({ "messages": errors }, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    recaptcha_data = {
        "secret": Config.ReCAPTCHA_SERVER_API_KEY,
        "response": request.json.get('token')
    }

    captcha_response = requests.post(Config.ReCAPTCHA_VERIFY_URL, data=recaptcha_data)
    captcha_response.raise_for_status()
    captcha = captcha_response.json()

    if not captcha["success"]:
        errors = ["Sorry, registration failed! Try again."]
        response = make_response({ "messages": errors }, 406) # pass code from captcha
        return response

    user_data["password"] = generate_password_hash(user_data["password"])
    form_check = validate_registration(user_data)

    if not form_check["is_valid"]:
        errors = form_check["messages"]
        response = make_response({ "messages": errors }, 403)
        return response

    address = create_address(address_data)
    new_user = create_user(user_data)
    email_data = get_welcome_email(new_user)
    send_async_email.apply_async(kwargs=email_data)
    messages = ["Welcome to the Hubbub community!"]

    response = make_response({ "messages": messages }, 200)
    return response
