from .factories import create_user
from .factories import create_item
from .factories import create_review
from .factories import create_reservation
from .factories import create_logistics
from .factories import create_extension
from .factories import create_order
from .factories import create_address
from .factories import create_charge
from .factories import create_issue

from .validators import validate_rental
from .validators import validate_date_range
from .validators import validate_login
from .validators import validate_registration

from .emails import *

from .safe_txns import lock_cart, unlock_cart, check_lock_access
from .safe_txns import get_stripe_checkout_session
from .safe_txns import get_stripe_extension_session
from .safe_txns import return_order_early

from .files import get_receipt
from .files import upload_email_data
from .files import upload_file_from_base64

from .auth import handle_preflight_only
from .auth import login_required, login_optional, login_user
from .auth import gen_token, verify_token

from .deliveries import attach_timeslots
from .deliveries import get_nearest_storage


def strip_non_numericals(value: str):
    assert value, "Must be of type string."
    return ''.join(e for e in value if e.isalnum())
