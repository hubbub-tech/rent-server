from flask import Blueprint
from flask_cors import CORS


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
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
