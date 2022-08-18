from flask import Blueprints, make_response, request

bp = Blueprint("cancel", __name__)


# PUT or DELETE request?
