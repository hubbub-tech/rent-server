from flask import Blueprint

from src.models import Users

from src.utils import validate_login
from src.utils import login_required
from src.utils import create_address

bp = Blueprint("edit", __name__)


#edit personal account
@bp.post("/account/password/edit")
@login_required
def edit_password():

    try:
        new_password = request.json["newPassword"]
        curr_password = request.json["currPassword"]
    except KeyError:
        errors = ["Sorry, did not receive your password updates. Please, try again."]
        response = make_response({"messages": errors}, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    user = Users.get({"id": g.user_id})

    form_data = { "email": user.email, "password": curr_password }
    status = validate_login(form_data)

    if status.is_successful == False:
        errors = status.messages
        response = make_response({"messages": errors}, 401)
        return response

    hashed_pass = generate_password_hash(new_password)
    Users.set({"id": g.user_id}, {"password": hashed_pass})

    messages = ["Successfully changed password!"]
    response = make_response({"messages": messages}, 200)
    return response


#edit personal account
@bp.post("/account/address/edit")
@login_required
def edit_address():

    try:
        formatted_address = request.json["formatted"]

        new_address_data = {
            "lat": request.json["lat"],
            "lng": request.json["lng"]
        }
    except KeyError:
        errors = ["Sorry, did not receive your new address updates. Please, try again."]
        response = make_response({"messages": errors}, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    # NOTE: parse address before creation...
    new_address = create_address(new_address_data)

    Users.set({"id": g.user_id}, {
        "address_lat": new_address.lat,
        "address_lng": new_address.lng
    })

    messages = ["Successfully changed your address!"]
    response = make_response({"messages": messages}, 200)
    return response
