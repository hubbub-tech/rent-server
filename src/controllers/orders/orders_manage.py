from flask import Blueprint

from src.models import Orders

from src.utils import get_receipt

bp = Blueprint("manage", __name__)


@bp.get('/order/receipt')
@login_required
def download_receipt():

    order_id = request.args.get("order_id")
    order = Orders.get({"id": order_id})

    if order is None:
        errors = ["We could not find the rental you're looking for."]
        response = make_response({"messages": errors}, 404)
        return response

    if order.renter_id != order.id:
        errors = ["You're not authorized to view this receipt."]
        response = make_response({"messages": errors}, 403)
        return response

    receipt = get_receipt(order)
    response = make_response({ "receipt": receipt }, 200)
    return response
