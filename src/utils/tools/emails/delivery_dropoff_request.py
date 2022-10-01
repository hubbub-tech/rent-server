from datetime import datetime

from src.utils.settings import SMTP

from src.models import Items
from src.models import Users
from src.models import Orders
from src.models import Addresses

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_dropoff_request_email(logistics):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    timeslots = logistics.get_timeslots()

    dt_range_start_index = 0
    dt_range_end_index = 1

    timeslots_printables = []
    for timeslot in timeslots:
        time_start_str = timeslot[dt_range_start_index].strftime("%H:%M")
        time_end_str = timeslot[dt_range_end_index].strftime("%H:%M")

        timeslots_printables.append(f"{time_start_str}-{time_end_str}")

    timeslots_str = ", ".join(timeslots_printables)

    dt_range_start_index = 0
    dt_range_end_index = 1

    dropoff_date_str = timeslots[0][dt_range_start_index].strftime("%B %-d, %Y")
    email_body_formatter.preview = f"Coordinating drop-off for your recent order(s) for {dropoff_date_str} - "

    renter = Users.get({"id": logistics.receiver_id})
    email_body_formatter.user = renter.name

    email_body_formatter.introduction = """
        Thank you for transacting with Hubbub! We've received your completed
        drop-off logistics form. Your response has been recorded below for your
        record.
        """

    order_ids = logistics.get_order_ids()
    to_addr_pkeys = logistics.to_query_address("to")
    to_addr = Addresses.get(to_addr_pkeys)

    item_names = []
    for order_id in order_ids:
        order = Orders.get({"id": order_id})
        item = Items.get({"id": order.item_id})

        item_names.append(item.name)

    email_body_formatter.content = f"""
        <p>You ordered: {", ".join(item_names)}</p>
        <p>For drop-off on: {dropoff_date_str}</p>
        <p>Meeting here: {to_addr.to_str()}</p>
        <p>Available at: {timeslots_str}</p>
        """

    email_body_formatter.conclusion = f"""
        We’ll respond confirming a precise drop off time that fits the dates/times
        you indicated within 48 hours. If you have any questions, please contact
        us at {SMTP.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_data.subject = "[Hubbub] Scheduling your Drop-off"
    email_data.to = (renter.email, SMTP.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data


def get_dropoff_error_email(logistics):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    renter = Users.get({"id": logistics.receiver_id})

    email_body_formatter.preview = f"There was a problem scheduling timeslots for user_id:{renter.id} - "

    email_body_formatter.user = "Team Hubbub"

    email_body_formatter.introduction = f"Please, manually confirm dropoff timeslots with user, {renter.name} ({renter.id})."
    email_body_formatter.content = "<p>Timeslot attachment failed, likely do to input error.</p>"
    email_body_formatter.conclusion = ""

    body = email_body_formatter.build()

    email_data.subject = "[Internal Error] Failed Silently while Recording Dropoff Timeslots"
    email_data.to = (SMTP.DEFAULT_RECEIVER,)
    email_data.body = body
    return email_data
