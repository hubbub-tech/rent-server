from flask import Blueprint, make_response, request

from src.models import Tags

from src.utils.settings import CODE_2_OK

bp = Blueprint("tags", __name__)

@bp.get("/tags")
def get_tags():

    tags = Tags.get_all()

    tags_to_dict = []
    for tag in tags:

        tag_to_dict = tag.to_dict()
        tags_to_dict.append(tag_to_dict)

    data = { "tags": tags_to_dict }
    response = make_response(data, CODE_2_OK)
    return response
