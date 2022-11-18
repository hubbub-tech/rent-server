from flask import Blueprint, make_response, request

from src.models import Users

from src.utils import login_required

from src.utils.settings import CODE_2_OK

bp = Blueprint("users", __name__)


@bp.get("/users")
@login_required
def get_users():
    user_ids = request.json["ids"]

    users_to_dict = []
    for user_id in user_ids:
        user = Users.get({"id": user_id})

        if user is None: continue

        user_to_dict = user.to_dict()
        users_to_dict.append(user_to_dict)

    data = { "users": users_to_dict }
    response = make_response(data, CODE_2_OK)
    return response
