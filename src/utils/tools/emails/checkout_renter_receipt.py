from datetime import datetime

from src.utils.settings import smtp_config
from src.utils.settings import CLIENT_DOMAIN

from src.models import Items
from src.models import Users
from src.models import Reservations

from ._email_table import EmailTable, EmailTableRow
from ._email_body import EmailBodyMessenger, EmailBodyFormatter

def get_renter_receipt_email(orders):

    email_body_messenger = EmailBodyMessenger()
    email_body_formatter = EmailBodyFormatter()

    renter = Users.get({"id": orders[0].renter_id})

    dt_now = datetime.now()
    email_body_formatter.preview = f"See your rental receipt for your order placed on {dt_now.strftime('%B %-d, %Y')}"
    email_body_formatter.user = renter.name

    email_body_formatter.introduction = """
        Thanks for ordering from Hubbub! Your payment has been processed,
        and your receipt has been recorded for you below.
        """

    scheduling_link = email_body_formatter.make_link(CLIENT_DOMAIN + "/rentals/schedule#dropoffs", "here")
    email_body_formatter.content = f"If you have not yet, please complete your dropoff and pickup request forms {scheduling_link}."

    table_rows = []
    total_charge = 0
    total_deposit = 0
    total_tax = 0
    for order in orders:
        item = Items.get({"id": order.item_id})

        res_pkeys = order.to_query_reservation()
        res = Reservations.get(res_pkeys)

        row_data = {
            "Item": item.name,
            "Start date": res.dt_started.strftime("%b %-d, %Y"),
            "End date": res.dt_ended.strftime("%b %-d, %Y"),
            "Cost": f"${res.est_charge:.2f}",
            "Deposit": f"${res.est_deposit:.2f}",
            "Tax": f"${res.est_tax:.2f}",
        }
        table_row = EmailTableRow(row_data)
        table_rows.append(table_row)

        total_charge += res.est_charge
        total_deposit += res.est_deposit
        total_tax += res.est_tax

    row_data = {
        "Item": "Total",
        "Start date": "-",
        "End date": "-",
        "Cost": f"${total_charge:.2f}",
        "Deposit": f"${total_deposit:.2f}",
        "Tax": f"${total_tax:.2f}"
    }
    table_row = EmailTableRow(row_data)
    table_rows.append(table_row)

    email_table = EmailTable(table_rows, title=f"Order Receipt: {dt_now.strftime('%B %-d, %Y')}")
    email_body_formatter.optional = email_table.to_html()

    email_body_formatter.conclusion = f"""
        <p>
            The Safety Deposit for each rental will be returned to you at the end of
            that rental assuming the item is clean and not damaged beyond reasonable wear and tear.
            You can go to your account page to see a record of your upcoming and
            current rentals.
        </p>
        <p>
            If you have any questions, please contact us at {smtp_config.DEFAULT_RECEIVER}. Thanks!
        </p>
        """

    body = email_body_formatter.build()

    email_body_messenger.subject = "[Hubbub] Order Receipt"
    email_body_messenger.to = (renter.email, smtp_config.DEFAULT_RECEIVER)
    email_body_messenger.body = body
    return email_body_messenger
