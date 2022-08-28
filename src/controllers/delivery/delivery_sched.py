from flask import Blueprint, make_response, request

from src.models import Orders

from src.utils import create_address
from src.utils import create_logistics
from src.utils import schedule_deliveries

bp = Blueprint("schedule", __name__)


@bp.post("/delivery/schedule")
@login_required
def schedule_delivery():

    try:
        order_ids = request.json["orderIds"]
        timeslots = request.json["timeslots"]
        to_address_data = request.json["toAddress"]
        from_address_data = request.json["fromAddress"]

        notes = request.json["notes"]
        referral = request.json["referral"]
        sender_id = request.json["senderId"]
        receiver_id = request.json["receiverId"]
    except KeyError:
        errors = ["Sorry, you didn't send anything in the form, try again."]
        response = make_response({ "messages": errors }, 406)
        return response
    except Exception as e:
        errors = ["Something went wrong. Please, try again."]
        # NOTE: Log error here.
        response = make_response({ "messages": errors }, 500)
        return response

    for order_id in order_ids:
        Orders.set({"id": order_id}, {"referral": referral})

    logistics_data = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "notes": notes,
        "to_addr_line_1": to_address_data["lineOne"],
        "to_addr_line_2": to_address_data["lineTwo"],
        "to_addr_country": to_address_data["country"],
        "to_addr_zip": to_address_data["zip"],
        "from_addr_line_1": from_address_data["lineOne"],
        "from_addr_line_2": from_address_data["lineTwo"],
        "from_addr_country": from_address_data["country"],
        "from_addr_zip": from_address_data["zip"],
    } # FILL WITH DATA FOR OBJ CREATION

    to_address = create_address(to_address_data)
    from_address = create_address(from_address_data)

    logistics = create_logistics(logistics_data)
    status = schedule_deliveries(logistics, order_ids, timeslots)

    if logistics.receiver_id == g.user_id:
        email_data = get_dropoff_request_email(logistics)
    elif logistics.sender_id == g.user_id
        email_data = get_pickup_request_email(logistics)
    else:
        pass # NOTE: when is this the case?

    send_async_email.apply_async(kwargs=email_data)
    
    messages = status.messages
    response = make_response({"messages": messages}, 200)
    return response
