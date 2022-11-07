import time
import random
import unittest
from blubber_orm import get_blubber

from src.models import Logistics


class TestLogistics(unittest.TestCase):

    def test_get_order_ids(self):

        logistics_all = Logistics.get_all()
        logistics_unit = random.choice(logistics_all)

        order_ids = logistics_unit.get_order_ids()

        is_list_type = isinstance(order_ids, list)
        self.assertTrue(is_list_type)

        order_id = order_ids[0]
        is_int_type = isinstance(order_id, int)
        self.assertTrue(is_int_type)


    def test_get_courier_ids(self):

        logistics_all = Logistics.get_all()
        logistics_unit = random.choice(logistics_all)

        courier_ids = logistics_unit.get_courier_ids()

        is_list_type = isinstance(courier_ids, list)
        self.assertTrue(is_list_type)

        courier_id = courier_ids[0]
        is_int_type = isinstance(courier_id, int)
        self.assertTrue(is_int_type)


    def test_get_timeslots(self):

        logistics_all = Logistics.get_all()
        logistics_unit = random.choice(logistics_all)

        timeslots = logistics_unit.get_timeslots()

        is_list_type = isinstance(timeslots, list)
        self.assertTrue(is_list_type)


    def test_remove_courier(self):

        logistics_all = Logistics.get_all()
        logistics_unit = random.choice(logistics_all)

        self.test_get_courier_ids()
        courier_ids = logistics_unit.get_courier_ids()
        courier_id = courier_ids[0]

        # It does not accept Models objects, only
        logistics_unit.remove_courier(courier_id)

        courier_ids = logistics_unit.get_courier_ids()

        is_removed = courier_id not in courier_ids

        self.assertTrue(is_removed)


    def test_add_courier(self):

        logistics_all = Logistics.get_all()
        logistics_unit = random.choice(logistics_all)
