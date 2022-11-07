from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .items_edit import bp as items_edit
from .items_feed import bp as items_feed
from .items_view import bp as items_view
from .items_review import bp as items_review

bp = Blueprint('items', __name__)

bp.register_blueprint(items_edit)
bp.register_blueprint(items_feed)
bp.register_blueprint(items_view)
bp.register_blueprint(items_review)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
