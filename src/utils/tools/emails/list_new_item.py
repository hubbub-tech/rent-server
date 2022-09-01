from datetime import datetime

from src.utils.settings import SMTP

from src.models import Items
from src.models import Calendars
from src.models import Orders
from src.models import Addresses

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_new_listing_email(item):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    email_body_formatter.preview = f"This is to confirm that your item was listed on {datetime.now().strftime('%B %-d, %Y')} - "

    lister = Users.get({"id": item.lister_id})
    email_body_formatter.user = lister.name

    item_calendar = Calendars.get({"id": item.id})
    email_body_formatter.introduction = f"""
        Thank you for listing on Hubbub. Your item, the {item.name}, has been published to
        Hubbub. The rental is available starting {item_calendar.dt_started.strftime('%B %-d, %Y')}
        and ending {item_calendar.dt_ended.strftime('%B %-d, %Y')}.
        """

    email_body_formatter.content = ""

    email_body_formatter.conclusion = f"""
        No need to list your item on other platforms! If it is listed somewhere
        else, take it down and leave the magic to us B-). If you have any
        questions, please contact us at {SMTP.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_data.subject = f"[Hubbub] Listing Confirmation for your {item.name}"
    email_data.to = (lister.email, SMTP.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
