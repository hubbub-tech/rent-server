from datetime import datetime, date, timedelta
from blubber_orm import Items, Orders, Users, Pickups, Dropoffs

def get_dropoff_email(dropoff):
    dropoff_logistics = dropoff.logistics
    renter = Users.get(dropoff_logistics.renter_id)
    orders = Orders.by_dropoff(dropoff)
    item_names = [Items.get(order.item_id).name for order in orders]
    timeslots = dropoff_logistics.timeslots
    dropoff_date = dropoff.dropoff_date.strftime("%B %-d, %Y")

    frame_data = {}
    frame_data["preview"] = f"Coordinating drop-off for your recent order(s) for {dropoff_date} - "
    frame_data["user"] = renter.name
    frame_data["introduction"] = """
        Thank you for transacting with Hubbub! We've received your completed
        drop-off logistics form. Your response has been recorded below for your
        record.
        """
    logistics = get_logistics_table(dropoff_date, item_names, timeslots)
    frame_data["content"] = f"""
        {logistics}
        <p>Referral Name: {dropoff_logistics.referral}</p>
        <p>Drop-off Address: {dropoff_logistics.address.display()}</p>
        <p>Your Delivery Notes: {dropoff_logistics.notes}</p>
        """
    frame_data["conclusion"] = """
        We’ll respond confirming a precise drop off time that fits the dates/times
        you indicated within 48 hours. If you have any questions, please contact
        us at hubbubcu@gmail.com.
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Scheduling your Dropoff"
    email_data["to"] = (renter.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "DROP-LOGISTICS"
    return email_data

def get_pickup_email(pickup):
    pickup_logistics = pickup.logistics
    renter = Users.get(pickup_logistics.renter_id)
    orders = Orders.by_pickup(pickup)
    item_names = [Items.get(order.item_id).name for order in orders]
    timeslots = pickup_logistics.timeslots
    pickup_date = pickup.pickup_date.strftime("%B %-d, %Y")

    frame_data = {}
    frame_data["preview"] = f"Coordinating pick-up for your order return on {pickup_date} - "
    frame_data["user"] = renter.name
    frame_data["introduction"] = f"""
        We hope you’re doing well! We’re reaching out to you regarding the upcoming
        end of your rental on {pickup_date}. We've received your completed pick-up
        logistics form. Your response has been recorded below for your record.
        """
    logistics = get_logistics_table(pickup_date, item_names, timeslots)
    frame_data["content"] = f"""
        {logistics}
        <p>Pick-up Address: {pickup_logistics.address.display()}</p>
        <p>Your Delivery Notes: {pickup_logistics.notes}</p>
        """
    frame_data["conclusion"] = """
        We’ll respond confirming a precise pick up time that fits the dates/times
        you indicated within 48 hours. If you have any questions, please contact
        us at hubbubcu@gmail.com.
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Scheduling your Pickup"
    email_data["to"] = (renter.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "PICK-LOGISTICS"
    return email_data

def get_renter_receipt_email(transactions):
    renter = transactions[0]["renter"]
    frame_data = {}
    frame_data["preview"] = f"See your rental receipt for your order placed on {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = renter.name
    frame_data["introduction"] = """
        Thank you for transacting with Hubbub! Your receipt has been recorded below for your
        record.
        """
    frame_data["content"] = get_receipt_table(transactions)
    frame_data["conclusion"] = f"""
            The Safety Deposit for each rental will be returned to you at the end of
            that rental assuming the item is not damaged beyond reasonable wear and tear.
            You can go to your account page to see a record of your upcoming and
            current rentals.
        </p>
        <p>
            Hubbub will handle all payments and delivery logistics
            between users and charge in-person at drop-off via Venmo at @{renter.payment}
            or card.
        </p>
        <p>
            Finally, if you have completed the Dropoff Form,
            you should have received another email titled, "[Hubbub] Scheduling your Dropoff".
            If you haven't completed it, please do so ASAP
            (<a href="https://www.hubbub.shop/accounts/u/orders">here</a>)!
        </p>
        <p>
            If you have any questions, please contact us at hubbubcu@gmail.com. Thanks!
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Order Receipt"
    email_data["to"] = (renter.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "RENTER-RECEIPT"
    return email_data

def get_lister_receipt_email(transaction):
    item = transaction["item"]
    renter = transaction["renter"]
    reservation = transaction["reservation"]
    lister = Users.get(item.lister_id)

    frame_data = {}
    frame_data["preview"] = f"See your rental receipt for your order on {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = lister.name
    frame_data["introduction"] = f"""
        Thank you for transacting with Hubbub! Your {item.name} has been rented
        by {renter.name}. The rental begins on {reservation.date_started.strftime('%B %-d, %Y')}
        and ends on {reservation.date_ended.strftime('%B %-d, %Y')}.
        """
    frame_data["content"] = f"""
        <p>
        Please respond with your availability on {reservation.date_started.strftime('%B %-d, %Y')}
        for item pick-up. If this date doesn't work, you can request pick-up on the backup date
        {(reservation.date_started - timedelta(days=2)).strftime("%m/%d/%Y")}. If you cannot be
        present for our pick-up team to get the item, you can CC a proxy on this email.
        </p>
        """
    frame_data["conclusion"] = """
        Hubbub will handle all payments and delivery logistics between users.
        If you have any questions, please contact us at hubbubcu@gmail.com. Thanks!
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub Lister][Action Required] Receipt for {item.name}"
    email_data["to"] = (lister.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "RENT-LISTER-RECEIPT"
    return email_data

def get_welcome_email(user):
    frame_data = {}
    frame_data["preview"] = f"Welcome to Hubbub! We're excited to have you join on {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = user.name
    frame_data["introduction"] = """
            Welcome to Hubbub! We are so excited to have you join our movement for
            flexible ownership! Hubbub is passionate about getting the maximum use
            out of our items and keeping the maximum number of items out of landfill.
        </p>
        <p>
            Our other driving mission is to make any item accessible to anyone while
            empowering communities. We are a brand that hopefully makes you feel
            good about shopping!
        """
    frame_data["content"] = """
        <p>
            As a member, you can rent items from other members. Get started renting
            <a href="https://www.hubbub.shop/inventory">here</a>. We have more features
            in the works, so stay tuned!
        </p>
        """
        #and you can learn more about listing <a href="https://www.hubbub.shop/how-to-list">here</a>
    frame_data["conclusion"] = """
        You can also go to your account portal on the website to view items you
        are renting and items you have listed. If you have any questions, please
        contact us at hubbubcu@gmail.com.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Welcome, {user.name}!"
    email_data["to"] = (user.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "AUTH-WELCOME"
    return email_data

def get_new_listing_email(item):
    lister = Users.get(item.lister_id)
    frame_data = {}
    frame_data["preview"] = f"This is to confirm that your item was listed on {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = lister.name
    frame_data["introduction"] = f"""
        Thank you for listing with Hubbub. Your item, the {item.name}, has been published to
        Hubbub. The rental is available starting {item.calendar.date_started.strftime('%B %-d, %Y')}
        and ending {item.calendar.date_ended.strftime('%B %-d, %Y')}.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = """
        No need to list your item on other platforms! If it is listed somewhere
        else, take it down and leave the magic to us B-). If you have any
        questions, please contact us at hubbubcu@gmail.com.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Listing Confirmation for your {item.name}"
    email_data["to"] = (lister.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "LIST-CONFIRMATION"
    return email_data

def get_extension_email(order, ext_reservation):
    item = Items.get(order.item_id)
    user = Users.get(order.renter_id)
    frame_data = {}
    frame_data["preview"] = f"This is to confirm that your rental has been extended - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        This email is to confirm that your rental on {item.name}, has been extended.
        This rental will now end on {ext_reservation.date_ended.strftime('%B %-d, %Y')}.
        """
    frame_data["content"] = f"""
        <p>
            Extension Cost: {ext_reservation.print_charge()}. Extension Deposit:
            {ext_reservation.print_deposit()}. Sales tax: {ext_reservation.print_tax()}.
        </p>
        <p>
            <bold>Total</bold>: {ext_reservation.print_total()}
        </p>
        """
    frame_data["conclusion"] = """
        If you had any previous plans for pickup, they have been cancelled. You can
        schedule a new end of rental pickup (<a href="https://www.hubbub.shop/accounts/u/orders">here</a>)!
        If you have any questions, please contact us at hubbubcu@gmail.com.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Your Rental on {item.name} has been Extended!"
    email_data["to"] = (user.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "EXTENSION-CONFIRMATION"
    return email_data

def get_early_return_email(order, early_reservation):
    item = Items.get(order.item_id)
    user = Users.get(order.renter_id)
    frame_data = {}
    frame_data["preview"] = f"This is to confirm that your early return request has been received - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        This email is to confirm that your request for an early return on {item.name}, has been received.
        This rental will now end on {early_reservation.date_ended.strftime('%B %-d, %Y')}.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = """
        You can schedule a new end of rental pickup
        (<a href="https://www.hubbub.shop/accounts/u/orders">here</a>)!
        If you have any questions, please contact us at hubbubcu@gmail.com.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Your Early Return Request on {item.name}"
    email_data["to"] = (user.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "EARLY-CONFIRMATION"
    return email_data

def get_cancellation_email(order):
    item = Items.get(order.item_id)
    user = Users.get(order.renter_id)
    frame_data = {}
    frame_data["preview"] = f"This is to confirm that your order for {item.name} has been cancelled - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        This email is to confirm that your request to cancel your recent rental of {item.name}, has been received.
        This rental is now cancelled and you don't need to do anything else.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = """
        If you have any questions, please contact us at hubbubcu@gmail.com.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Your Order Cancellation on {item.name}"
    email_data["to"] = (user.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "CANCEL-CONFIRMATION"
    return email_data

def get_password_reset_email(user, link):
    frame_data = {}
    frame_data["preview"] = f"Someone requested a password recovery on {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        Recently, you placed a request to recover your password. If you requested
        this, follow the link <a href="{link}">here</a> to recover your password.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = """
        If you did not request this service, please report to admins at hubbubcu@gmail.com. Thank you!
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Recover Your Password"
    email_data["to"] = (user.email, "hubbubcu@gmail.com")
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "PASS-RECOVERY"
    return email_data

#EMAIL HELPERS---------------------------------------

def email_builder(frame_data):
    frame = """
        <!doctype html>
        <html lang="en">
          <head>
            <style>
              .preheader {{
                color: transparent;
                display: none;
                height: 0;
                max-height: 0;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                mso-hide: all;
                visibility: hidden;
                width: 0;
                }}
              td, th {{
                border: 1px solid #ffffff;
                text-align: left;
                padding: 8px;
                }}
              div.content {{
                  width: 600px;
                  margin: 0em 5em 5em 5em;
                  padding: 2em;
                  background-color: #fdfdff;
                  border-radius: 0em 0em 0.5em 0.5em;
                  box-shadow: 0px 3px 7px 2px rgba(0,0,0,0.02);
                  }}
            </style>
          </head>
          <body style="background-color: #f0f0f2; font-family: arial, sans-serif; margin: 0; padding: 0;">
            <span class="preheader">{preview}</span>
            <div class="content">

              <!-- START CENTERED WHITE CONTAINER -->
              <table role="presentation" class="main">

                <!-- START MAIN CONTENT AREA -->
                <tr>
                  <p>Hi {user},</p>
                  <p>{introduction}</p>
                </tr>
                <tr>
                  {content}
                </tr>
                <tr>
                    <br>
                  <p>{conclusion}</p>
                  <p>Sincerely,</p>
                  <p>  Team Hubbub</p>
                </tr>
              </table>
              <!-- END CENTERED WHITE CONTAINER -->

              <!-- START FOOTER-->
              <div class="footer">
                <small>
                  <span>Hubbub HQ, 523 W. 160th St., Apt 5A, New York, NY 10032</span>
                  <br> Continue shopping at <a href="https://www.hubbub.shop/inventory">Hubbub Shop</a>.
                <small>
              </div>
              <!--END FOOTER -->

            </div>
          </body>
        </html>
        """.format(
                preview=frame_data["preview"],
                user=frame_data["user"],
                introduction=frame_data["introduction"],
                content=frame_data["content"],
                conclusion=frame_data["conclusion"]
                )
    return frame

def get_logistics_table(date_str, item_names, timeslots):
    item_names_str = ", ".join(item_names)
    timeslots_str = ", ".join(timeslots)
    logistics_table = f"""
        <table>
            <tr>
                <th>Date</th>
                <th>Items</th>
                <th>Availability</th>
            </tr>
            <tr>
                <td>{date_str}</td>
                <td>{item_names_str}</td>
                <td>{timeslots_str}</td>
            </tr>
        </table>
            """
    return logistics_table

def get_receipt_table(transactions):
    total_cost = 0.0
    total_deposit = 0.0
    total_tax = 0.0
    receipt = """
        <table>
            <tr>
                <th>Item</th>
                <th>Start Rental</th>
                <th>End Rental</th>
                <th>Cost</th>
                <th>Safety Deposit</th>
                <th>Tax</th>
            </tr>
        """
    for transaction in transactions:
        item = transaction["item"]
        order = transaction["order"]
        reservation = transaction["reservation"]
        row = f"""
            <tr>
                <td>{item.name}</td>
                <td>{reservation.date_started.strftime('%B %-d, %Y')}</td>
                <td>{reservation.date_ended.strftime('%B %-d, %Y')}</td>
                <td>{reservation.print_charge()}</td>
                <td>{reservation.print_deposit()}</td>
                <td>{reservation.print_tax()}</td>
            </tr>
            """
        receipt += row
        total_cost += reservation._charge
        total_deposit += reservation._deposit
        total_tax += reservation._tax
    totals = f"""
        <tr>
            <td><strong>Totals</strong></td>
            <td></td>
            <td></td>
            <td><strong>${round(total_cost, 2)}</strong></td>
            <td><strong>${round(total_deposit, 2)}</strong></td>
            <td><strong>${round(total_tax, 2)}</strong></td>
        </tr>
        """
    receipt += totals + "</table>"
    return receipt
