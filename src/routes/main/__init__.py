from flask import Blueprint
from flask_cors import CORS


from src.utils.settings import FlaskConfig

from .main_feedback import bp as main_feedback
from .main_index import bp as main_index
from .main_newsletter import bp as main_newsletter

bp = Blueprint("main", __name__)

bp.register_blueprint(main_feedback)
bp.register_blueprint(main_index)
bp.register_blueprint(main_newsletter)

CORS(
    bp,
    origins=[FlaskConfig.CORS_ALLOW_ORIGIN],
    supports_credentials=FlaskConfig.CORS_SUPPORTS_CREDENTIALS
)
