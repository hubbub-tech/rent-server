from flask import Blueprint

bp = Blueprint("details", __name__)


@bp.get("/inventory/i/id=<int:item_id>")
def view_item(item_id):
    photo_url = AWS.get_url(dir="items")
    item = Items.get({"id": item_id})
    if item:
        lister = Users.get({"id": item.lister_id})
        item_to_dict = item.to_dict()
        item_to_dict["lister_name"] = lister.name
        next_start, next_end = item.calendar.next_availability()
        item_to_dict["address"] = item.address.to_dict()
        item_to_dict["details"] = item.details.to_dict()
        item_to_dict["calendar"] = item.calendar.to_dict()
        item_to_dict["calendar"]["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["calendar"]["next_available_end"] = next_end.strftime("%Y-%m-%d")

        recommendations = get_recommendations(item.name)
        recs_to_dict = []
        for rec in recommendations:
            lister = Users.get({"id": rec.lister_id})
            rec_to_dict = rec.to_dict()
            next_start, next_end  = rec.calendar.next_availability()
            rec_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
            rec_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
            rec_to_dict["details"] = rec.details.to_dict()
            rec_to_dict["lister"] = lister.to_dict()
            rec_to_dict["lister"]["name"] = lister.name
            recs_to_dict.append(rec_to_dict)
        return {
            "item": item_to_dict,
            "photo_url": photo_url,
            "recommendations": recs_to_dict
        }
    else:
        return {"flashes": ["This item does not exist at the moment."]}, 404
