import requests
from flask import Blueprint, make_response, request

from src.utils.settings import CaptchaConfig

from src.utils import get_newsletter_welcome
from src.utils import upload_email_data

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_4_TIMEOUT,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("newsletter", __name__)


@bp.post("/newsletter/join")
def newsletter_sign_up():

    try:
        name = request.json["name"]
        email = request.json["email"]
        token = request.json["token"]
    except KeyError as e:
        error = "Sorry, seems like there was a problem receiving your sign up request, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Seems like something is wrong."
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    recaptcha_data = {
        "secret": CaptchaConfig.ReCAPTCHA_SERVER_APIKEY,
        "response": token
    }
    captcha_response = requests.post(CaptchaConfig.ReCAPTCHA_VERIFY_URL, data=recaptcha_data)
    captcha_response.raise_for_status()
    captcha = captcha_response.json()
    
    if data and captcha["success"]:
        email_data = get_newsletter_welcome({"name": name, "email": email})
        upload_email_data(email_data, email_type="newsletter_notice")

        data = {"message": "Thanks for joining our newsletter!" }
        response = make_response(data, CODE_2_OK)
        return response
    else:
        error = "Sorry, try again recaptcha timed out."
        response = make_response({ "message": error }, CODE_4_TIMEOUT)
        return response
