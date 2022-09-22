from flask import Blueprint, make_response, request, g

from src.models import Orders

from src.utils import create_address
from src.utils import create_logistics
from src.utils import schedule_deliveries

from src.utils import login_required
from src.utils import send_async_email
from src.utils import get_dropoff_request_email
from src.utils import get_pickup_request_email

bp = Blueprint("schedule", __name__)


@bp.post("/delivery/schedule")
@login_required
def schedule_delivery():

    print("address: ", request.json["address"])
    print("timeslots: ", request.json["timeslots"])
    try:
        orders = request.json["orders"]
        timeslots = request.json["timeslots"]
        to_address_data = {
            "line_1": request.json["toAddress"]["lineOne"],
            "line_2": request.json["toAddress"]["lineTwo"],
            "city": request.json["toAddress"]["city"],
            "state": request.json["toAddress"]["state"],
            "country": "USA", # request.json["toAddress"]["country"],
            "zip": request.json["toAddress"]["zip"],
        }
        from_address_data = {
            "line_1": request.json["fromAddress"]["lineOne"],
            "line_2": request.json["fromAddress"]["lineTwo"],
            "city": request.json["fromAddress"]["city"],
            "state": request.json["fromAddress"]["state"],
            "country": "USA", # request.json["fromAddress"]["country"],
            "zip": request.json["fromAddress"]["zip"],
        }

        notes = request.json["notes"]
        referral = request.json.get("referral")
        sender_id = request.json.get("senderId", g.user_id)
        receiver_id = request.json.get("receiverId", g.user_id)
    except KeyError:
        errors = ["Sorry, you didn't send anything in the form, try again."]
        response = make_response({ "messages": errors }, 406)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    order_ids = []
    for order in orders:
        order_ids.append(order["id"])

        if referral:
            Orders.set({"id": order["id"]}, {"referral": referral})

    logistics_data = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "notes": notes,
        "to_addr_line_1": to_address_data["line_1"],
        "to_addr_line_2": to_address_data["line_2"],
        "to_addr_country": "USA", # to_address_data["country"],
        "to_addr_zip": to_address_data["zip"],
        "from_addr_line_1": from_address_data["line_1"],
        "from_addr_line_2": from_address_data["line_2"],
        "from_addr_country": "USA", # from_address_data["country"],
        "from_addr_zip": from_address_data["zip"],
    } # FILL WITH DATA FOR OBJ CREATION

    to_address = create_address(to_address_data)
    from_address = create_address(from_address_data)

    to_address.set_as_destination()
    from_address.set_as_origin()

    logistics = create_logistics(logistics_data)
    status = schedule_deliveries(logistics, order_ids, timeslots)

    if logistics.receiver_id == g.user_id:
        email_data = get_dropoff_request_email(logistics)
        send_async_email.apply_async(kwargs=email_data.to_dict())

    if logistics.sender_id == g.user_id:
        email_data = get_pickup_request_email(logistics)
        send_async_email.apply_async(kwargs=email_data.to_dict())

    messages = status.messages
    response = make_response({"messages": messages}, 200)
    return response
