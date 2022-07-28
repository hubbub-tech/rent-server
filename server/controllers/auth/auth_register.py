from flask import Blueprint

bp = Blueprint('manage', __name__)


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
                "address_line_1": data["address"]["line_1"],
                "address_line_2": data["address"]["line_2"],
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
                "line_1": data["address"]["line_1"],
                "line_2": data["address"]["line_2"],
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
