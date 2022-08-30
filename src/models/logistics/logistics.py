from blubber_orm import Models
from datetime import datetime


class Logistics(Models):

    table_name = "logistics"
    table_primaries = ["id"]
    sensitive_attributes = []

    def __init__(self, attrs):
        self.id = attrs["id"]
        self.notes = attrs["notes"]
        self.is_canceled = attrs["is_canceled"]
        self.dt_created = attrs["dt_created"]

        self.dt_sent = attrs["dt_sent"]
        self.dt_received = attrs["dt_received"]

        self.sender_id = attrs["sender_id"]
        self.receiver_id = attrs["receiver_id"]
        self.courier_id = attrs["courier_id"]

        self.from_addr_line_1 = attrs["from_addr_line_1"]
        self.from_addr_line_2 = attrs["from_addr_line_2"]
        self.from_addr_country = attrs["from_addr_country"]
        self.from_addr_zip = attrs["from_addr_zip"]

        self.to_addr_line_1 = attrs["to_addr_line_1"]
        self.to_addr_line_2 = attrs["to_addr_line_2"]
        self.to_addr_country = attrs["to_addr_country"]
        self.to_addr_zip = attrs["to_addr_zip"]


    def to_query_address(self, direction):
        direction = direction.lower()
        assert direction in ["from", "to"], "Error: select a valid direction ['from', 'to']"

        if direction == "from":
            query_address = {
                "line_1": self.from_addr_line_1,
                "line_2": self.from_addr_line_2,
                "country": self.from_addr_country,
                "zip": self.from_addr_zip
            }
        elif direction == "to":
            query_address = {
                "line_1": self.to_addr_line_1,
                "line_2": self.to_addr_line_2,
                "country": self.to_addr_country,
                "zip": self.to_addr_zip
            }
        else: raise Exception("Error: Invalid logistics direction.")

        return query_address


    def get_order_ids(self):
        SQL = """
            SELECT order_id
            FROM order_logistics
            WHERE logistics_id = %s;
            """

        data = (self.id,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchall()


    def get_courier_ids(self):
        SQL = """
            SELECT courier_id
            FROM logistics_couriers
            WHERE logistics_id = %s;
            """

        data = (self.id,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchall()


    def confirm_sent(self):
        self.set({"id": self.id}, {
            "dt_sent": datetime.now()
        })


    def confirm_received(self):
        self.set({"id": self.id}, {
            "dt_received": datetime.now()
        })


    def get_timeslots(self):
        SQL = """
            SELECT (dt_range_start, dt_range_end)
            FROM timeslots
            WHERE logistics_id = %s;
            """

        data = (self.id,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchall()


    def get_eta(self):
        SQL = """
            SELECT (dt_range_start, dt_range_end)
            FROM timeslots
            WHERE logistics_id = %s AND is_sched = %s;
            """

        data = (self.id, True)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchone()


    def add_order(self, order_id: int):

        SQL = """
            INSERT
            INTO order_logistics (order_id, logistics_id)
            VALUES (%s, %s)
            """

        data = (order_id, self.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def remove_order(self, order_id: int):
        # We want both of these commands to succeed or fail together
        SQL = """
            DELETE
            FROM order_logistics
            WHERE order_id = %s AND logistics_id = %s;
            """
        data = (order_id, self.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def add_courier(self, courier_id: int):

        SQL = """
            INSERT
            INTO logistics_couriers (logistics_id, courier_id)
            VALUES (%s, %s)
            """

        data = (self.id, courier_id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def remove_courier(self, courier_id: int):
        # We want both of these commands to succeed or fail together
        SQL = """
            DELETE
            FROM logistics_couriers
            WHERE courier_id = %s AND logistics_id = %s;
            """
        data = (courier_id, self.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()
