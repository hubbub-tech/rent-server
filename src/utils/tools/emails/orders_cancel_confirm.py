from datetime import datetime

from src.models import Items
from src.models import Users

from src.utils.settings import smtp_config

from ._email_body import EmailBodyMessenger, EmailBodyFormatter


def get_cancellation_email(order):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    item = Items.get({"id": order.item_id})
    user = Users.get({"id": order.renter_id})

    email_body_formatter.preview = f"This is to confirm that your order for {item.name} has been cancelled"

    email_body_formatter.user = user.name

    email_body_formatter.introduction = f"""
        This email is to confirm that your request to cancel your recent rental of {item.name}, has been received.
        """

    email_body_formatter.content = "This rental is now cancelled and you don't need to do anything else."

    email_body_formatter.conclusion = f"If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}."

    body = email_body_formatter.build()

    email_body_messenger.subject = f"[Hubbub] Rental Canceled: {item.name}"
    email_body_messenger.to = (user.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body
    return email_body_messenger
