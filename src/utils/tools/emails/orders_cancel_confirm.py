from datetime import datetime

from src.models import Items
from src.models import Users

from src.utils.settings import SMTP

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter


def get_cancellation_email(order):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    item = Items.get({"id": order.item_id})
    user = Users.get({"id": order.renter_id})

    email_body_formatter.preview = f"This is to confirm that your order for {item.name} has been cancelled - "

    email_body_formatter.user = user.name

    email_body_formatter.introduction = f"""
        This email is to confirm that your request to cancel your recent rental of {item.name}, has been received.
        This rental is now cancelled and you don't need to do anything else.
        """

    email_body_formatter.content = ""

    email_body_formatter.conclusion = f"If you have any questions, please contact us at {SMTP.DEFAULT_RECEIVER}."

    body = email_body_formatter.build()

    email_data.subject = f"[Hubbub] Your Order Cancellation on {item.name}"
    email_data.to = (user.email, SMTP.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
