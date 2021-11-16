import requests

from datetime import datetime, timedelta
from flask import Blueprint, g, request, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from blubber_orm import Users
from server.tools.settings import login_user
from server.tools.settings import ReCAPTCHA_VERIFY_URL, COOKIE_KEY_USER, COOKIE_KEY_SESSION, COOKIE_KEY_CART
from server.tools.settings import create_auth_token, verify_auth_token
from server.tools.settings import Config

from server.tools.build import create_user
from server.tools.build import validate_registration, validate_login
from server.tools.build import get_welcome_email, get_password_reset_email, send_async_email

bp = Blueprint('auth', __name__)

@bp.post('/login')
def login():
    flashes = []
    errors = []

    data = request.json
    if data:
        form_data = {
            "email": data["user"]["email"].lower(),
            "password": data["user"]["password"]
        }
        form_check = validate_login(form_data)
        if form_check["is_valid"]:
            user = Users.unique({"email": form_data["email"]})
            login_response = login_user(user)
            if login_response["is_valid"]:
                session = create_auth_token(user)
                flashes.append(login_response["message"])
                data = {
                    "flashes": flashes,
                    COOKIE_KEY_USER: f'{user.id}',
                    COOKIE_KEY_CART: f'{user.cart.size()}',
                    COOKIE_KEY_SESSION: session
                }
                response = make_response(data, 200)
                return response
            else:
                errors.append(login_response["message"])
        else:
            errors.append(form_check["message"])
        flashes.append("Houston, we have a problem...")
    else:
        flashes.append("Nothing was entered! We need input to log you in.")
    data = {"errors": errors, "flashes": flashes}
    response = make_response(data, 401)
    return response

@bp.post('/register')
def register():
    flashes = []
    errors = []
    data = request.json
    recaptcha_data = {
        "secret": Config.ReCAPTCHA_SERVER_API_KEY,
        "response": data.get('token')
    }
    captcha_response = requests.post(ReCAPTCHA_VERIFY_URL, data=recaptcha_data)
    captcha_response.raise_for_status()
    captcha = captcha_response.json()
    if data and captcha["success"]:
        first_name = data["user"]["firstName"]
        last_name = data["user"]["lastName"]
        unhashed_pass = data["user"]["password"]
        hashed_pass = generate_password_hash(unhashed_pass)
        form_data = {
            "user": {
                "name": f"{first_name},{last_name}",
                "email": data["user"]["email"].lower(),
                "payment": data["user"]["payment"],
                "password": hashed_pass,
                "address_num": data["address"]["num"],
                "address_street": data["address"]["street"],
                "address_apt": data["address"]["apt"],
                "address_zip": data["address"]["zip_code"]
            },
            "profile": {
                "phone": data["profile"]["phone"],
                "bio": "I love Hubbub!",
                "id": None
            },
            "cart": {
                "total": 0.0,
                "total_deposit": 0.0,
                "total_tax": 0.0,
                "id": None
            },
            "address": {
                "num": data["address"]["num"],
                "street": data["address"]["street"],
                "apt": data["address"]["apt"],
                "city": data["address"]["city"],
                "state": data["address"]["state"],
                "zip": data["address"]["zip_code"]
            }
        }
        form_check = validate_registration(form_data["user"])
        if form_check["is_valid"]:
            new_user = create_user(form_data)
            email_data = get_welcome_email(new_user)
            send_async_email.apply_async(kwargs=email_data)
            flashes.append(form_check["message"])
            data = {"flashes": flashes}
            response = make_response(data, 200)
            return response
        else:
            errors.append(form_check["message"])
    else:
        errors.append("Sorry! Try again.")
    flashes.append("Uh oh...")
    data = {"flashes": flashes, "errors": errors}
    response = make_response(data, 406)
    return response

@bp.post('/password/recovery')
def password_recovery():
    flashes = []
    data = request.json
    if data:
        user = Users.unique({"email": data["email"].lower()})
        if user:
            if user.session is None: token = create_auth_token(user)
            else: token = generate_password_hash(user.session)

            reset_link = f"{Config.CORS_ALLOW_ORIGIN}/password/reset/token={token}"
            email_data = get_password_reset_email(user, reset_link)
            send_async_email.apply_async(kwargs=email_data)
        flashes.append("If this email has an account, we have sent the recovery link there.")
        data = {"flashes": flashes}
        response = make_response(data, 200)
        return response
    else:
        flashes.append("Sorry, you didn't send anything in the form, try again.")
        data = {"flashes": flashes}
        response = make_response(data, 406)
        return response

@bp.post('/password/reset/token=<token>')
def password_reset(token):
    flashes = []
    data = request.json
    if data:
        user = Users.unique({"email": data["email"].lower()})
        if user:
            is_authenticated = verify_auth_token(token, user.id)
            if is_authenticated:
                hashed_pass = generate_password_hash(data["newPassword"])
                Users.set({"id": user.id}, {"password": hashed_pass})

                flashes.append("You've successfully reset your password!")
                data = {"flashes": flashes}
                response = make_response(data, 200)
                return response
    flashes.append("Reset attempt failed. Try again.")
    data = {"flashes": flashes}
    response = make_response(data, 200)
    return response
