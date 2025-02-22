from datetime import datetime

from src.utils.settings import smtp_config
from src.utils.settings import CLIENT_DOMAIN

from src.models import Items
from src.models import Users
from src.models import Orders
from src.models import Extensions

from ._email_body import EmailBodyMessenger, EmailBodyFormatter


def get_early_return_email(txn, early_reservation):
    """Must remain compatible with extensions and orders."""

    assert type(txn) in [Orders, Extensions], "Invalid transaction type."

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    email_body_formatter.preview = "This is to confirm that your early return request has been received - "

    item = Items.get({"id": txn.item_id})
    user = Users.get({"id": txn.renter_id})

    email_body_formatter.user = user.name

    email_body_formatter.introduction = f"""
        This email is to confirm that your request for an early return on {item.name}, has been received.
        This rental will now end on {early_reservation.dt_ended.strftime('%B %-d, %Y')}.
        """

    email_body_formatter.content = ""

    link_to_html = email_body_formatter.make_link(CLIENT_DOMAIN + '/rentals/schedule#pickups', 'here')
    email_body_formatter.conclusion = f"""
        You can schedule a new end of rental pickup {link_to_html}!
        If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()
    email_body_messenger.subject = f"[Hubbub] Early Return Request: {item.name}"
    email_body_messenger.to = (user.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body
    return email_body_messenger
