import requests
from flask import Blueprint

from src.utils.settings import FlaskConfig


bp = Blueprint("newsletter", __name__)


@bp.post("/newsletter/join")
def newsletter_form_submit():
    flashes = []
    data = request.json
    recaptcha_data = {
        "secret": FlaskConfig.ReCAPTCHA_SERVER_API_KEY,
        "response": data.get('token')
    }
    captcha_response = requests.post(ReCAPTCHA_VERIFY_URL, data=recaptcha_data)
    captcha_response.raise_for_status()
    captcha = captcha_response.json()
    if data and captcha["success"]:
        name = data.get("name")
        email = data.get("email")
        if email:
            email_data = get_newsletter_welcome({"name": name, "email": email})
            send_async_email.apply_async(kwargs=email_data)
            flashes.append("Woo, you've been added to our newsletter!")
            return {"flashes": flashes}, 200
    return {"flashes": ["There was a problem adding you to our email list. try again."]}, 406
