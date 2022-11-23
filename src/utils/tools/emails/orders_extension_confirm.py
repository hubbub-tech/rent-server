from datetime import datetime

from src.utils.settings import smtp_config
from src.utils.settings import CLIENT_DOMAIN

from src.models import Items
from src.models import Users
from src.models import Reservations

from ._email_body import EmailBodyMessenger, EmailBodyFormatter

def get_extension_receipt_email(extension):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    item = Items.get({"id": extension.item_id})
    user = Users.get({"id": extension.renter_id})

    res_pkeys = extension.to_query_reservation()
    res = Reservations.get(res_pkeys)

    email_body_formatter.user = user.name

    email_body_formatter.preview = "This is to confirm that your rental has been extended"

    email_body_formatter.introduction = f"""
        This email is to confirm that your rental on {item.name}, has been extended.
        This rental will now end on {extension.res_dt_end.strftime('%B %-d, %Y')}.
        """

    link_to_html = email_body_formatter.make_link(CLIENT_DOMAIN + '/rentals/schedule#pickups', 'here')
    email_body_formatter.content = f"""
        If you had any previous plans for pickup, they have been cancelled. You can
        schedule a new end of rental pickup {link_to_html}!
        """

    email_body_formatter.conclusion = f"""
        If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}.
        """

    email_body_formatter.optional = f"""
        <p>Extension Receipt</p>
        <ul>
            <li>Extension Cost: ${res.est_charge:.2f}</li>
            <li>Extension Deposit: ${res.est_deposit:.2f}</li>
            <li>Sales Tax: ${res.est_tax:.2f}</li>
            <li><bold>Total: ${res.total():.2f}</bold></li>
        </ul>
        """

    body = email_body_formatter.build()

    email_body_messenger.subject = f"[Hubbub] Rental Extension: {item.name} to {extension.res_dt_end.strftime('%B %-d, %Y')}"
    email_body_messenger.to = (user.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body
    return email_body_messenger
