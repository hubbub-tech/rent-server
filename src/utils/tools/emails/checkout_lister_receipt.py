from datetime import datetime

from src.utils.settings import smtp_config

from src.models import Items
from src.models import Users

from ._email_body import EmailBodyMessenger, EmailBodyFormatter


def get_lister_receipt_email(order):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    item = Items.get({"id": order.item_id})
    renter = Users.get({"id": order.renter_id})
    lister = Users.get({"id": item.lister_id})

    dt_now = datetime.now()
    email_body_formatter.preview = f"See your lister receipt for your item, ordered on {dt_now.strftime('%B %-d, %Y')}"

    email_body_formatter.user = lister.name

    email_body_formatter.introduction = f"""
        Thank you for listing on Hubbub! Your {item.name} has been rented by {renter.name}.
        """

    email_body_formatter.content = f"""
        The rental begins on {order.res_dt_start.strftime('%B %-d, %Y')}
        and is currently set to end on {order.res_dt_end.strftime('%B %-d, %Y')}.
        """

    email_body_formatter.conclusion = f"If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}."

    body = email_body_formatter.build()

    email_body_messenger.subject = f"[Hubbub] Lister Receipt for {item.name}"
    email_body_messenger.to = (lister.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body
    return email_body_messenger
