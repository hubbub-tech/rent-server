from flask import Blueprint


bp = Blueprint("main", __name__)


@bp.get("/index")
def index():
    user_url = AWS.get_url(dir="users")
    testimonial = get_random_testimonials(size=1)

    if testimonial:
        testimonial = testimonial[0]
        testimonial_to_dict = testimonial.to_dict()

        user = Users.get({"id": testimonial.user_id})
        user_to_dict = user.to_dict()

        user_to_dict["name"] = user.alias
        user_to_dict["city"] = user.address.city
        user_to_dict["state"] = user.address.state
        user_to_dict["profile"] = user.profile.to_dict()
    else:
        user_to_dict = {}
        testimonial_to_dict = {}
    return {
        "user": user_to_dict,
        "testimonial": testimonial_to_dict,
        "photo_url": user_url
    }
