from datetime import datetime

from src.utils import SMTP

from src.models import Items
from src.models import Users
from src.models import Reservations

from ._email_data import EmailData
from ._email_body_formatter import EmailBodyFormatter

def get_renter_receipt_email(orders):

    email_data = EmailData()
    email_body_formatter = EmailBodyFormatter()

    renter = Users.get({"id": orders[0].renter_id})

    email_body_formatter.preview = f"See your rental receipt for your order placed on {datetime.now().strftime('%B %-d, %Y')} - "
    email_body_formatter.user = renter.name

    email_body_formatter.introduction = "Thanks ordering from Hubbub! Here's your receipt!"

    table_data = []
    total_charge = 0
    total_deposit = 0
    total_tax = 0
    for order in orders:
        item = Items.get({"id": order.item_id})

        res_pkeys = order.to_query_reservation()
        res = Reservations.get(res_pkeys)

        row_data = {
            "item_name": item.name,
            "date_started": res.dt_started.strftime("%B %-d, %Y"),
            "date_ended": res.dt_ended.strftime("%B %-d, %Y"),
            "charge": f"${res.est_charge:.2f}",
            "deposit": f"${res.est_deposit:.2f}",
            "tax": f"${res.est_tax:.2f}",
        }
        table_data.append(row_data)

        total_charge += res.est_charge
        total_deposit += res.est_deposit
        total_tax += res.est_tax

    promos = order.get_promos()
    if promos: pass # NOTE: build promos into cost table.

    row_data = {
        "item_name": "TOTAL"
        "date_started": "",
        "date_ended": "",
        "charge": f"${total_charge:.2f}",
        "deposit": f"${total_deposit:.2f}",
        "tax": f"${total_tax:.2f}",
    }
    table_data.append(row_data)

    # NOTE: should use pandas to be concise
    email_body_formatter.content = email_body_formatter.generate_table(
        columns=["Item", "Start", "End", "Cost", "Deposit", "Tax"],
        data=table_data
    )

    schedule_dropoff_link = "https://www.hubbub.shop/accounts/u/orders"
    email_body_formatter.conclusion = f"""
            The Safety Deposit for each rental will be returned to you at the end of
            that rental assuming the item is not damaged beyond reasonable wear and tear.
            You can go to your account page to see a record of your upcoming and
            current rentals.
        </p>
        <p>
            We handle payment in-person and accept Venmo, card, or cash.
        </p>
        <p>
            Finally, if you have completed the Dropoff Form,
            you should have received another email titled, "[Hubbub] Scheduling your Dropoff".
            If you haven't completed it, please do so ASAP
            (<a href='{schedule_dropoff_link}'>here</a>)!
        </p>
        <p>
            If you have any questions, please contact us at {SMTP.DEFAULT_RECEIVER}. Thanks!
        """

    body = email_body_formatter.build()

    email_data.subject = "[Hubbub] Order Receipt"
    email_data.to = (renter.email, SMTP.DEFAULT_RECEIVER)
    email_data.body = body
    return email_data
