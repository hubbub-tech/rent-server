from blubber_orm import Models

class Calendars(Models):
    """
    A class to define the use of the Calendars type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "calendars"
    table_primaries = ["id"]

    def __init__(self, attrs: dict):
        self.id = attrs["id"]
        self.dt_started = attrs["dt_started"]
        self.dt_ended = attrs["dt_ended"]


    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        SQL = """
            UPDATE reservations
            SET is_calendared = %s
            WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;
            """

        data = (
            False,
            reservation.item_id,
            reservation.renter_id,
            reservation.dt_started,
            reservation.dt_ended
        )

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.database.connection.commit()


    def add(self, reservation):
        SQL = """
            UPDATE reservations
            SET is_in_cart = %s, is_calendared = %s
            WHERE item_id = %s AND renter_id = %s AND dt_started = %s AND dt_ended = %s;
            """

        data = (
            False,
            True,
            reservation.item_id,
            reservation.renter_id,
            reservation.dt_started,
            reservation.dt_ended
        )

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.database.connection.commit()


    def get_reservations(dt_lbound=None, dt_ubound=None, descending=True):
        """Returns an array of tuples"""

        if dt_lbound is None: dt_lbound = self.dt_started
        elif dt_ubound is None: dt_ubound = self.dt_ended

        assert dt_lbound < dt_ubound, "Invalid bounds set."

        if descending: order_direction = 'DESC'
        else: order_direction = 'ASC'

        SQL = f"""
            SELECT (item_id, renter_id, dt_started, dt_ended)
            FROM reservations
            ORDER BY dt_started {order_direction}
            WHERE item_id = %s AND dt_started > %s AND dt_ended < %s;
            """

        data = (self.id, dt_lbound, dt_ubound)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            reservations_pkeys = cursor.fetchall()

        return reservations_pkeys
