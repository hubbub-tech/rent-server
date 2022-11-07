import requests

class Geocoder:
    """
    A class built on top of the geocoding services of a prominent mapping API.

    Instantiate this class then perform operations on addresses and have all your
    dreams come true.
    """

    def __init__(self, apikey):
        self.geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        self.apikey = apikey


    def get_latlng(self, address):
        params = {
            "apikey": self.apikey,
            "address": address.to_http_format()
        }
        res = requests.get(self.geocode_url, params=params)
        data = res.json()

        lat = data["results"][0]["geometry"]["location"]["lat"]
        lng = data["results"][0]["geometry"]["location"]["lng"]
        return lat, lng


    def get_address(self, lat, lng):
        params = {
            "apikey": self.apikey,
            "latlng": f"{lat},{lng}"
        }
        res = requests.get(self.geocode_url, params=params)
        data = res.json()

        formatted_address = data["results"][0]["formatted_address"]
        return formatted_address


    def get_zip_code(self, lat, lng):
        params = {
            "apikey": self.apikey,
            "latlng": f"{lat},{lng}"
        }
        res = requests.get(self.geocode_url, params=params)
        data = res.json()

        results = data.get("results")
        if results:
            try:
                zip_code = results[0]["components"]["postal_code"]
            except:
                # LOGGING: record error
                zip_code = None
        else:
            zip_code = None
        return zip_code
