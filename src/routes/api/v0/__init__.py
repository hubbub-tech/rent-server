from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .items import bp as items
from .users import bp as users
from .orders import bp as orders

bp = Blueprint("v0", __name__, url_prefix="/v0")

bp.register_blueprint(items)
bp.register_blueprint(users)
bp.register_blueprint(orders)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
