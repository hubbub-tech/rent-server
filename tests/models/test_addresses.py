import random
import unittest
from blubber_orm import get_blubber

from src.models import Addresses

FAKE_LAT = 800
FAKE_LNG = -355
FAKE_FORMATTED = "123 Cherry Hill, Mount Olympus, Mars"


class TestAddresses(unittest.TestCase):

    def test_to_str(self):
        addresses = Addresses.get_all()
        address = random.choice(addresses)

        del addresses

        address_to_str = address.to_str()
        statement = isinstance(address_to_str, str)
        self.assertTrue(statement)


    def test_to_http_format(self):
        addresses = Addresses.get_all()
        address = random.choice(addresses)

        del addresses

        address_to_http_format = address.to_http_format()
        statement = ' ' not in address_to_http_format
        self.assertTrue(statement)


    def test_set_as_origin(self):

        address = Addresses.insert({
            "lat": FAKE_LAT,
            "lng": FAKE_LNG,
            "formatted": FAKE_FORMATTED
        })

        address.set_as_origin()

        blubber = get_blubber()

        SQL = "SELECT lat, lng FROM from_addresses WHERE lat = %s AND lng = %s;"
        data = (address.lat, address.lng)

        with blubber.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            statement = cursor.fetchone() is not None

        self.assertTrue(statement)

        Addresses.delete({ "lat": FAKE_LAT, "lng": FAKE_LNG })


    def test_set_as_destination(self):

        address = Addresses.insert({
            "lat": FAKE_LAT,
            "lng": FAKE_LNG,
            "formatted": FAKE_FORMATTED
        })

        address.set_as_destination()

        blubber = get_blubber()

        SQL = "SELECT lat, lng FROM to_addresses WHERE lat = %s AND lng = %s;"
        data = (address.lat, address.lng)

        with blubber.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            statement = cursor.fetchone() is not None

        self.assertTrue(statement)

        Addresses.delete({ "lat": FAKE_LAT, "lng": FAKE_LNG })
