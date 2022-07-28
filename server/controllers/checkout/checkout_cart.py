from flask import Blueprint


bp = Blueprint("checkout", __name__)


@bp.get("/checkout")
@login_required
def checkout():
    photo_url = AWS.get_url(dir="items")
    items = []
    is_ready = g.user.cart.size() > 0
    ready_to_order_items = g.user.cart.get_reserved_contents()
    _cart_contents = g.user.cart.contents.copy()
    for item in _cart_contents:
        if is_item_in_itemlist(item, ready_to_order_items):
            reservation = Reservations.unique({
                "renter_id": g.user_id,
                "item_id": item.id,
                "is_in_cart": True
            })
            # @func: has someone ordered the item since you've added it to cart?
            if item.calendar.scheduler(reservation) == False:
                g.user.cart.remove(reservation)
                g.user.cart.add_without_reservation(item)
            elif not reservation.is_calendared:
                if item.calendar.scheduler(reservation) is None:
                    Items.set({"id": item.id}, {"is_available": False})
                    g.user.cart.remove(reservation)
                elif item.calendar.scheduler(reservation):
                    item_to_dict = item.to_dict()
                    item_to_dict["reservation"] = reservation.to_dict()
        else:
            is_ready = False
            item_to_dict = item.to_dict()
            item_to_dict["reservation"] = ''
        item_to_dict["details"] = item.details.to_dict()
        item_to_dict["calendar"] = item.calendar.to_dict()
        next_start, next_end = item.calendar.next_availability()
        item_to_dict["calendar"]["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["calendar"]["next_available_end"] = next_end.strftime("%Y-%m-%d")
        items.append(item_to_dict)
    return {
        "is_ready": is_ready,
        "photo_url": photo_url,
        "user": g.user.to_dict(),
        "cart": g.user.cart.to_dict(),
        "items": items
    }
