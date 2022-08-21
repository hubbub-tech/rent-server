from flask import Blueprint


bp = Blueprint("account", __name__)


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
    form_check = validate_login(form_data)

    if form_check["is_valid"] == False:
        errors = form_check["messages"]
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
        new_address_data = {
            "line_1": request.json["newLineOne"],
            "line_2": request.json["newLineTwo"],
            "city": request.json["newCity"],
            "state": request.json["newState"],
            "country": request.json["newCountry"],
            "zip": request.json["newZip"]
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

    new_address = create_address(new_address_data)

    if form_check["is_valid"] == False:
        errors = form_check["messages"]
        response = make_response({"messages": errors}, 401)
        return response

    Users.set({"id": g.user_id}, {
        "address_line_1": new_address.line_1,
        "address_line_2": new_address.line_2,
        "address_country": new_address.country,
        "address_zip": new_address.zip,
    })

    messages = ["Successfully changed your address!"]
    response = make_response({"messages": messages}, 200)
    return response
    
