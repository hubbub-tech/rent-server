from flask import Blueprint

bp = Blueprint("item", __name__)


@bp.post("/accounts/i/hide/id=<int:item_id>")
@login_required
def hide_item(item_id):
    flashes = []
    item = Items.get({"id": item_id})
    if item:
        if item.lister_id == g.user_id:
            data = request.json
            if data: Items.set({"id": item_id}, {"is_available": data["toggle"]})

            if item.is_available: flashes.append("Item has been revealed.")
            else: flashes.append("Item has been hidden.")
            return {"flashes": flashes}, 200
        else:
            flashes.append("You are not authorized to manage the visibility of this item.")
            return {"flashes": flashes}, 403
    return {"flashes": ["This item does not exist at the moment."]}, 404

@bp.get("/accounts/i/edit/id=<int:item_id>")
@login_required
def edit_item(item_id):
    flashes = []
    item = Items.get({"id": item_id})
    if item:
        if item.lister_id == g.user_id:
            item_to_dict = item.to_dict()
            item_to_dict["details"] = item.details.to_dict()
            item_to_dict["calendar"] = item.calendar.to_dict()
            return { "item": item_to_dict }, 200
        else:
            flashes.append("You are not authorized to manage the visibility of this item.")
            return {"flashes": flashes}, 403
    return {"flashes": ["this item does not exist at the moment."]}, 404

@bp.post("/accounts/i/edit/submit")
@login_required
def edit_item_submit():
    flashes = []
    data = request.json
    if data:
        item = Items.get({"id": data["itemId"]})
        # date_end_extended = json_date_to_python_date(data["extendEndDate"])
        form_data = {
            "price": data.get("price", item.price),
            "description": data.get("description", item.details.description),
            # "extend": date_end_extended
        }
        Items.set({"id": item.id}, {"price": form_data["price"]})
        Details.set({"id": item.id}, {"description": form_data["description"]})
        # Calendars.set({"id": item.id}, {"date_ended": date_end_extended})
        flashes.append(f"Your {item.name} has been updated!")
        return {"flashes": flashes}, 200
    flashes.append("No changes were received! Try again.")
    return {"flashes": flashes}, 406

@bp.post("/accounts/i/photo/submit")
@login_required
def edit_item_photo_submit():
    flashes = []
    data = request.form
    item = Items.get({"id": data["itemId"]})
    image = request.files.get("image")
    if image and item:
        image_data = {
            "self": item.id,
            "image" : image,
            "directory" : "items",
            "bucket" : AWS.S3_BUCKET
        }
        upload_response = upload_image(image_data)
        if upload_response["is_valid"]:
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 200
        else:
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 406
    return {"flashes": ["Failed to receive the photo update for your item."]}, 406
