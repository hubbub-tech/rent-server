import requests


class Geocoder:
    """
    A class built on top of the geocoding services of a prominent mapping API.

    Instantiate this class then perform operations on addresses and have all your
    dreams come true.
    """

    def __init__(self, apikey, encoding_engine="here"):
        if encoding_engine == "here":
            self.url = "something"
        elif encoding_engine == "google":
            self.url = "something else"

        self.apikey = apikey


    # NOTE: find way to assert that it is an Addresses object while keeping decoupled
    def get_latlng(self, address):
        params = {
            "apikey": self.apikey,
            "address": address.to_http_format()
        }
        res = requests.get(self.url, params=params)
