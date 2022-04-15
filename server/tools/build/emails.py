from datetime import datetime, date, timedelta
from blubber_orm import Items, Orders, Users, Pickups, Dropoffs

from server.tools.settings import SG, GRACE_LIMIT, PENALTY_LIMIT

def get_late_warning(order):
    item = Items.get({ "id": order.item_id })
    renter = Users.get({ "id": order.renter_id })

    assert order.dt_pickup_completed is None # FLAG
    overdue_days = (date.today() - order.ext_date_end).days

    assert overdue_days > 0

    frame_data = {}
    frame_data["preview"] = f"The {item.name} rented by {renter.name} is overdue - "
    frame_data["user"] = renter.name
    frame_data["introduction"] = f"""
        We noticed that your rental of our {item.name} ended {overdue_days} days
        ago and you have not returned it.
        """

    if overdue_days < GRACE_LIMIT:
        response = f"""
            Your overdraft is within our grace period of {GRACE_LIMIT}. If you schedule
            a time for us to pick up in the next {(GRACE_LIMIT - overdue_days) * 24},
            we will wave any penalties as long as the item is not booked by another user for
            that period*.
            """
    elif overdue_days < PENALTY_LIMIT:
        response = f"""
            Your overdraft has begun to incur penalties equivalent to ${round(item.price / 9, 2)}
            per overdue day. You currently owe ${round(overdue_days * item.price / 9, 2)}.
            Please reply to this email to coordinate pickup with us immediately.
            """
    elif not renter.is_blocked:
        Users.set({"id": renter.id}, {"is_blocked": True})
        response = "You have been permanently banded from Hubbub."

    frame_data["content"] = f"<p>{response}</p>"
    frame_data["conclusion"] = """
        Please contact us if you have any questions or believe that there is
        some mistake in this judgment.
        """
    email_data = {}
    email_data["subject"] = f"[Action] Overdue Rental of {item.name}"
    email_data["to"] = (renter.email,)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "WARNING-OVERDUE"

def get_newsletter_welcome(newsletter_data):
    frame_data = {}
    frame_data["preview"] = f"New newsletter signup '{newsletter_data['email']}' {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = "Hubbub Team"
    frame_data["introduction"] = f"New signup in town! Check it below."
    frame_data["content"] = f"""
        <p>New Name: <bold>{newsletter_data['name']}</bold></p>
        <p>New Email: <bold>{newsletter_data['email']}</bold></p>
        """
    frame_data["conclusion"] = "Thanks!"
    email_data = {}
    email_data["subject"] = f"[Internal] New Newsletter Signup"
    email_data["to"] = (SG.DEFAULT_RECEIVER,)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "WELCOME-TO-NEWSLETTER"
    return email_data

