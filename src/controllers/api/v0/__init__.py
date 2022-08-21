from flask import Blueprint

from .items import bp as items
from .users import bp as users

bp = Blueprint("v0", __name__, url_prefix="v0")

bp.register_blueprint(items)
bp.register_blueprint(users)

CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
