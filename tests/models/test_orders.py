import time
import random
import unittest
from blubber_orm import get_blubber

from src.models import Items
from src.models import Orders
from src.models import Extensions
from src.models import Reservations


class TestOrders(unittest.TestCase):

    def test_get_extensions(self):

        orders = Orders.get_all()
        order = random.choice(orders)

        extensions = order.get_extensions()
        is_list_type = extensions == []

        self.assertTrue(is_list_type)


    def test_ext_dt_end(self):

        res_dt_start_index = -2
        res_dt_end_index = -1

        extensions = Extensions.get_all()
        extension = random.choice(extensions)

        order = Orders.get({ "id": extension.order_id })
        extensions = order.get_extensions()

        extensions.sort(key = lambda ext: ext[res_dt_end_index])

        is_extended_dt_end = order.ext_dt_end == extensions[-1][res_dt_end_index]
        self.assertTrue(is_extended_dt_end)


    def test_ext_dt_start(self):

        res_dt_start_index = -2
        res_dt_end_index = -1

        extensions = Extensions.get_all()
        extension = random.choice(extensions)

        order = Orders.get({ "id": extension.order_id })
        extensions = order.get_extensions()

        extensions.sort(key = lambda ext: ext[res_dt_end_index])

        is_extended_dt_start = order.ext_dt_start == extensions[-1][res_dt_start_index]
        self.assertTrue(is_extended_dt_start)
