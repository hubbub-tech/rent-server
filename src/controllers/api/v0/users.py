from flask import Blueprint, make_response, request

from src.models import Users

bp = Blueprint("users", __name__)


@bp.get("/users")
@login_required
def get_users():
    user_ids = request.args.get("ids", None)
    user_ids = item_ids.split(",")

    users_to_dict = []
    for user_id in user_ids:
        user = Users.get({"id": user_id})

        if user is None: continue

        user_to_dict = user.to_dict()
        users_to_dict.append(user_to_dict)

    data = { "users": users_to_dict }
    response = make_response(data, 200)
    return response
