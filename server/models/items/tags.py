from blubber_orm import Models

class Tags(Models):

    table_name = "tags"
    table_primaries = ["title"]


    def __init__(self, attrs):
        self.title = attrs["title"]
