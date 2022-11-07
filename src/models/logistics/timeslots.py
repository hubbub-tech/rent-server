from blubber_orm import Models


class Timeslots(Models):


    table_name = "timeslots"
    table_primaries = ["logistics_id", "dt_range_start", "dt_range_end"]
    sensitive_attributes = []


    def __init__(self, attrs):
        self.logistics_id = attrs["logistics_id"]
        self.dt_range_start = attrs["dt_range_start"]
        self.dt_range_end = attrs["dt_range_end"]
        self.is_sched = attrs["is_sched"]
        self.dt_sched_eta = attrs["dt_sched_eta"]
