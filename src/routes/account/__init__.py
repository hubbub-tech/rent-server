from flask import Blueprint
from flask_cors import CORS


from src.utils.settings import FlaskConfig

from .account_edit import bp as account_edit
from .account_view import bp as account_view


bp = Blueprint('account', __name__)

bp.register_blueprint(account_edit)
bp.register_blueprint(account_view)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
