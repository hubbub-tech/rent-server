from flask import Blueprint, make_response, request, g

from src.models import Users
from src.models import Orders
from src.models import Items
from src.models import Addresses
from src.models import Logistics

from src.utils import create_address
from src.utils import create_logistics
from src.utils import get_nearest_storage
from src.utils import attach_timeslots

from src.utils import login_required
from src.utils import send_async_email
from src.utils import get_dropoff_request_email
from src.utils import get_dropoff_error_email
from src.utils import get_pickup_request_email
from src.utils import get_pickup_error_email

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_5_SERVER_ERROR
)

bp = Blueprint("schedule", __name__)


@bp.post("/dropoff/schedule")
@login_required
def schedule_dropoff():

    try:
        order_ids = request.json["orderIds"]
        timeslots = request.json["timeslots"]

        to_address_data = {
            "lat": request.json["address"]["lat"],
            "lng": request.json["address"]["lng"],
            "formatted": request.json["address"]["formatted"]
        }

        notes = request.json.get("notes")
        referral = request.json.get("referral")
    except KeyError:
        error = "Sorry, you didn't send anything in the form, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        errors = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    to_address = create_address(to_address_data)
    to_address.set_as_destination()

    for order_id in order_ids:
        order = Orders.get({ "id": order_id })
        item = Items.get({ "id": order.item_id })
        from_address = Addresses.get(item.to_query_address())
        from_address.set_as_origin()

        logistics = Logistics.unique({
            "sender_id": item.lister_id,
            "receiver_id": g.user_id,
            "to_addr_lat": to_address.lat,
            "to_addr_lng": to_address.lng,
            "from_addr_lat": from_address.lat,
            "from_addr_lng": from_address.lng,
            "is_canceled": False,
            "dt_sent": None
        })

        if logistics is None:
            logistics_data = {
                "sender_id": item.lister_id,
                "receiver_id": g.user_id,
                "notes": notes,
                "to_addr_lat": to_address.lat,
                "to_addr_lng": to_address.lng,
                "from_addr_lat": from_address.lat,
                "from_addr_lng": from_address.lng,
            }

            logistics = create_logistics(logistics_data)
            date_event = order.res_dt_start.date()

            status = attach_timeslots(order_ids, logistics, timeslots, date_event)

            if status.is_successful:
                try:
                    email_data = get_dropoff_request_email(logistics)
                except:
                    email_data = get_dropoff_error_email(logistics)
            else:
                email_data = get_dropoff_error_email(logistics)
            send_async_email.apply_async(kwargs=email_data.to_dict())

        attached_order_ids = logistics.get_order_ids()
        if order.id not in attached_order_ids:
            logistics.add_order(order.id)

    Users.set({ "id": g.user_id }, {
        "address_lat": to_address.lat,
        "address_lng": to_address.lng
    })

    response = make_response({ "message": "Thanks for scheduling!" }, CODE_2_OK)
    return response


@bp.post("/pickup/schedule")
@login_required
def schedule_pickup():

    try:
        order_ids = request.json["orderIds"]
        timeslots = request.json["timeslots"]

        from_address_data = {
            "lat": request.json["address"]["lat"],
            "lng": request.json["address"]["lng"],
            "formatted": request.json["address"]["formatted"]
        }

        notes = request.json.get("notes")
    except KeyError:
        error = "Sorry, you didn't send anything in the form, try again."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Something went wrong. Please, try again."
        # NOTE: Log error here.
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    from_address = create_address(from_address_data)
    from_addr_coords = (from_address.lat, from_address.lng)

    storage_lat, storage_lng = get_nearest_storage(from_addr_coords)
    to_storage_address = create_address({ "lat": storage_lat, "lng": storage_lng })

    to_storage_address.set_as_destination()
    from_address.set_as_origin()

    for order_id in order_ids:
        order = Orders.get({ "id": order_id })
        item = Items.get({ "id": order.item_id })

        logistics = Logistics.unique({
            "sender_id": g.user_id,
            "receiver_id": item.lister_id,
            "to_addr_lat": to_storage_address.lat,
            "to_addr_lng": to_storage_address.lng,
            "from_addr_lat": from_address.lat,
            "from_addr_lng": from_address.lng,
            "is_canceled": False,
            "dt_sent": None
        })

        if logistics is None:
            logistics_data = {
                "sender_id": g.user_id,
                "receiver_id": item.lister_id,
                "notes": notes,
                "to_addr_lat": to_storage_address.lat,
                "to_addr_lng": to_storage_address.lng,
                "from_addr_lat": from_address.lat,
                "from_addr_lng": from_address.lng,
            }

            logistics = create_logistics(logistics_data)
            date_event = order.ext_dt_end.date()

            status = attach_timeslots(order_ids, logistics, timeslots, date_event)

            if status.is_successful:
                try:
                    email_data = get_pickup_request_email(logistics)
                except:
                    email_data = get_pickup_error_email(logistics)
            else:
                email_data = get_pickup_error_email(logistics)
            send_async_email.apply_async(kwargs=email_data.to_dict())

        attached_order_ids = logistics.get_order_ids()
        if order.id not in attached_order_ids:
            logistics.add_order(order.id)

    response = make_response({ "message": "Thanks for scheduling!" }, CODE_2_OK)
    return response
