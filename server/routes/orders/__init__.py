from flask import Blueprint
from flask_cors import CORS


bp = Blueprint("orders", __name__)


CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
