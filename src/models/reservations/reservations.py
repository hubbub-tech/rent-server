from blubber_orm import Models



class Reservations(Models):


    table_name = "reservations"
    table_primaries = ["item_id", "renter_id", "dt_started", "dt_ended"]
    sensitive_attributes = []

    def __init__(self, attrs):
        self.dt_started = attrs["dt_started"]
        self.dt_ended = attrs["dt_ended"]
        self.item_id = attrs["item_id"]
        self.renter_id = attrs["renter_id"]

        self.dt_created = attrs["dt_created"]
        self.est_charge = attrs["est_charge"]
        self.est_deposit = attrs["est_deposit"]
        self.est_tax = attrs["est_tax"]

        self.is_in_cart = attrs["is_in_cart"]
        self.is_extension = attrs["is_extension"]
        self.is_calendared = attrs["is_calendared"]


    def archive(self, notes=None):
        if self.is_calendared:
            if self.is_extension:
                SQL = """
                    SELECT order_id
                    FROM extensions
                    WHERE item_id = %s AND renter_id = %s AND res_dt_start = %s AND res_dt_end = %s
                    """
            else:
                SQL = """
                    SELECT id
                    FROM orders
                    WHERE item_id = %s AND renter_id = %s AND res_dt_start = %s AND res_dt_end = %s
                    """

            data = (self.item_id, self.renter_id, self.dt_started, self.dt_ended)

            with Models.db.conn.cursor() as cursor:
                cursor.execute(SQL, data)
                order_id = cursor.fetchone()

                if order_id: order_id = order_id[0]

            assert order_id, "Reservation is not pointing to an order."

            SQL = """
                INSERT
                INTO reservations_archived (item_id, renter_id, dt_started, dt_ended, order_id, notes)
                VALUES (%s, %s, %s, %s, %s, %s);
                """

            data = (self.item_id, self.renter_id, self.dt_started, self.dt_ended, order_id, notes)

            with Models.db.conn.cursor() as cursor:
                cursor.execute(SQL, data)
                Models.db.conn.commit()


    @property
    def is_archived(self):
        SQL = """
            SELECT *
            FROM reservations_archived
            WHERE renter_id = %s AND item_id = %s AND dt_started = %s AND dt_ended = %s;
            """

        data = (self.renter_id, self.item_id, self.dt_started, self.dt_ended)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchone() is not None


    def total(self):
        return self.est_charge + self.est_deposit + self.est_tax


    def __len__(self):
        return (self.dt_ended.date() - self.dt_started.date()).days
