from datetime import datetime

from src.utils.settings import smtp_config

from src.models import Items
from src.models import Users
from src.models import Reservations

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_extension_receipt_email(extension):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    email_body_formatter.preview = "This is to confirm that your rental has been extended - "

    item = Items.get({"id": extension.item_id})
    user = Users.get({"id": extension.renter_id})

    email_body_formatter.user = user.name

    email_body_formatter.introduction = f"""
        This email is to confirm that your rental on {item.name}, has been extended.
        This rental will now end on {extension.res_dt_end.strftime('%B %-d, %Y')}.
        """

    res_pkeys = extension.to_query_reservation()
    res = Reservations.get(res_pkeys)

    email_body_formatter.content = f"""
        <p>
            Extension Cost: ${res.est_charge:.2f}.
            Extension Deposit: ${res.est_deposit:.2f}.
            Sales tax: ${res.est_tax:.2f}.
        </p>
        <p>
            <bold>Total: ${res.total():.2f}</bold>
        </p>
        """

    pickup_request_link = "https://www.hubbub.shop/accounts/u/orders"
    email_body_formatter.conclusion = f"""
        If you had any previous plans for pickup, they have been cancelled. You can
        schedule a new end of rental pickup (<a href='{pickup_request_link}'>here</a>)!
        If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}.
        """

    body = email_body_formatter.build()

    email_data.subject = f"[Hubbub] Your Rental on {item.name} has been Extended!"
    email_data.to = (user.email, smtp_config.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
