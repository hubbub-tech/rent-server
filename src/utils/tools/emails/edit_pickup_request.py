from datetime import datetime

from src.utils.settings import SMTP

from src.models import Items
from src.models import Users
from src.models import Orders

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_edit_pickup_request_email(order, address_formatted, date_pickup, timeslots):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    item = Items.get({ "id": order.item_id })

    timeslots_printables = []
    for timeslot in timeslots:
        time_start_str, time_end_str = timeslot
        timeslots_printables.append(f"{time_start_str}-{time_end_str}")

    timeslots_str = ", ".join(timeslots_printables)

    curr_date_pickup_str = order.ext_dt_end.strftime("%B %-d, %Y")
    new_date_pickup_str = date_pickup.strftime("%B %-d, %Y")
    email_body_formatter.preview = f"Updating pick-up for your order ending on {curr_date_pickup_str} - "

    renter = Users.get({ "id": order.renter_id })
    email_body_formatter.user = renter.name

    email_body_formatter.introduction = """
        We've received your request for a new pick-up date and time. Your response has
        been recorded below for your record.
        """

    email_body_formatter.content = f"""
        <p>You ordered: {item.name}</p>
        <p>Requested pick-up date: {new_date_pickup_str}</p>
        <p>Requested pick-up time: {timeslots_str}</p>
        """

    email_body_formatter.conclusion = f"""
        We'll see if we can update the pick-up time. If possible, we'll email you
        with next steps if we can make it happen. If you have any questions, please contact
        us at {SMTP.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_data.subject = "[Hubbub] Updating your Pick-up"
    email_data.to = (renter.email, SMTP.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
