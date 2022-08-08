from flask import Blueprint
from flask_cors import CORS


from .account_edit import bp as account_edit
from .account_view import bp as account_view


bp = Blueprint('account', __name__)

bp.register_blueprint(account_edit)
bp.register_blueprint(account_view)

CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
