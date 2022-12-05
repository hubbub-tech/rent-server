from blubber_orm import Models


class Issues(Models):

    table_name = "issues"
    table_primaries = ["id"]

    def __init__(self, attrs):
        self.id = attrs["id"]
        self.body = attrs["body"]
        self.slug = attrs["slug"]
        self.user_id = attrs["user_id"]
        self.resolution = attrs["resolution"]
        self.is_resolved = attrs["is_resolved"]
        self.dt_created = attrs["dt_created"]
