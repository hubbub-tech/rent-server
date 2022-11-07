from datetime import datetime

from src.utils.settings import smtp_config

from src.models import Items
from src.models import Users
from src.models import Orders
from src.models import Addresses

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_pickup_request_email(logistics):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    timeslots = logistics.get_timeslots()
    # NOTE: need printable timeslots

    dt_range_start_index = 0
    dt_range_end_index = 1

    date_pickup_str = timeslots[0][dt_range_start_index].strftime("%B %-d, %Y")
    email_body_formatter.preview = f"Coordinating pick-up for your recent order(s) for {date_pickup_str} - "

    renter = Users.get({"id": logistics.sender_id})
    email_body_formatter.user = renter.name

    email_body_formatter.introduction = """
        Thank you for transacting with Hubbub! We've received your completed
        pick-up logistics form. Your response has been recorded below for your
        record.
        """

    order_ids = logistics.get_order_ids()
    from_addr_pkeys = logistics.to_query_address("from")
    from_addr = Addresses.get(from_addr_pkeys)

    item_names = []
    for order_id in order_ids:
        order = Orders.get({"id": order_id})
        item = Items.get({"id": order.item_id})

        item_names.append(item.name)

    email_body_formatter.content = f"""
        <p>You ordered: {", ".join(item_names)}</p>
        <p>For pick-up on: {date_pickup_str}</p>
        <p>Meeting here: {from_addr.to_str()}</p>
        <p>Available at: {timeslots}</p>
        """

    email_body_formatter.conclusion = f"""
        We’ll respond confirming a precise pick-up time that fits the dates/times
        you indicated within 48 hours. If you have any questions, please contact
        us at {smtp_config.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_data.subject = "[Hubbub] Scheduling your Pick-up"
    email_data.to = (renter.email, smtp_config.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data


def get_pickup_error_email(logistics):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    renter = Users.get({"id": logistics.sender_id})

    email_body_formatter.preview = f"There was a problem scheduling timeslots for user_id:{renter.id} - "

    email_body_formatter.user = "Team Hubbub"

    email_body_formatter.introduction = f"Please, manually confirm pickup timeslots with user, {renter.name} ({renter.id})."
    email_body_formatter.content = "<p>Timeslot attachment failed, likely do to input error.</p>"
    email_body_formatter.conclusion = ""

    body = email_body_formatter.build()

    email_data.subject = "[Internal Error] Failed Silently while Recording Pickup Timeslots"
    email_data.to = (smtp_config.DEFAULT_RECEIVER,)
    email_data.body = body
    return email_data
