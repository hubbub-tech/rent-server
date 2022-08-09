from flask import Blueprint

from .v0 import bp as v0

bp = Blueprint("api", __name__, url_prefix="api")

bp.register_blueprint(v0)

CORS(
    bp,
    origins=[Config.CORS_ALLOW_ORIGIN_SHOP],
    supports_credentials=Config.CORS_SUPPORTS_CREDENTIALS
)
