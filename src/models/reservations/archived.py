from blubber_orm import Models

class ReservationsArchived(Models):

    table_name = "reservations_archived"
    table_primaries = ["item_id", "renter_id", "dt_started", "dt_ended"]
    sensitive_attributes = []


    def __init__(self, attrs):
        self.dt_started = attrs["dt_started"]
        self.dt_ended = attrs["dt_ended"]
        self.item_id = attrs["item_id"]
        self.renter_id = attrs["renter_id"]
        self.dt_archived = attrs["dt_archived"]
        self.notes = attrs["notes"]
        self.order_id = attrs["order_id"]
