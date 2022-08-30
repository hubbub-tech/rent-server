from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .v0 import bp as v0

bp = Blueprint("api", __name__, url_prefix="/api")

bp.register_blueprint(v0)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
