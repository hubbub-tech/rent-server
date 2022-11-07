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
        error = "We can't seem to find the item that you're looking for."
        response = make_response({"message": error}, 404)
        return response

    if item.lister_id == g.user_id:
        error = "Listers cannot write reviews on their own items."
        response = make_response({"message": error}, 403)
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
    message = f"Your review on the item, '{item.name}' has been received. Thanks!"
    response = make_response({"message": message}, 200)
    return response
