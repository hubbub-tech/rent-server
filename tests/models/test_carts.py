import time
import random
import unittest
from blubber_orm import get_blubber

from src.models import Carts
from src.models import Items
from src.models import Reservations


class TestCarts(unittest.TestCase):

    def test_get_item_ids(self):

        carts = Carts.get_all()
        user_cart = random.choice(carts)

        item_ids = user_cart.get_item_ids()

        is_list_type = isinstance(item_ids, list)
        self.assertTrue(is_list_type)

        if item_ids:
            item_id = item_ids[0]
            is_int_type = isinstance(item_id, int)
            self.assertTrue(is_int_type)


    def test_remove(self):

        reservations = Reservations.filter({ "is_in_cart": True })
        reservation = random.choice(reservations)

        user_cart = Carts.get({ "id": reservation.renter_id })

        user_cart.remove(reservation)

        item_ids = user_cart.get_item_ids()
        is_removed = reservation.item_id not in item_ids

        self.assertTrue(is_removed)

        reservation = Reservations.get({
            "renter_id": reservation.renter_id,
            "item_id": reservation.item_id,
            "dt_started": reservation.dt_started,
            "dt_ended": reservation.dt_ended
        })

        self.assertFalse(reservation.is_in_cart)

        with self.assertRaises(AssertionError):
            user_cart.remove(reservation.item_id)

        user_cart.add(reservation)


    def test_add(self):

        reservations = Reservations.filter({ "is_in_cart": False })
        reservation = random.choice(reservations)

        user_cart = Carts.get({ "id": reservation.renter_id })

        reserved_item_ids = user_cart.get_item_ids(reserved_only=True)
        if reservation.item_id in reserved_item_ids:
            with self.assertRaises(AssertionError):
                user_cart.add(reservation)

        else:
            user_cart.add(reservation)

            reserved_item_ids = user_cart.get_item_ids(reserved_only=True)
            is_added = reservation.item_id in reserved_item_ids

            self.assertTrue(is_added)

            reservation = Reservations.get({
                "renter_id": reservation.renter_id,
                "item_id": reservation.item_id,
                "dt_started": reservation.dt_started,
                "dt_ended": reservation.dt_ended
            })

            self.assertTrue(reservation.is_in_cart)

            user_cart.remove(reservation)


        with self.assertRaises(AssertionError):
            user_cart.add(reservation.item_id)


    def test_add_with_reservation(self):

        carts = Carts.get_all()
        user_cart = random.choice(carts)

        items = Items.get_all()
        item = random.choice(items)

        cart_item_ids = user_cart.get_item_ids()
        while item.id in cart_item_ids:
            item = random.choice(items)

        user_cart.add_without_reservation(item)

        cart_item_ids = user_cart.get_item_ids()
        is_in_cart = item.id in cart_item_ids

        self.assertTrue(is_in_cart)

        _ = Reservations.unique({
            "is_in_cart": True,
            "renter_id": user_cart.id,
            "item_id": item.id
        })

        is_not_reserved = _ is None
        self.assertTrue(is_not_reserved)

        with self.assertRaises(AssertionError):
            user_cart.add_without_reservation(item.id)

        user_cart.remove_without_reservation(item)


    def test_remove_without_reservation(self):

        carts = Carts.get_all()
        cart_item_ids = []

        while cart_item_ids == []:
            user_cart = carts.pop()
            cart_item_ids = user_cart.get_item_ids()
            reserved_item_ids = user_cart.get_item_ids(reserved_only=True)

            if cart_item_ids == reserved_item_ids:
                cart_item_ids = []

            if carts == [] and cart_item_ids == []: return

        while True:
            item_id = cart_item_ids.pop()
            if item_id in reserved_item_ids: continue

            item = Items.get({ "id": item_id })

            user_cart.remove_without_reservation(item)

            cart_item_ids = user_cart.get_item_ids()
            is_removed = item_id not in cart_item_ids

            self.assertTrue(is_removed)

            with self.assertRaises(AssertionError):
                user_cart.remove_without_reservation(item.id)

            user_cart.add_without_reservation(item)
            break
