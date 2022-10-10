from datetime import datetime

from src.utils.settings import smtp_config

from src.models import Items
from src.models import Users
from src.models import Orders

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_edit_dropoff_request_email(order, address_formatted, date_dropoff, timeslots):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    item = Items.get({ "id": order.item_id })

    timeslots_printables = []
    for timeslot in timeslots:
        time_start_str, time_end_str = timeslot
        timeslots_printables.append(f"{time_start_str}-{time_end_str}")

    timeslots_str = ", ".join(timeslots_printables)

    curr_date_dropoff_str = order.res_dt_start.strftime("%B %-d, %Y")
    new_date_dropoff_str = date_dropoff.strftime("%B %-d, %Y")
    email_body_formatter.preview = f"Updating drop-off for your order starting on {curr_date_dropoff_str} - "

    renter = Users.get({ "id": order.renter_id })
    email_body_formatter.user = renter.name

    email_body_formatter.introduction = """
        We've received your request for a new drop-off date and time. Your response has
        been recorded below for your record.
        """

    email_body_formatter.content = f"""
        <p>You ordered: {item.name}</p>
        <p>Requested drop-off date: {new_date_dropoff_str}</p>
        <p>Requested drop-off time: {timeslots_str}</p>
        """

    email_body_formatter.conclusion = f"""
        We'll see if we can update the drop-off time. If possible, we'll email you
        with next steps if we can make it happen. If you have any questions, please contact
        us at {smtp_config.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_data.subject = "[Hubbub] Updating your Drop-off"
    email_data.to = (renter.email, smtp_config.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
