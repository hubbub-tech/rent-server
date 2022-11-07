from flask import Blueprint


bp = Blueprint("index", __name__)


@bp.get("/index")
def index():
    return {"messages": "Hello!"}, 200
