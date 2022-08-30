from flask import Blueprint

bp = Blueprint('feedback', __name__)


@bp.post('/feedback/submit')
def feedback_submit():
    flashes = []
    data = request.json
    if data:
        feedback = {
            "link": data["href"],
            "complaint": data["feedback"],
            "user_id": data.get('userId')
        }
        # issue = Issues.insert(feedback)
        flashes.append("We got your feedback! Thanks for your patience :)!")
        return {"flashes": flashes}, 200
    flashes.append(f"There was a problem receiving your feedback :(... Try again or email at hello@hubbub.shop.")
    return {"flashes": flashes}, 406
