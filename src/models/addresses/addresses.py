from blubber_orm import Models


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