def get_dropoff_email(dropoff):
    dropoff_logistics = dropoff.logistics
    renter = Users.get({"id": dropoff_logistics.renter_id})
    orders = Orders.by_dropoff(dropoff)

    item_names = []
    for order in orders:
        item = Items.get({"id": order.item_id})
        item_names.append(item.name)

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
    frame_data["conclusion"] = f"""
        We’ll respond confirming a precise drop off time that fits the dates/times
        you indicated within 48 hours. If you have any questions, please contact
        us at {SG.DEFAULT_RECEIVER}.
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Scheduling your Dropoff"
    email_data["to"] = (renter.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "DROP-LOGISTICS"
    return email_data

def get_pickup_email(pickup):
    pickup_logistics = pickup.logistics
    renter = Users.get({"id": pickup_logistics.renter_id})
    orders = Orders.by_pickup(pickup)

    item_names = []
    for order in orders:
        item = Items.get({"id": order.item_id})
        item_names.append(item.name)

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
    frame_data["conclusion"] = f"""
        We’ll respond confirming a precise pick up time that fits the dates/times
        you indicated within 48 hours. If you have any questions, please contact
        us at {SG.DEFAULT_RECEIVER}.
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Scheduling your Pickup"
    email_data["to"] = (renter.email, SG.DEFAULT_RECEIVER)
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
            If you have any questions, please contact us at {SG.DEFAULT_RECEIVER}. Thanks!
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Order Receipt"
    email_data["to"] = (renter.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "RENTER-RECEIPT"
    return email_data

def get_lister_receipt_email(transaction):
    item = transaction["item"]
    renter = transaction["renter"]
    reservation = transaction["reservation"]
    lister = Users.get({"id": item.lister_id})

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
    frame_data["conclusion"] = f"""
        Hubbub will handle all payments and delivery logistics between users.
        If you have any questions, please contact us at {SG.DEFAULT_RECEIVER}. Thanks!
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub Lister][Action Required] Receipt for {item.name}"
    email_data["to"] = (lister.email, SG.DEFAULT_RECEIVER)
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
            As a member, you can rent any item on the platform. Get started renting
            <a href="https://www.hubbub.shop/inventory">here</a>. We have more features
            in the works, so stay tuned!
        </p>
        """
        #and you can learn more about listing <a href="https://www.hubbub.shop/how-to-list">here</a>
    frame_data["conclusion"] = f"""
        You can also go to your account portal on the website to view items you
        are renting with other features coming soon! If you have any questions, please
        contact us at {SG.DEFAULT_RECEIVER}.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Welcome, {user.name}!"
    email_data["to"] = (user.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "AUTH-WELCOME"
    return email_data

def get_new_listing_email(item):
    lister = Users.get({"id": item.lister_id})
    frame_data = {}
    frame_data["preview"] = f"This is to confirm that your item was listed on {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = lister.name
    frame_data["introduction"] = f"""
        Thank you for listing with Hubbub. Your item, the {item.name}, has been published to
        Hubbub. The rental is available starting {item.calendar.date_started.strftime('%B %-d, %Y')}
        and ending {item.calendar.date_ended.strftime('%B %-d, %Y')}.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = f"""
        No need to list your item on other platforms! If it is listed somewhere
        else, take it down and leave the magic to us B-). If you have any
        questions, please contact us at {SG.DEFAULT_RECEIVER}.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Listing Confirmation for your {item.name}"
    email_data["to"] = (lister.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "LIST-CONFIRMATION"
    return email_data

def get_extension_email(order, ext_reservation):
    item = Items.get({"id": order.item_id})
    user = Users.get({"id": order.renter_id})
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
    frame_data["conclusion"] = f"""
        If you had any previous plans for pickup, they have been cancelled. You can
        schedule a new end of rental pickup (<a href="https://www.hubbub.shop/accounts/u/orders">here</a>)!
        If you have any questions, please contact us at {SG.DEFAULT_RECEIVER}.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Your Rental on {item.name} has been Extended!"
    email_data["to"] = (user.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "EXTENSION-CONFIRMATION"
    return email_data

def get_early_return_email(order, early_reservation):
    item = Items.get({"id": order.item_id})
    user = Users.get({"id": order.renter_id})
    frame_data = {}
    frame_data["preview"] = f"This is to confirm that your early return request has been received - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        This email is to confirm that your request for an early return on {item.name}, has been received.
        This rental will now end on {early_reservation.date_ended.strftime('%B %-d, %Y')}.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = f"""
        You can schedule a new end of rental pickup
        (<a href="https://www.hubbub.shop/accounts/u/orders">here</a>)!
        If you have any questions, please contact us at {SG.DEFAULT_RECEIVER}.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Your Early Return Request on {item.name}"
    email_data["to"] = (user.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "EARLY-CONFIRMATION"
    return email_data

def get_cancellation_email(order):
    item = Items.get({"id": order.item_id})
    user = Users.get({"id": order.renter_id})
    frame_data = {}
    frame_data["preview"] = f"This is to confirm that your order for {item.name} has been cancelled - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        This email is to confirm that your request to cancel your recent rental of {item.name}, has been received.
        This rental is now cancelled and you don't need to do anything else.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = f"""
        If you have any questions, please contact us at {SG.DEFAULT_RECEIVER}.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Your Order Cancellation on {item.name}"
    email_data["to"] = (user.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "CANCEL-CONFIRMATION"
    return email_data

def get_password_reset_email(user, link):
    frame_data = {}
    frame_data["preview"] = f"Someone requested a password recovery on {date.today().strftime('%B %-d, %Y')} - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        Recently, you placed a request to recover your password. If you requested
        this, follow the link <a href='{link}'>here</a> to recover your password.
        """
    frame_data["content"] = ""
    frame_data["conclusion"] = f"""
        If you did not request this service, please report to admins at {SG.DEFAULT_RECEIVER}. Thank you!
        """
    email_data = {}
    email_data["subject"] = "[Hubbub] Recover Your Password"
    email_data["to"] = (user.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "PASS-RECOVERY"
    return email_data


def get_we_miss_you_email(user):
    discount = "20%"

    frame_data = {}
    frame_data["preview"] = f"Hubbub hasn't been the same since you left :'( - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        It's been so long since we've seen you! We know life get's busy, and
        we want to be there for you.
        """
    frame_data["content"] = f"""
        <p>
            We want to offer you {discount} off the next item you order. We're so
            happy that you gave us a chance by signing up, and we want to follow
            through on the amazing experience that we promised to you.
        </p>
        """
    frame_data["conclusion"] = """
        Hopefully this gift will help you and save some time and money. We would also
        love to receive your feedback! Tell us how we can improve Hubbub through this
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSe5gWyZ6XtGYhMk8n_pPbxVtt8_YhEh139BTRydbF4XCkVHJg/viewform">anonymous feedback form</a>.
        Check out the <a href='https://www.hubbub.shop/inventory'>website</a> for the latest listings,
        and as always, you can reach out with questions :)
        """
    email_data = {}
    email_data['subject'] = f"Hey {user.name}, we miss you @Hubbub!"
    email_data['to'] = (user.email, SG.DEFAULT_RECEIVER)
    email_data['body'] = email_builder(frame_data)
    return email_data

def get_referral_offer_email(user):
    amount = "$10"

    frame_data = {}
    frame_data["preview"] = f"Refer a friend to rent and get {amount} from Hubbub! - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        You've been with Hubbub for a while now, and we want to reward you for that!
        For anyone you refer to Hubbub who places a new rental order, we want to send
        you {amount} over Venmo (CashApp, Zelle, etc)!
        """
    frame_data["content"] = f"""
        <p>
            Just ask them to note YOU, {user.name}, as their referral when they
            schedule the dropoff of their rental. After that, you can expect to
            receive your {amount} reward through your payment app of choice!
        </p>
        """
    frame_data["conclusion"] = """
        We’ll be keeping this offer valid through the end of June 2021 to hopefully
        help you and your friends save time and money! In the meantime, check out the
        <a href='https://www.hubbub.shop/inventory'>website</a> for the latest listings!
        And as always, you can reach out with questions :)
        """
    email_data = {}
    email_data['subject'] = f"Hey {user.name}, get {amount} from Hubbub :)!"
    email_data['to'] = (user.email, SG.DEFAULT_RECEIVER)
    email_data['body'] = email_builder(frame_data)
    return email_data


def get_shopping_cart_reminder(user):
    frame_data = {}
    frame_data["preview"] = f"Remember the items in your Hubbub cart! - "
    frame_data["user"] = user.name
    frame_data["introduction"] = f"""
        We noticed that you still had something in your Hubbub cart! We've linked
        them below for you :). With everything else going on in the world,
        you shouldn't have to worry about how you’ll get the items you need.
        """
    frame_data["content"] = get_cart_items(user)
    frame_data["conclusion"] = """
        Finish checking out the items in your <a href='https://www.hubbub.shop/checkout'>cart</a>
        before someone else gets to them! Once you complete your order through Hubbub,
        we make the rest simple for you by delivering directly to your door! Then when
        you're done, you can either extend the rental or we can pick it up without a hassle.
        Thanks for renting through us, and don't hesitate to reach out with any questions :)
        """
    email_data = {}
    email_data['subject'] = 'Looks like you were checking out some items on Hubbub ;)?'
    email_data['to'] = (user.email, SG.DEFAULT_RECEIVER)
    email_data['body'] = email_builder(frame_data)
    return email_data

def get_pickup_schedule_reminder(renter, orders):
    frame_data = {}
    frame_data["preview"] = f"Remember to schedule a pickup for your rental(s) - "
    frame_data["user"] = renter.name
    frame_data["introduction"] = f"""
        Hey there! It seems like you still have {len(orders)} rental(s) without
        pickups scheduled. Your rental(s) have been listed below:
        """
    frame_data["content"] = get_active_orders_table(orders)
    frame_data["conclusion"] = f"""
        You can schedule your pickup at <a href="https://www.hubbub.shop/accounts/u/orders">My Rentals</a>.
        Alternatively, you can extend your rental for any of these items by following the same link.
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Remember to Schedule your Rental Pickup!"
    email_data["to"] = (renter.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "REMINDER-PICKUP"
    return email_data

def get_task_time_email(task, chosen_time):

    renter = Users.get({"id": task.renter_id})
    courier = Users.get({"id": task.logistics.courier_id})

    frame_data = {}
    frame_data["preview"] = f"Your {task.type} time has been set for {chosen_time.strftime('%I:%M:00 %p')} - "
    frame_data["user"] = renter.name
    frame_data["introduction"] = f"""
        Thanks for submitting your availability! We have scheduled a specific time
        for your {task.type}. See the information below for details.
        """
    frame_data["content"] = get_task_update_table(task, chosen_time)

    total_tax = 0
    total_deposit = 0
    total_charge = 0
    for order in task.orders:
        reservation = order.reservation
        total_tax += reservation._tax
        total_deposit += reservation._deposit
        total_charge += reservation._charge
    if task.type == "pickup":
        charge = "" #"Your deposit will be returned at pickup."
        clause = """
            Please make sure each item is in a clean and usable state upon pickup,
            charges may be applied otherwise.
            """
    else:
        total = round(total_tax + total_deposit + total_charge, 2)
        charge = f"Total due at dropoff: ${total}"
        clause = ""
    frame_data["conclusion"] = f"""
            {charge}
        </p>
        <p>
            We will be sending you a text from our Hubbub phone number (929) 244-0748‬ when we are on
            our way to you. Feel free to text or call us at that number with any updates or changes
            on the day of {task.type}.
        </p>
        <p>
            Please be prompt, as a $5 {task.type} attempt charge will be made if you do not show
            up after 30 minutes. {clause}
        </p>
        <p>
            Let us know if anything looks incorrect with the above information or if you have any questions!
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Confirming your {task.type.capitalize()} Time"
    email_data["to"] = (renter.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "TASK-TIME"
    return email_data

def update_task_time_email(task, chosen_time):
    renter = Users.get({"id": task.renter_id})
    courier = Users.get({"id": task.logistics.courier_id})

    frame_data = {}
    frame_data["preview"] = f"Your {task.type} time has been updated to {chosen_time.strftime('%I:%M:00 %p')} - "
    frame_data["user"] = renter.name
    frame_data["introduction"] = f"""
        We have updated your {task.type} time. See the information below for details.
        """
    frame_data["content"] = get_task_update_table(task, chosen_time)

    total_tax = 0
    total_deposit = 0
    total_charge = 0
    for order in task["orders"]:
        reservation = order.reservation
        total_tax += reservation._tax
        total_deposit += reservation._deposit
        total_charge += reservation._charge
    if task.type == "pickup":
        charge = "" #"Your deposit will be returned at pickup."
        clause = """
            Please make sure each item is in a clean and usable state upon pickup,
            charges may be applied otherwise.
            """
    else:
        total = round(total_tax + total_deposit + total_charge, 2)
        charge = f"Total due at dropoff: ${total}"
        clause = ""
    frame_data["conclusion"] = f"""
            {charge}
        </p>
        <p>
            We will be sending you a text from our Hubbub phone number (929) 244-0748‬ when we are on
            our way to you. Feel free to text or call us at that number with any updates or changes
            on the day of {task.type}.
        </p>
        <p>
            Please be prompt, as a $5 {task.type} attempt charge will be made if you do not show
            up after 30 minutes. {clause}
        </p>
        <p>
            Let us know if anything looks incorrect with the above information or if you have any questions!
        """
    email_data = {}
    email_data["subject"] = f"[Hubbub] Updating your {task.type.capitalize()} Time"
    email_data["to"] = (renter.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "TASK-TIME"
    return email_data

def get_task_confirmation_email(task):
    renter = Users.get({"id": task.renter_id})
    courier = Users.get({"id": task.logistics.courier_id})

    task_date = datetime.strptime(task.task_date, "%Y-%m-%d").date()
    task_date_str = datetime.strftime(task_date, "%B %-d, %Y")
    item_names = get_linkable_items(task)

    address_formatted = f"{task.address.display()}"
    frame_data = {}
    frame_data["preview"] = f"Your {task.type} has been marked as completed! See this email for verification - "
    frame_data["user"] = renter.name
    if task.type == 'dropoff':
        intro = f"""
            This email is to confirm that your rental(s) beginning on {task_date_str}
            has been dropped off at <strong>{address_formatted}</strong>.
            """
        action = "receive"
    else:
        intro = f"""
            This email is to confirm that your rental(s) ending on {task_date_str}
            has been picked up.
            """
        action = "return"
    frame_data["introduction"] = intro
    frame_data["content"] = f"""
        <p>
            The item(s) in this rental order were: {item_names}
        </p>
        """

    frame_data["conclusion"] = f"""
            If you or someone you authorized did not {action} the above item(s),
            please contact us immediately at (929) 244-0748‬ or reply to this email.
            Otherwise, no action is needed.
        </p>
        <p>
            Please let us know if you ever need anything else!
        """

    email_data = {}
    email_data["subject"] = f"[Hubbub] Your {task.type.capitalize()} has been Completed!"
    email_data["to"] = (renter.email, SG.DEFAULT_RECEIVER)
    email_data["body"] = email_builder(frame_data)
    email_data["error"] = "TASK-COMPLETED"
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

def get_active_orders_table(orders):
    active_orders_table = f"""
        <table>
            <tr>
                <th>Item</th>
                <th>End Date</th>
            </tr>
        """
    for order in orders:
        item = Items.get(order.item_id)
        link = f"https://www.hubbub.shop/inventory/i/id={item.id}"
        order_end_date_str = datetime.strftime(order.ext_date_end, "%B %-d, %Y")
        row = f"""
            <tr>
                <td><a href='{link}'>{item.name}</a></td>
                <td>{order_end_date_str}</td>
            </tr>
            """
        active_orders_table += row
    active_orders_table += "</table>"
    return active_orders_table

def get_task_update_table(task, chosen_time):
    task_date = datetime.strptime(task["task_date"], "%Y-%m-%d").date()
    task_date_str = datetime.strftime(task_date, "%B %-d, %Y")

    item_names = get_linkable_items(task)

    task_table = f"""
        <table>
            <tr>
                <td>{task['type'].capitalize()} Date</td>
                <td>{task_date_str}</td>
            </tr>
            <tr>
                <td>{task['type'].capitalize()} Time</td>
                <td>{chosen_time.strftime('%-I:%M %p')}</td>
            </tr>
            <tr>
                <td>{task['type'].capitalize()} Address</td>
                <td>{task['address']['num']} {task['address']['street']}, {task['address']['city']} {task['address']['state']}, {task['address']['zip_code']}</td>
            </tr>
            <tr>
                <td>Item(s)</td>
                <td>{item_names}</td>
            </tr>
        </table>
        """
    return task_table

def get_cart_items(user):
    items = user.cart.contents
    cart_items_table = f"""
        <table>
            <tr>
                <th>Item</th>
            </tr>
        """
    for item in items:
        link = f"https://www.hubbub.shop/inventory/i/id={item.id}"
        row = f"""
            <tr>
                <td>
                    <a href='{link}'>{item.name}</a>
                </td>
            </tr>
            """
        cart_items_table += row
    cart_items_table += "</table>"
    return cart_items_table

def get_linkable_items(task):
    item_links =[]
    items = [order["item"] for order in task["orders"]]
    for item in items:
        link = f"https://www.hubbub.shop/inventory/i/id={item['id']}"
        item_links.append(f"<a href='{link}'>{item['name']}</a>")
    item_names = ", ".join(item_links)
    return item_names
