from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .delivery_cancel import bp as delivery_cancel
from .delivery_sched import bp as delivery_sched
from .delivery_view import bp as delivery_view


bp = Blueprint('delivery', __name__)

bp.register_blueprint(delivery_cancel)
bp.register_blueprint(delivery_sched)
bp.register_blueprint(delivery_view)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
