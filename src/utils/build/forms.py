import boto3
from datetime import datetime, date, timedelta
from botocore.exceptions import NoCredentialsError
from werkzeug.security import check_password_hash, generate_password_hash
from blubber_orm import Users, Items

from server.tools.settings import AWS, SG

# is_valid -> bool
# messages -> array of messages (str)


#done 5/21
def validate_edit_account(form_data):
    is_valid = True
    message = None
    registered_email_owner = Users.unique({"email": form_data["email"]})
    if registered_email_owner:
        if registered_email_owner.id != form_data["self"].id:
            is_valid = False
            message = "Sorry, the email you want to user is already in use."
    elif not form_data["email"]:
        form_data["email"] = form_data["self"].email
    if form_data["payment"]:
        if "@" in form_data["payment"] and "@" == form_data["payment"][0]:
            form_data["payment"] = form_data["payment"].replace("@", "", 1)

    if not form_data["payment"]: form_data["payment"] = form_data["self"].payment
    if not form_data["phone"]: form_data["phone"] = form_data["self"].profile.phone
    if not form_data["bio"]: form_data["bio"] = form_data["self"].profile.bio
    return {
        "is_valid" : is_valid,
        "message" : message
        }

def validate_edit_password(form_data):
    is_valid = False
    _self = form_data["self"]
    if not check_password_hash(_self.password, form_data["current_password"]):
        message = "The password you entered is incorrect."
    else:
        is_valid = True
        message = "Your password was successfully changed!"
    return {
        "is_valid" : is_valid,
        "message" : message
        }

def validate_registration(form_data):
    is_valid = False
    loaded_user = Users.unique({"email": form_data["email"]})
    if loaded_user:
        message = "You might already have an account. Try logging in!"
    else:
        if form_data["payment"] is None:
            form_data["payment"] = "NA"
        elif "@" in form_data["payment"] and "@" == form_data["payment"][0]:
            form_data["payment"] = form_data["payment"].replace("@", "", 1)
        is_valid = True
        message = "You're registered on Hubbub, now login to get started!"
    return {
        "is_valid" : is_valid,
        "message" : message
        }

def validate_login(form_data):
    is_valid = False
    loaded_user = Users.unique({"email": form_data["email"]})
    if loaded_user:
        if not check_password_hash(loaded_user.password, form_data["password"]):
            message = "Sorry, invalid password and email combination."
        else:
            is_valid = True
            message = "You logged in, welcome back!"
    else:
        message = "Sorry, invalid password and email combination."
    return {
        "is_valid" : is_valid,
        "message" : message
        }

# for now does nothing but will be import for validation
def validate_listing(form_data):
    is_valid = True
    message = "Successful listing! Go to the Rent Page to check it out!"
    return {
        "is_valid" : is_valid,
        "message" : message
        }

def validate_rental_bounds(item, rental_range):
    is_valid = False
    min_days_to_rental_start = 2
    max_rental_period = 365
    rental_start_date = rental_range["date_started"]
    rental_end_date = rental_range["date_ended"]
    if date.today() + timedelta(days=4) >= item.calendar.date_ended:
        Items.set({"id": item.id}, {"is_available": False})
        message = "Sorry, the item is not currently available."

    elif rental_start_date < item.calendar.date_started:
        message = f"""
            The {item.name} is unavailable for the period you requested. It
            is listed starting {item.calendar.date_started.strftime("%B %-d, %Y")} to
            {item.calendar.date_ended.strftime("%B %-d, %Y")}.
            """
    elif rental_end_date > item.calendar.date_ended:
        message = f"""
            The {item.name} is unavailable for the period you requested. It
            is listed starting {item.calendar.date_started.strftime("%B %-d, %Y")} to
            {item.calendar.date_ended.strftime("%B %-d, %Y")}.
            """
    elif rental_start_date < date.today() + timedelta(days=min_days_to_rental_start):
        message = f"The earliest your rental can start is {min_days_to_rental_start} days from today."

    elif (rental_end_date - rental_start_date).days > max_rental_period:
        message = f"Rentals cannot exceed {max_rental_period} days."

    else:
        is_valid = True
        message = "Your proposed rental is within the calendar bounds."
    return {
        "is_valid": is_valid,
        "message": message
        }

def upload_image(image_data):
    is_valid = False

    image = image_data["image"]
    _self = image_data["self"]
    dir = image_data["directory"]
    bucket = image_data["bucket"]

    path = f"{dir}/{_self.id}.jpg"
    s3_resource = AWS.get_s3_resource()
    try:
        s3_resource.Bucket(bucket).put_object(Key=path, Body=image, ACL='public-read')
    except FileNotFoundError:
        #logging here
        message = f"The file was not found by the cloud. Contact admins at {SG.DEFAULT_RECEIVER} for help."
    except NoCredentialsError:
        #logging here
        message = f"Credentials not available. Contact admins at {SG.DEFAULT_RECEIVER} for help."
    else:
        is_valid = True
        message = "Photo was successfully saved!"
    return {
        "is_valid" : is_valid,
        "message" : message
        }
