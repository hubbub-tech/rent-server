from blubber_orm import Models


class Addresses(Models):
    """
    A class to define the use of the Addresses type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "addresses"
    table_primaries = ["line_1", "line_2", "country", "zip"]
    sensitive_attributes = []

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

    def set_as_origin(self):
        SQL = """
            SELECT line_1, line_2, country, zip
            FROM from_addresses
            WHERE line_1 = %s AND line_2 = %s AND country = %s AND zip = %s;
            """

        data = (self.line_1, self.line_2, self.country, self.zip)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            address_pkeys = cursor.fetchone()

        if address_pkeys: return

        SQL = f"""
            INSERT
            INTO from_addresses (line_1, line_2, country, zip)
            VALUES (%s, %s, %s, %s);
            """

        data = (self.line_1, self.line_2, self.country, self.zip)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def set_as_destination(self):
        SQL = """
            SELECT line_1, line_2, country, zip
            FROM to_addresses
            WHERE line_1 = %s AND line_2 = %s AND country = %s AND zip = %s;
            """

        data = (self.line_1, self.line_2, self.country, self.zip)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            address_pkeys = cursor.fetchone()

        if address_pkeys: return

        SQL = f"""
            INSERT
            INTO to_addresses (line_1, line_2, country, zip)
            VALUES (%s, %s, %s, %s);
            """

        data = (self.line_1, self.line_2, self.country, self.zip)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()
