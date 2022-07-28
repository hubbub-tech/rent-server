from flask import Blueprint


bp = Blueprint("account", __name__)


#edit personal account
@bp.get("/accounts/u/edit")
@login_required
def edit_account():
    photo_url = AWS.get_url(dir="users")
    user_to_dict = g.user.to_dict()
    user_to_dict["address"] = g.user.address.to_dict()
    user_to_dict["profile"] = g.user.profile.to_dict()
    return {
        "user": user_to_dict,
        "photo_url": photo_url
    }

#edit personal account
@bp.post("/accounts/u/edit/submit")
@login_required
def edit_account_submit():
    flashes = []
    data = request.json
    form_data = {
        "self": g.user,
        "email": data.get("email", g.user.email),
        "bio": data.get("bio", g.user.profile.bio),
        "payment": data.get("payment", g.user.payment),
        "phone": data.get("phone", g.user.profile.phone)
    }

    form_check = validate_edit_account(form_data)
    if form_check["is_valid"]:
        Users.set({"id": g.user_id}, {
            "email": form_data["email"],
            "payment": form_data["payment"]
        })
        Profiles.set({"id": g.user_id}, {
            "bio": form_data["bio"],
            "phone": form_data["phone"]
        })
        flashes.append("Successfully edited your account!")
        return {"flashes": flashes}, 200
    else:
        flashes.append(form_check["message"])
        return {"flashes": flashes}, 406

@bp.post("/accounts/u/photo/submit")
@login_required
def edit_account_photo_submit():
    flashes = []
    image = request.files.get("image")
    if image:
        image_data = {
            "self": g.user,
            "image" : image,
            "directory" : "users",
            "bucket" : AWS.S3_BUCKET
        }
        upload_response = upload_image(image_data)
        if upload_response["is_valid"]:
            Profiles.set({"id": g.user_id}, {"has_pic": True})
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 200
        else:
            flashes.append(upload_response["message"])
            return {"flashes": flashes}, 406
    return {"flashes": ["Failed to receive your profile update."]}, 406

#edit personal password
#check that the confirmation pass and new pass match on frontend
@bp.post("/accounts/u/password/submit")
@login_required
def edit_password_submit():
    flashes = []
    errors = []
    data = request.json
    if data:
        form_data = {
            "self" : g.user,
            "current_password" : data["password"]["old"],
            "new_password" : data["password"]["new"]
        }
        form_check = validate_edit_password(form_data)
        if form_check["is_valid"]:
            hashed_pass = generate_password_hash(form_data["new_password"])
            Users.set({"id": g.user_id}, {"password": hashed_pass})

            flashes.append(form_check["message"])
            return {"flashes": flashes}, 200
        else:
            errors.append(form_check["message"])
            return {"errors": errors}, 406
    flashes.append("No data was sent! Try again.")
    return {"flashes": flashes}, 406
