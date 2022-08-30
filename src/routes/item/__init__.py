from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .item_edit import bp as item_edit
from .item_feed import bp as item_feed
from .item_view import bp as item_view
from .item_review import bp as item_review

bp = Blueprint('items', __name__)

bp.register_blueprint(item_edit)
bp.register_blueprint(item_feed)
bp.register_blueprint(item_view)
bp.register_blueprint(item_review)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
