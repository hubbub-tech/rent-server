from flask import Blueprint


bp = Blueprint("orders", __name__)


@bp.get("/accounts/u/orders")
@login_required
def order_history():
    photo_url = AWS.get_url(dir="items")
    order_history = Orders.filter({"renter_id": g.user_id})
    orders = []
    if order_history:
        for order in order_history:

            item = Items.get({"id": order.item_id})
            item_to_dict = item.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            item_to_dict["details"] = item.details.to_dict()

            order_to_dict = order.to_dict()
            order_to_dict["is_extended"] = order.ext_date_end != order.res_date_end
            order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
            order_to_dict["reservation"] = order.reservation.to_dict()

            lister = Users.get({"id": order.lister_id})
            order_to_dict["lister"] = lister.to_dict()
            order_to_dict["item"] = item_to_dict

            orders.append(order_to_dict)
        json_sort(orders, "date_placed", reverse=True)
    return {
        "photo_url": photo_url,
        "orders": orders
    }
