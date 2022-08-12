from flask import Blueprint, make_response, request
from werkzeug.security import generate_password_hash

from src.models import Users
# from src.utils.??? import Config
# from src.utils.??? import gen_token, verify_token
# from src.utils.??? import get_password_reset_email
# from src.utils.??? import send_async_email

bp = Blueprint('manage', __name__)


@bp.post('pass/recover')
def pass_recover():

    try:
        email = request.json["email"].lower()
    except KeyError:
        errors = ["Sorry, you didn't send anything in the form, try again."]
        response = make_response({ "messages": errors }, 406)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    user = Users.unique({"email": email})

    if user:
        if user.session_key:
            recovery_token = generate_password_hash(user.session_key)
        else:
            recovery_token = gen_token()
            Users.set({"id": user.id}, {"session_key": recovery_token['unhashed']})

        # NOTE: async timer which invalidates token after X hours
        pass_reset_link = f"{Config.CORS_ALLOW_ORIGIN}/pass/reset?token={recovery_token['hashed']}"
        email_data = get_password_reset_email(user, reset_link)
        send_async_email.apply_async(kwargs=email_data)

    messages = ["If this email has an account, we have sent the recovery link there."]
    response = make_response({ "messages": messages }, 200)
    return response


@bp.post('/pass/reset')
def pass_reset():

    recovery_token = request.args.get("token", '')

    try:
        email = request.json["email"].lower()
        new_pass = request.json["newPassword"]
    except KeyError:
        errors = ["Did not receive your charges. Please, try again."]
        response = make_response({ "messages": errors }, 401)
        return response
    except Exception:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response


    user = Users.unique({ "email": email })
    if user:
        is_authenticated = verify_token(recovery_token, user.session_key)
        if is_authenticated:
            hashed_pass = generate_password_hash(new_pass)
            Users.set({"id": user.id}, {"password": hashed_pass})

            messages = ["You've successfully reset your password!"]
            response = make_response({ "messages": messages }, 200)
            return response

    errors = ["Reset attempt failed. Try again."]
    response = make_response({ "messages": errors}, 403)
    return response
