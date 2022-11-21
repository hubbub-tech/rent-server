import os
from datetime import datetime

from src.utils.classes import DateGenerator

date_generator = DateGenerator()

class UtilsList:

    def __init__(self):
        pass


    @staticmethod
    def get_list_item_data():

        data = {
            "item": {
                "name": "Kusty Krab",
                "retailPrice": 200,
                "description": "They go straight to your hips."
            },
            "address": {
                "lat": 40.7274061,
                "lng": -74.00605,
                "formatted": "175 Varick St, New York, NY 10014, USA"
            },
            "calendar": {
                "dtStarted": None,
                "dtEnded": None
            },
            "tags": ["all"]
        }

        image_file = open("../../test_item_base64.txt", "r")
        image_base64s =  [image_file.read()]

        dt_start, dt_end = date_generator.generate_dt_range()

        ts_start = datetime.timestamp(dt_start)
        ts_end = datetime.timestamp(dt_end)

        data["dtStarted"] = ts_start
        data["dtEnded"] = ts_end
        data["imageBase64s"] = image_base64s
        return data
