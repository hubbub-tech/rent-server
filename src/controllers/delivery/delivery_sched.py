from flask import Blueprint


bp = Blueprint("schedule", __name__)


@bp.post("/delivery/schedule")
@login_required
def schedule_delivery():

    try:
        order_ids = request.json["orderIds"]
        timeslots = request.json["timeslots"]
        to_address = request.json["toAddress"]
        from_address = request.json["fromAddress"]

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
        "to_addr_line_1": to_address["lineOne"],
        "to_addr_line_2": to_address["lineTwo"],
        "to_addr_country": to_address["country"],
        "to_addr_zip": to_address["zip"],
        "from_addr_line_1": from_address["lineOne"],
        "from_addr_line_2": from_address["lineTwo"],
        "from_addr_country": from_address["country"],
        "from_addr_zip": from_address["zip"],
    } # FILL WITH DATA FOR OBJ CREATION

    # NOTE: check to_addr and from_addr
    logistics = create_logistics(logistics_data)
    status = schedule_deliveries(logistics, order_ids, timeslots)

    messages = status["messages"]
    response = make_response({"messages": messages}, 200)
    return response
