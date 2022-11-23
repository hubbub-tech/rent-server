from datetime import datetime

from src.utils.settings import smtp_config

from src.models import Users
from src.models import Items
from src.models import Calendars
from src.models import Orders
from src.models import Addresses

from ._email_body import EmailBodyMessenger, EmailBodyFormatter

def get_new_listing_email(item):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    dt_now = datetime.now()
    email_body_formatter.preview = f"This is to confirm that your item was listed on {dt_now.strftime('%B %-d, %Y')}"

    lister = Users.get({"id": item.lister_id})
    email_body_formatter.user = lister.name

    item_calendar = Calendars.get({"id": item.id})
    email_body_formatter.introduction = f"""
        Thank you for listing on Hubbub. Your item, the {item.name}, has been published to
        Hubbub.
        """

    email_body_formatter.content = f"""
        The rental is available starting {item_calendar.dt_started.strftime('%B %-d, %Y')}
        and ending {item_calendar.dt_ended.strftime('%B %-d, %Y')}.
        """

    email_body_formatter.conclusion = f"""
        If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_body_messenger.subject = f"[Hubbub] Listing Confirmation: {item.name}"
    email_body_messenger.to = (lister.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body
    return email_body_messenger
