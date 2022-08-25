from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

from blubber_orm import Users, Items


def validate_login(form_data):
    loaded_user = Users.unique({"email": form_data["email"]})

    status = Status()
    if loaded_user is None:
        status.messages.append("Could not find this user.")
        status.is_successful = False
        return status

    if not check_password_hash(loaded_user.password, form_data["password"]):
        status.messages.append("Sorry, invalid password and email combination.")
        status.is_successful = False
        return status

    status.messages.append("Successful email and password match!")
    status.is_successful = True
    return status



def validate_registration(form_data):
    loaded_user = Users.unique({"email": form_data["email"]})

    status = Status()
    if loaded_user:
        status.messages.append("You might already have an account. Try logging in!")
        status.is_successful = False
        return status

    status.messages.append("Passed validation checks!")
    status.is_successful = True
    return status


# for now does nothing but will be import for validation
def validate_date_range(dt_lbound: datetime, dt_ubound: datetime):

    status = Status()
    if dt_lbound >= dt_ubound:
        status.messages.append("Lower bound date cannot be greater than or equal to upper bound date.")
        status.is_successful = False
        return status

    status.messages.append("Valid calendar range!")
    status.is_successful = True
    return status


def validate_rental(calendar: Calendars, dt_started: datetime, dt_ended: datetime):

    DAYS_BUFFER = 2
    MAX_RENTAL_DURATION = 365

    rental_start_date = rental_range["date_started"]
    rental_end_date = rental_range["date_ended"]

    status = validate_date_range(dt_lbound=dt_started, dt_ubound=dt_ended)

    if status.is_successful == False:
        return status

    status = Status()
    if (rental_end_date - rental_start_date).days > MAX_RENTAL_DURATION:
        status.messages.append(f"Rentals cannot exceed {MAX_RENTAL_DURATION} days.")
        status.is_successful = False
        return status

    if calendar.check_reservation(dt_started, dt_ended, days_buffer=0) == False:
        res_dt_start, res_dt_end = best_match_reservation(dt_started, dt_ended, days_buffer=0)

        avail_date_start_str = res_dt_start.strftime("%B %-d, %Y")

        if res_dt_end > datetime.now() + timedelta(years=10):
            avail_date_range = avail_date_start_str
        else:
            avail_date_end_str = res_dt_end.strftime("%B %-d, %Y")
            avail_date_range = f"{avail_date_start_str} until {avail_date_end_str}"

        status.messages.append("This item is unavailable for the period you requested.")
        status.messages.append(f"Currently, the item is available starting {avail_date_range}.")
        status.messages.append("You can also request more of this item in the form at the bottom of the page, and we will get back to you within 48hrs!")

        status.is_successful = False
        return status

    elif calendar.check_reservation(dt_started, dt_ended, days_buffer=0) is None:
        Items.set({"id": calendar.id}, {"is_available": False})

        status.messages.append("Sorry, the item is not currently available.")
        status.messages.append("You can also request more of this item in the form at the bottom of the page, and we will get back to you within 48hrs!")
        status.is_successful = False
        return status

    status.messages.append("The item is available for this period!")
    status.is_successful = True
    return status
