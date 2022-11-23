from datetime import datetime

from src.utils.settings import smtp_config

from src.models import Items
from src.models import Users
from src.models import Orders

from ._email_body import EmailBodyMessenger, EmailBodyFormatter


def get_item_expiration_email(item):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    lister = Users.get({ "id": item.lister_id })

    email_body_formatter.preview = f"Your listing of {item.name} has expired!"

    email_body_formatter.user = lister.name

    email_body_formatter.introduction = f"""
        This is a notice that your listing of the {item.name} has expired on the platform
        and is no longer visible to potential renters. This might be because:
        """

    email_body_formatter.content = f"""
        <p>* The entire rental duration you originally set has been booked,</p>
        <p>* The last allowable rental date that you set when listing has passed.</p>
        """

    email_body_formatter.conclusion = f"""
        You can contact us if you would like to extend the availability of your listing.
        Otherwise, this item will be archived {smtp_config.DEFAULT_RECEIVER}. Thanks!
        """

    body = email_body_formatter.build()

    email_body_messenger.subject = f"[Hubbub] Expired Listing: {item.name}"
    email_body_messenger.to = (lister.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body
    return email_body_messenger
