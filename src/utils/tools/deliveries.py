from datetime import datetime, date

from src.models import Timeslots
from src.models import Logistics
from src.utils.classes import Status

STORAGES = [
    (40.8001225, -73.9634888), # 108 W 107th St, New York, NY 10225
    (40.7274061, -74.00605), # 175 Varick St, New York, NY 10014
]

def attach_timeslots(order_ids: list, logistics: Logistics, timeslots: list, date_event: date):

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
    status.message = "Successfully attached timeslots to delivery."
    return status


def get_distance(coords_a, coords_b):
    ax, ay = coords_a
    bx, by = coords_b

    dist = ((ax - bx) ** 2 + (ay - by) ** 2) ** (1 / 2)
    return dist


def get_nearest_storage(coords):

    nearest_storage = (STORAGES[0])
    nearest_dist = float("inf")
    for storage_coords in STORAGES:

        curr_dist = get_distance(coords, storage_coords)
        if nearest_dist > curr_dist:
            nearest_dist = curr_dist
            nearest_storage = storage_coords

    return nearest_storage
