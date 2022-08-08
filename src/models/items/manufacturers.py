from blubber_orm import Models


class Manufacturers(Models):
    """
    A class to define the use of the Manufacturers type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """
    table_name = "manufacturers"
    table_primaries = ["id"]

    def __init__(self, attrs):
        self.id = attrs["id"]
        self.brand = attrs["brand"]
