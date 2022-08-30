from datetime import datetime

from src.utils.settings import SMTP

from src.models import Items
from src.models import Users

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter


def get_early_return_email(txn, early_reservation):
    """Must remain compatible with extensions and orders."""

    assert type(txn) in [Orders, Extensions], "Invalid transaction type."

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    email_body_formatter.preview = "This is to confirm that your early return request has been received - "

    item = Items.get({"id": txn.item_id})
    user = Users.get({"id": txn.renter_id})

    email_body_formatter.user = user.name

    email_body_formatter.introduction = f"""
        This email is to confirm that your request for an early return on {item.name}, has been received.
        This rental will now end on {early_reservation.date_ended.strftime('%B %-d, %Y')}.
        """

    email_body_formatter.content = ""

    pickup_request_link = "https://www.hubbub.shop/accounts/u/orders"
    email_body_formatter.conclusion = f"""
        You can schedule a new end of rental pickup (<a href='{pickup_request_link}'>here</a>)!
        If you have any questions, please contact us at {SMTP.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()
    email_data.subject = f"[Hubbub] Your Early Return Request on {item.name}"
    email_data.to = (user.email, SG.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
