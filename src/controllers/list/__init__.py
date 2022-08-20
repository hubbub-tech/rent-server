from flask import Blueprint
from flask_cors import CORS

from .list_item import list_item


bp = Blueprint("list", __name__)

bp.register_blueprint(list_item)

CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
