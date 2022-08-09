from flask import Blueprint

from .items import bp as items

bp = Blueprint("v0", __name__, url_prefix="v0")

bp.register_blueprint(items)

CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
