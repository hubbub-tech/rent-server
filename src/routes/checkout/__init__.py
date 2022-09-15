from flask import Blueprint
from flask_cors import CORS

from src.utils import FlaskConfig

from .checkout_cart import bp as checkout_cart
from .checkout_add import bp as checkout_add
from .checkout_edit import bp as checkout_edit
from .checkout_remove import bp as checkout_remove
from .checkout_execute import bp as checkout_execute
from .checkout_webhook import bp as checkout_webhook


bp = Blueprint("checkout", __name__)

bp.register_blueprint(checkout_cart)
bp.register_blueprint(checkout_add)
bp.register_blueprint(checkout_edit)
bp.register_blueprint(checkout_remove)
bp.register_blueprint(checkout_execute)
bp.register_blueprint(checkout_webhook)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
