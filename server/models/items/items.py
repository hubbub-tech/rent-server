from blubber_orm import Models

class Items(Models):
    """
    A class to define the use of the Items type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    def __init__(self, attrs: dict):
        self.id = attrs["id"]
        self.name = attrs["name"]
        self.retail_price = attrs["retail_price"]
        self.is_visible = attrs["is_visible"]
        self.is_transactable = attrs["is_transactable"]
        self.is_featured = attrs["is_featured"]
        self.dt_created = attrs["dt_created"]
        self.is_locked = attrs["is_locked"]
        self.locker_id = attrs["locker_id"]
        self.description = attrs["description"]
        self.weight = attrs["weight"]
        self.weight_unit = attrs["weight_unit"]
        self.dim_height = attrs["dim_height"]
        self.dim_length = attrs["dim_length"]
        self.dim_width = attrs["dim_width"]
        self.dim_unit = attrs["dim_unit"]
        self.lister_id = attrs["lister_id"]

        self.address_line_1 = attrs["address_line_1"]
        self.address_line_2 = attrs["address_line_2"]
        self.address_city = attrs["address_city"]
        self.address_country = attrs["address_country"]
        self.address_zip = attrs["address_zip"]
