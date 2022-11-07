from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .orders_cancel import bp as orders_cancel
from .orders_early_return import bp as orders_early_return
from .orders_extend import bp as orders_extend
from .orders_history import bp as orders_history
from .orders_manage import bp as orders_manage
from .orders_view import bp as orders_view

bp = Blueprint("orders", __name__)

bp.register_blueprint(orders_cancel)
bp.register_blueprint(orders_early_return)
bp.register_blueprint(orders_extend)
bp.register_blueprint(orders_history)
bp.register_blueprint(orders_manage)
bp.register_blueprint(orders_view)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
