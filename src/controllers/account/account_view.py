from flask import Blueprint

bp = Blueprint("account", __name__)


@bp.get("/accounts/<int:id>")
def view_account():
    pass
