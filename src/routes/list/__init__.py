from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .list_item import bp as list_item


bp = Blueprint("list", __name__)

bp.register_blueprint(list_item)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
