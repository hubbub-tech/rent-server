from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

from src.models import Users, Items, Calendars

from src.utils.classes import Status


def validate_login(form_data):
    loaded_user = Users.unique({"email": form_data["email"]})

    status = Status()
    if loaded_user is None:
        status.message = "Could not find this user."
        status.is_successful = False
        return status

    if not check_password_hash(loaded_user.password, form_data["password"]):
        status.message = "Sorry, invalid password and email combination."
        status.is_successful = False
        return status

    status.message = "Successful email and password match!"
    status.is_successful = True
    return status



def validate_registration(form_data):
    loaded_user = Users.unique({"email": form_data["email"]})

    status = Status()
    if loaded_user:
        status.message = "You might already have an account. Try logging in!"
        status.is_successful = False
        return status

    status.message = "Passed validation checks!"
    status.is_successful = True
    return status


# for now does nothing but will be import for validation
def validate_date_range(dt_lbound: datetime, dt_ubound: datetime):

    status = Status()
    if dt_lbound >= dt_ubound:
        status.message = "Your end date must be at least one date after your start date."
        status.is_successful = False
        return status

    status.message = "Valid calendar range!"
    status.is_successful = True
    return status


def validate_rental(calendar: Calendars, dt_started: datetime, dt_ended: datetime):

    DAYS_BUFFER = 2
    MAX_RENTAL_DURATION = 365

    status = validate_date_range(dt_lbound=dt_started, dt_ubound=dt_ended)

    if status.is_successful == False:
        return status

    status = Status()
    if (dt_ended - dt_started).days > MAX_RENTAL_DURATION:
        status.message = f"Rentals cannot exceed {MAX_RENTAL_DURATION} days."
        status.is_successful = False
        return status

    if calendar.check_reservation(dt_started, dt_ended, days_buffer=0) == False:
        res_dt_start, res_dt_end = calendar.best_match_reservation(dt_started, dt_ended, days_buffer=0)

        avail_date_start_str = res_dt_start.strftime("%B %-d, %Y")

        if res_dt_end > datetime.now() + timedelta(weeks=104):
            avail_date_range = avail_date_start_str
        else:
            avail_date_end_str = res_dt_end.strftime("%B %-d, %Y")
            avail_date_range = f"{avail_date_start_str} until {avail_date_end_str}"

        status.message = f"""
            This item is unavailable for the period you requested. Currently, the
            item is available starting {avail_date_range}. You can also request more of this
            item in the form at the bottom of the page, and we will get back to you within 48hrs!
            """

        status.is_successful = False
        return status

    elif calendar.check_reservation(dt_started, dt_ended, days_buffer=0) is None:
        Items.set({"id": calendar.id}, {"is_available": False})

        status.message = """
            Sorry, the item is not currently available. You can also request more of
            this item in the form at the bottom of the page, and we will get back to
            you within 48hrs!
            """

        status.is_successful = False
        return status

    status.message = "The item is available for this period!"
    status.is_successful = True
    return status
