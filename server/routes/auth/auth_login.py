from flask import Blueprint

bp = Blueprint('login', __name__)

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

@bp.post('/login/callback')
def login_callback():
    pass
