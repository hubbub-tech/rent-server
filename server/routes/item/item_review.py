@bp.get("/accounts/o/review/id=<int:order_id>")
@login_required
def review_item(order_id):
    flashes = []
    order = Orders.get({"id": order_id})
    if order:
        item = Items.get(order.item_id)
        if order.renter_id == g.user_id:
            item_to_dict = item.to_dict()
            item_to_dict["details"] = item.details.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            order_to_dict = order.to_dict()
            order_to_dict["ext_date_end"] = order.ext_date_end.strftime("%Y-%m-%d")
            order_to_dict["reservation"] = order.reservation.to_dict()
            return { "item": item_to_dict, "order": order_to_dict }, 200
        else:
            flashes.append("You are not authorized to manage the visibility of this item.")
            return {"flashes": flashes}, 406
    return {"flashes": ["this order does not exist at the moment."]}, 404


@bp.post("/accounts/o/review/submit")
@login_required
def review_item_submit():
    flashes = []
    data = request.json
    if data:
        item = Items.get({"id": data["itemId"]})
        review_data = {
            "item_id": item.id,
            "author_id": g.user_id,
            "body": data.get("body", "No review provided."),
            "rating": data.get("rating")
        }
        review = create_review(review_data)
        flashes.append(f"Thanks for your feedback on your {item.name} rental!")
        return {"flashes": flashes}, 200
    return {"flashes": ["No changes were received! Try again."]}, 406
