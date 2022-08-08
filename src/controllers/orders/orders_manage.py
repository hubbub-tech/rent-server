from flask import Blueprint


bp = Blueprint("orders", __name__)


@bp.get("/accounts/o/id=<int:order_id>")
@login_required
def manage_order(order_id):
    photo_url = AWS.get_url(dir="items")
    flashes = []
    order = Orders.get({"id": order_id})
    if order:
        item = Items.get({"id": order.item_id})
        is_extended = order.ext_date_end != order.res_date_end
        if g.user_id == order.renter_id:
            item_to_dict = item.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            item_to_dict["details"] = item.details.to_dict()

            order_to_dict = order.to_dict()
            order_to_dict["is_extended"] = is_extended
            order_to_dict["ext_date_start"] = order.ext_date_start.strftime("%Y-%m-%d")
            order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
            order_to_dict["reservation"] = order.reservation.to_dict()

            lister = Users.get({"id": order.lister_id})
            order_to_dict["lister"] = lister.to_dict()
            order_to_dict["item"] = item_to_dict
            return {
                "order": order_to_dict,
                "photo_url": photo_url
            }
        else:
            flashes.append("You can only manage orders that you placed.")
            return {"flashes": flashes}, 406
    else:
        return {"flashes": ["This order does not exist at the moment."]}, 404


@bp.get('/accounts/o/receipt/id=<int:order_id>')
@login_required
def download_receipt(order_id):
    order = Orders.get({"id": order_id})
    if order:
        if g.user_id == order.renter_id:
            receipt = generate_receipt_json(order)
            return { "receipt": receipt }, 200
        return {"flashes": ["You're not authorized to view this receipt."]}, 406
    return {"flashes": ["This order does not exist at the moment."]}, 404
