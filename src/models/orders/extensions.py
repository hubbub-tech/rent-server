from blubber_orm import Models


class Extensions(Models):
    """
    FILLER
    """

    table_name = "extensions"
    table_primaries = ["order_id", "res_dt_start"]
    sensitive_attributes = []

    def __init__(self, attrs):
        self.order_id = attrs["order_id"]
        self.renter_id = attrs["renter_id"]
        self.item_id = attrs["item_id"]
        self.res_dt_start = attrs["res_dt_start"]
        self.res_dt_end = attrs["res_dt_end"]


    def to_query_reservation(self):
        query_res = {
            "renter_id": self.renter_id,
            "item_id": self.item_id,
            "dt_started": self.res_dt_start,
            "dt_ended": self.res_dt_end
        }

        return query_res
