from flask import Blueprint
from flask_cors import CORS

from src.utils.settings import FlaskConfig

from .auth_login import bp as auth_login
from .auth_manage import bp as auth_manage
from .auth_register import bp as auth_register


bp = Blueprint('auth', __name__)

bp.register_blueprint(auth_login)
bp.register_blueprint(auth_manage)
bp.register_blueprint(auth_register)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
