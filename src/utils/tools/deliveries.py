from datetime import datetime

from src.models import Timeslots
from src.utils.classes import Status

def schedule_deliveries(logistics, order_ids, timeslots):

    for order_id in order_ids:
        logistics.add_order(order_id)

    for timeslot in timeslots:
        dt_start = datetime.strptime(timeslot["start"], "%Y-%m-%dT%H:%M")
        dt_end = datetime.strptime(timeslot["end"], "%Y-%m-%dT%H:%M")

        timeslot_data = {
            "logistics_id": logistics.id,
            "dt_range_start": dt_start,
            "dt_range_end": dt_end,
            "is_sched": False,
            "dt_sched_eta": None,
        }
        timeslot = Timeslots.insert(timeslot_data)

    status = Status()
    status.is_successful = True
    status.messages.append("Successfully scheduled your delivery!")
    return status
