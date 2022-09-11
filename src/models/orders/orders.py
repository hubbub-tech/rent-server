from blubber_orm import Models


class Orders(Models):
    """
    A class to define the use of the Items type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "orders"
    table_primaries = ["id"]
    sensitive_attributes = []

    def __init__(self, attrs):
        self.id = attrs["id"]
        self.dt_placed = attrs["dt_placed"]
        self.is_canceled = attrs["is_canceled"]
        self.checkout_session_key = attrs["checkout_session_key"]
        self.referral = attrs["referral"]
        self.item_id = attrs["item_id"]
        self.renter_id = attrs["renter_id"]
        self.res_dt_start = attrs["res_dt_start"]
        self.res_dt_end = attrs["res_dt_end"]


    def get_extensions(self):
        "return structure: [(order_id, renter_id, item_id, res_dt_start, res_dt_end), ...]"

        SQL = """
            SELECT *
            FROM extensions
            WHERE order_id = %s
            """

        data = (self.id,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            extensions = cursor.fetchall()

        return extensions


    @property
    def ext_dt_start(self):
        """Get the start date of the order, extensions considered."""

        res_dt_start_index = -2
        res_dt_end_index = -1

        extensions = self.get_extensions()

        if extensions:
            extensions.sort(key = lambda ext: ext[res_dt_end_index])
            ext_dt_start = extensions[-1][res_dt_start_index]
        else:
            ext_dt_start = self.res_dt_start
        return ext_dt_start


    @property
    def ext_dt_end(self):
        """Get the true end date of the order, extensions considered."""

        res_dt_start_index = -2
        res_dt_end_index = -1

        extensions = self.get_extensions()

        if extensions:
            extensions.sort(key = lambda ext: ext[res_dt_end_index])
            ext_dt_end = extensions[-1][res_dt_end_index]
        else:
            ext_dt_end = self.res_dt_end
        return ext_dt_end



    def to_query_reservation(self):
        query_res = {
            "renter_id": self.renter_id,
            "item_id": self.item_id,
            "dt_started": self.res_dt_start,
            "dt_ended": self.res_dt_end
        }

        return query_res


    def get_dropoff_id(self):
        SQL = """
            SELECT logistics_id
            FROM order_logistics ol
            INNER JOIN logistics l
            ON ol.logistics_id = l.id
            WHERE ol.order_id = %s AND l.receiver_id = %s;
            """

        data = (self.id, self.renter_id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchone()


    def get_pickup_id(self):
        SQL = """
            SELECT logistics_id
            FROM order_logistics ol
            INNER JOIN logistics l
            ON ol.logistics_id = l.id
            WHERE ol.order_id = %s AND l.sender_id = %s;
            """

        data = (self.id, self.renter_id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchone()


    def get_promos(self):
        SQL = """
            SELECT title
            FROM order_promos
            WHERE order_id = %s;
            """

        data = (self.id,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            promos = cursor.fetchall()
            promos = [promo_title for promo_t in promos for promo_title in promo_t]
