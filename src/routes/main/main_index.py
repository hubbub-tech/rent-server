from flask import Blueprint, make_response

bp = Blueprint("index", __name__)

@bp.get("/index")
def index():
    data = { "message": "Hello, World!" }
    response = make_response(data, 200)
    return response
