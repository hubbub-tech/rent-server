from blubber_orm import Models

from src.utils.classes import Geocoder
from src.utils.settings import GOOGLE_MAPS_API


class Addresses(Models):
    """
    A class to define the use of the Addresses type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "addresses"
    table_primaries = ["lat", "lng"]
    sensitive_attributes = []

    def __init__(self, attrs):
        self.lat = attrs["lat"]
        self.lng = attrs["lng"]
        self.formatted = attrs["formatted"]
        self.description = attrs["description"]

        # Cached attributes
        self._zip_code = None


    def to_str(self):
        return self.formatted


    def to_http_format(self):
        address_str = self.to_str()
        address_http_formatted = address_str.replace(' ', '+')
        return address_http_formatted

    def set_as_origin(self):
        SQL = """
            SELECT lat, lng
            FROM from_addresses
            WHERE lat = %s AND lng = %s;
            """

        data = (self.lat, self.lng)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            address_pkeys = cursor.fetchone()

        if address_pkeys: return

        SQL = f"""
            INSERT
            INTO from_addresses (lat, lng)
            VALUES (%s, %s);
            """

        data = (self.lat, self.lng)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def set_as_destination(self):
        SQL = """
            SELECT lat, lng
            FROM to_addresses
            WHERE lat = %s AND lng = %s;
            """

        data = (self.lat, self.lng)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            address_pkeys = cursor.fetchone()

        if address_pkeys: return

        SQL = f"""
            INSERT
            INTO to_addresses (lat, lng)
            VALUES (%s, %s);
            """

        data = (self.lat, self.lng)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def get_zip_code(self):
        if self._zip_code is None:
            geocoder = Geocoder(apikey=GOOGLE_MAPS_API)
            self._zip_code = geocoder.get_zip_code(lat=self.lat, lng=self.lng)
        return self._zip_code
