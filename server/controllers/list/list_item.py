from flask import Blueprint

bp = Blueprint("list", __name__)


@bp.post('/list/submit')
@login_required
def list_submit():
    format = "%Y-%m-%d"
    flashes = []
    data = request.form
    if data:
        if data.get("startDate") and data.get("endDate"):
            new_date_started = json_date_to_python_date(data["startDate"])
            new_date_ended = json_date_to_python_date(data["endDate"])
            form_data = {
                "item": {
                    "lister_id": g.user_id,
                    "name": data["name"],
                    "price": data["price"],
                    "address_line_1": data["line_1"],
                    "address_line_2": data["line_2"],
                    "address_zip": data["zip"]
                },
                "details": {
                    "description": data["description"],
                    "condition": data["condition"],
                    "volume": data["volume"],
                    "weight": data["weight"],
                    "id": None
                },
                "calendar": {
                    "date_started": new_date_started,
                    "date_ended": new_date_ended,
                    "id": None
                },
                "address": {
                    "line_1": data["line_1"],
                    "line_2": data["line_2"],
                    "city": data["city"],
                    "state": data["state"],
                    "zip": data["zip"]
                },
                "tags": ['all'] + data['tags'].split(","),
                "is_listed_from_user_address": strtobool(data["isDefaultAddress"])
            }
            image = request.files["image"]
            form_check = validate_listing(form_data)
            if form_check["is_valid"]:
                item = create_item(form_data)
                image_data = {
                    "self": item,
                    "image" : image,
                    "directory" : "items",
                    "bucket" : AWS.S3_BUCKET
                }
                upload_response = upload_image(image_data)
                if upload_response["is_valid"]:
                    email_data = get_new_listing_email(item)
                    send_async_email.apply_async(kwargs=email_data)
                    flashes.append(form_check["message"])
                    return {"flashes": flashes}, 200
                else:
                    flashes.append(upload_response["message"])
            else:
                flashes.append("There was an error getting the dates you set, make sure they're in 'MM/DD/YYYY'.")
        else:
            flashes.append("No data was sent.")
    else:
        flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, 406
