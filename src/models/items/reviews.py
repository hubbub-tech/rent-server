from blubber_orm import Models

class Reviews(Models):

    table_name = "reviews"
    table_primaries = ["id"]
    sensitive_attributes = []

    def __init__(self):
        self.id = attrs["id"]
        self.body = attrs["body"]
        self.dt_created = attrs["dt_created"]
        self.rating = attrs["rating"]
        self.item_id = attrs["item_id"]
        self.author_id = attrs["author_id"]
