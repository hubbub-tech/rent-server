from flask import Blueprint, make_response, request

from src.models import Users

from src.utils import create_issue

from src.utils.settings import (
    CODE_2_OK,
    CODE_4_BAD_REQUEST,
    CODE_5_SERVER_ERROR
)

from src.utils.settings import smtp_config

bp = Blueprint('feedback', __name__)


@bp.post('/feedback')
def give_feedback():

    try:
        slug = request.json["feedbackSlug"]
        body = request.json["feedbackBody"]
        user_id = request.json.get("userId")
    except KeyError:
        error = "Sorry, you didn't provide enough information to complete your request."
        response = make_response({ "message": error }, CODE_4_BAD_REQUEST)
        return response
    except Exception as e:
        error = "Whoops, something went wrong on our end... Come back later."
        response = make_response({ "message": error }, CODE_5_SERVER_ERROR)
        return response

    if user_id: user = Users.get({ "id": user_id })
    else: user = None

    slug = slug[:127]
    issue_data = { "slug": slug, "body": body }

    if user:
        issue_data["user_id"] = user_id
        issue = create_issue(issue_data)
    else:
        issue_data["user_id"] = None
        issue = create_issue(issue_data)

    message = f"We got your feedback, thanks! You can always reach us at {smtp_config.DEFAULT_SENDER}."
    response = make_response({ "message": message }, CODE_2_OK)
    return response
