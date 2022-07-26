from flask import Blueprint

bp = Blueprint('login', __name__)


@bp.get("/inventory", defaults={"search": None})
@bp.get("/inventory/search=<search>")
def inventory(search):
    photo_url = AWS.get_url(dir="items")
    if search:
        listings = search_items(search)
    else:
        listings = Items.filter({"is_available": True})
    listings_to_dict = []
    featured_to_dict = []
    for item in listings:
        lister = Users.get({"id": item.lister_id})
        tags = Tags.by_item(item)
        item_to_dict = item.to_dict()
        next_start, next_end  = item.calendar.next_availability()
        item_to_dict["next_available_start"] = next_start.strftime("%Y-%m-%d")
        item_to_dict["next_available_end"] = next_end.strftime("%Y-%m-%d")
        item_to_dict["details"] = item.details.to_dict()
        item_to_dict["lister"] = lister.to_dict()
        item_to_dict["lister"]["name"] = lister.name
        item_to_dict["tags"] = [tag.name for tag in tags]
        if item.is_featured:
            featured_to_dict.append(item_to_dict)
        else:
            listings_to_dict.append(item_to_dict)
    json_sort(listings_to_dict, "next_available_start")
    for item in listings_to_dict:
        featured_to_dict.append(item)
    return {
        "items": featured_to_dict,
        "photo_url": photo_url
        }
