from blubber_orm import Models


class Promos(Models):

    table_name = "promos"
    table_primaries = ["title"]
    sensitive_attributes = []


    def __init__(self, attrs):
        self.title = attrs["title"]
        self.sku = attrs["sku"]
        self.description = attrs["description"]
        self.discount_value = attrs["discount_value"]
        self.discount_unit = attrs["discount_unit"]
        self.discount_type = attrs["discount_type"]
        self.dt_activated = attrs["dt_activated"]
        self.dt_expired = attrs["dt_expired"]
