from flask import Blueprint, make_response, request

bp = Blueprint("list", __name__)


@bp.post('/list')
@login_required
def list_item():

    try:
        item_data = {
            "name": request.json["item"]["name"],
            "retail_price": request.json["item"]["retailPrice"],
            "description": request.json["item"]["description"],
            "weight": request.json["item"].get("weight"),
            "weight_unit": request.json["item"].get("weightUnit"),
            "dim_height": request.json["item"].get("height"),
            "dim_length": request.json["item"].get("length"),
            "dim_width": request.json["item"].get("width"),
            "manufacturer_id": request.json["item"].get("manufacturerId"),
            "lister_id": g.user_id,
            "address_line_1": None,
            "address_line_2": None,
            "address_country": None,
            "address_zip": None
        }

        address_data = {
            "line_1": request.json["address"]["lineOne"],
            "line_2": request.json["address"]["lineTwo"],
            "city": request.json["address"]["city"],
            "state": request.json["address"]["state"],
            "country": request.json["address"]["country"],
            "zip": request.json["address"]["zip"]
        }

        calendar_data = {
            "dt_started": request.json["calendar"]["dtStarted"],
            "dt_ended": request.json["calendar"]["dtEnded"]
        }

        tags = ["all"] + request.json.get("tags").split()
        is_from_lister_address = strtobool(request.json["isDefaultAddress"])

    except KeyError:
        errors = ["Missing data to complete your listing! Please, try again."]
        response = make_response({ "messages": errors }, 401)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    form_check = validate_calendar(
        dt_lbound=calendar_data["dt_started"],
        dt_ubound=calendar_data["dt_ended"]
    )

    if not form_check["is_valid"]:
        errors = form_check["messages"]
        response = make_response({ "messages": errors }, 403)
        return response

    address = create_address(address_data)
    new_item = create_item(item_data, calandar_data)
    email_data = get_successful_listing_email(new_item)
    send_async_email.apply_async(kwargs=email_data)

    messages = ["Thanks for listing on Hubbub!"]

    response = make_response({ "messages": messages }, 200)
    return response
