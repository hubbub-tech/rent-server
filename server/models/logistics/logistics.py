from blubber_orm import Models
from datetime import datetime


class Logsitics(Models):

    table_name = "logistics"
    table_primaries = ["id"]

    def __init__(self, attrs):
        self.id = attrs["id"]
        self.notes = attrs["notes"]
        self.timeslots = attrs["timeslots"].split(",") # ?
        self.dt_created = attrs["dt_created"]

        self.date_sched = attrs["date_sched"]
        self.time_sched = attrs["time_sched"]

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


    def to_query_address(self, dir):
        dir = dir.lower()
        assert dir in ["from", "to"], "Error: select a valid direction ['from', 'to']"

        if dir == "from":
            query_address = {
                "line_1": self.from_addr_line_1,
                "line_2": self.from_addr_line_2,
                "country": self.from_addr_country,
                "zip": self.from_addr_zip
            }
        elif dir == "to":
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

        with Models.database.connection.cursor() as cursor:
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


    def cancel(self, order):
        SQL = """
            DELETE
            FROM order_logistics
            WHERE order_id = %s AND logistics_id = %s;
            """
        data = (order.id, self.id)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.database.connection.commit()
