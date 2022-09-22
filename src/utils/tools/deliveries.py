from datetime import datetime, date

from src.models import Timeslots
from src.models import Logistics
from src.utils.classes import Status

def schedule_deliveries(logistics: Logistics, order_ids: list, timeslots: list, date_event: date):

    for order_id in order_ids:
        logistics.add_order(order_id)

    for timeslot in timeslots:
        time_start = datetime.strptime(timeslot["start"], "%H:%M").time()
        time_end = datetime.strptime(timeslot["end"], "%H:%M").time()

        dt_start = datetime.combine(date_event, time_start)
        dt_end = datetime.combine(date_event, time_end)

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
