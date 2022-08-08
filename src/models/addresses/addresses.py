from blubber_orm import Models


class Addresses(Models):
    """
    A class to define the use of the Addresses type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "addresses"
    table_primaries = ["line_1", "line_2", "country", "zip"]

    def __init__(self, attrs):
        self.line_1 = attrs["line_1"]
        self.line_2 = attrs["line_2"]
        self.city = attrs["city"]
        self.state = attrs["state"]
        self.country = attrs["country"]
        self.zip = attrs["zip"]
        self.lat = attrs["lat"]
        self.lng = attrs["lng"]


    def to_str(self):
        return f"{self.line_1} {self.line_2} {self.city} {self.state} {self.country} {self.zip}"


    def to_http_format(self):
        address_str = self.to_str()
        address_http_formatted = address_str.replace(' ', '+')
        address_http_formatted = address_str.replace(',', '')
        return address_http_formatted
