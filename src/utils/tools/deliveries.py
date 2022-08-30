from src.models import Timeslots

def schedule_deliveries(logistics, order_ids, timeslots):

    for order_id in order_ids:
        logistics.add_order(order_id)

    for dt_start, dt_end in timeslots:
        timeslot_data = {
            "logistics_id": logistics.id,
            "dt_range_start": dt_start,
            "dt_range_end": dt_end,
            "is_sched": False,
            "dt_sched_eta": None,
        }
        timeslot = Timeslots.insert(timeslot_data)
