from flask import Blueprint, make_response, request, g

from src.models import Items

from src.utils import create_review
from src.utils import login_required

bp = Blueprint("review", __name__)

# NOTE: Consider only allowing people who have rented to leave reviews.
@bp.post("/items/review")
@login_required
def review_item():

    item_id = request.args.get("id", None)
    item = Items.get({"id": item_id})

    if item is None:
        errors = ["We can't seem to find the item that you're looking for."]
        response = make_response({"messages": errors}, 404)
        return response

    if item.lister_id == g.user_id:
        errors = ["Listers cannot write reviews on their own items."]
        response = make_response({"messages": errors}, 403)
        return response

    review_body = request.json.get("body", "No review provided.")
    review_rating = request.json.get("rating", None)

    review_data = {
        "item_id": item.id,
        "author_id": g.user_id,
        "body": review_body,
        "rating": review_rating
    }

    review = create_review(review_data)
    messages = [f"Your review on the item, '{item.name}' has been received. Thanks!"]
    response = make_response({"messages": messages}, 200)
    return response
