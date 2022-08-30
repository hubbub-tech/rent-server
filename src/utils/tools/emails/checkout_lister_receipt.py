from datetime import datetime

from src.utils.settings import SMTP

from src.models import Items
from src.models import Users

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter



def get_lister_receipt_email(order):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    item = Items.get({"id": order.item_id})
    renter = Users.get({"id": order.renter_id})
    lister = Users.get({"id": item.lister_id})

    email_body_formatter.preview = f"See your lister receipt for your item, ordered on {date.today().strftime('%B %-d, %Y')} - "

    email_body_formatter.user = lister.name

    email_body_formatter.introduction = f"""
        Thank you for listing on Hubbub! Your {item.name} has been rented
        by {renter.name}. The rental begins on {reservation.date_started.strftime('%B %-d, %Y')}
        and ends on {reservation.date_ended.strftime('%B %-d, %Y')}.
        """

    email_body_formatter.content = """
        <p>
        You can find next steps at this <a href='https://forms.hubbub.shop/'>form</a>.
        Please message us at hello@hubbub.shop for next steps.
        </p>
        """

    email_body_formatter.conclusion = ""

    body = email_body_formatter.build()

    email_data.subject = f"[Hubbub][Action Required] Lister Receipt for {item.name}"
    email_data.to = (lister.email, SMTP.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
