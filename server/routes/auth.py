from datetime import datetime, timedelta
from flask import Blueprint, flash, redirect, get_flashed_messages, session, g, request
from werkzeug.security import check_password_hash, generate_password_hash

from blubber_orm import Users

from server.tools.settings import login_user, create_auth_token, verify_auth_token, Config

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
            "email": data["user"]["email"],
            "password": data["user"]["password"]
        }
        form_check = validate_login(form_data)
        if form_check["is_valid"]:
            user, = Users.filter({"email": form_data["email"]})
            login_response = login_user(user)
            if login_response["is_valid"]:
                auth = create_auth_token(user)
                flashes.append(login_response["message"])
                return {
                    "errors": errors,
                    "flashes": flashes,
                    "user_id": user.id,
                    "cart_size": user.cart.size(),
                    "auth": auth,
                }, 201
            else:
                errors.append(login_response["message"])
                flashes.append("Houston, we have a problem...")
        else:
            errors.append(form_check["message"])
            flashes.append("Houston, we have a problem...")
    else:
        flashes.append("Nothing was entered! We need input to log you in.")
    return {"errors": errors, "flashes": flashes}, 406 #NOTE: no data

@bp.post('/register')
def register():
    flashes = []
    errors = []
    data = request.json
    if data:
        first_name = data["user"]["firstName"]
        last_name = data["user"]["lastName"]
        unhashed_pass = data["user"]["password"]
        hashed_pass = generate_password_hash(unhashed_pass)
        form_data = {
            "user": {
                "name": f"{first_name},{last_name}",
                "email": data["user"]["email"],
                "payment": data["user"]["payment"],
                "password": hashed_pass,
                "address_num": data["address"]["num"],
                "address_street": data["address"]["street"],
                "address_apt": data["address"]["apt"],
                "address_zip": data["address"]["zip"]
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
                "zip": data["address"]["zip"]
            }
        }
        form_check = validate_registration(form_data["user"])
        if form_check["is_valid"]:
            new_user = create_user(form_data)
            email_data = get_welcome_email(new_user)
            send_async_email.apply_async(kwargs=email_data)
            flashes.append(form_check["message"])
            return {"flashes": flashes}, 201
        else:
            errors.append(form_check["message"])
            flashes.append("Uh oh...")
    else:
        errors.append("No information to create an account! Try again.")
        flashes.append("Uh oh...")
    return {"flashes": flashes, "errors": errors}, 406

@bp.get("/logout")
def logout():
    session.clear()
    return {"is_logged_in": False}

#TODO: rebuild account recovery
@bp.post('/password/recovery')
def password_recovery():
    flashes = []
    data = request.json
    if data:
        _user = Users.filter({"email": data["email"]})
        if _user:
            user, = _user
            if user.session is None:
                token = create_auth_token(user)
            else:
                token = generate_password_hash(user.session)
            reset_link = f"{Config.CORS_ALLOW_ORIGIN}/password/reset/token={token}"
            email_data = get_password_reset_email(user, reset_link)
            send_async_email.apply_async(kwargs=email_data)
        flashes.append("If this email has an account, we have sent the recovery link there.")
        return {"flashes": flashes}, 201
    else:
        flashes.append("Sorry, you didn't send anything in the form, try again.")
        return {"flashes": flashes}, 406

@bp.post('/password/reset/token=<token>')
def password_reset(token):
    flashes = []
    data = request.json
    if data:
        _user = Users.filter({"email": data["email"]})
        if _user:
            user, = _user
            is_authenticated = verify_auth_token(token, user.id)
            if is_authenticated:
                hashed_password = generate_password_hash(data["newPassword"])
                Users.set(user.id, {"password": hashed_password})
                flashes.append("You've successfully reset your password!")
                return {"flashes": flashes}, 201
            else:
                flashes.append("Reset attempt failed. Try again.")
                return {"flashes": flashes}, 406
        else:
            flashes.append("Reset attempt failed. Try again.")
            return {"flashes": flashes}, 406
    else:
        flashes.append("Sorry, you didn't send anything in the form, try again.")
        return {"flashes": flashes}, 406
