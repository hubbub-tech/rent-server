from datetime import datetime

from src.utils.classes import DateGenerator

date_generator = DateGenerator()

class UtilsCheckout:

    def __init__(self):
        pass


    @staticmethod
    def get_checkout_add_data(item_id, with_reservation=True):
        data = {
            "dtStarted": None,
            "dtEnded": None,
            "itemId": None
        }

        if with_reservation:
            dt_start, dt_end = date_generator.generate_dt_range()

            timestamp_start = datetime.timestamp(dt_start)
            timestamp_end = datetime.timestamp(dt_end)

            data["dtStarted"] = timestamp_start
            data["dtEnded"] = timestamp_end

        data["itemId"] = item_id
        return data


    @staticmethod
    def get_checkout_remove_data(item_id):
        return { "itemId": item_id }
