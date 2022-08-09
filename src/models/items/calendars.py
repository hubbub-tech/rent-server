from blubber_orm import Models
from datetime import datetime, timedelta

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
        """
        Returns an array of tuples.
        Structure:
            [(
                item_id,
                renter_id,
                dt_started,
                dt_ended
            ), ...]
        """

        if dt_lbound is None: dt_lbound = self.dt_started
        elif dt_ubound is None: dt_ubound = self.dt_ended

        assert dt_lbound < dt_ubound, "Invalid bounds set."

        if descending: order_direction = 'DESC'
        else: order_direction = 'ASC'

        SQL = f"""
            SELECT (item_id, renter_id, dt_started, dt_ended)
            FROM reservations
            ORDER BY dt_started {order_direction}
            WHERE item_id = %s AND dt_started >= %s AND dt_ended <= %s;
            """

        data = (self.id, dt_lbound, dt_ubound)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            reservations_pkeys = cursor.fetchall()

        return reservations_pkeys


    def __len__(self):
        SQL = """
            SELECT count(*)
            FFROM reservations
            WHERE item_id = %s AND is_calendared = %s;
            """

        data = (self.id, True)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            return cursor.fetchone()



    #determining if an item is available day-by-day
    def check_availability(self, dt_comparison=datetime.now()):
        dt_started_index = -2
        dt_ended_index = -1

        reservations = self.get_reservations()
        res_count = len(reservations)

        if res_count > 0:
            for res in reservations:
                if res[dt_started_index] <= dt_comparison and /
                    dt_comparison <= res[dt_ended_index]:
                    return False
        return True


    def get_availabilities(self):
        dt_started_index = -2
        dt_ended_index = -1

        reservations = self.get_reservations()
        if reservations == []: return [(self.dt_started, self.dt_ended)]

        reservations.sort(key = lambda res: res[dt_ended_index])

        res_count = len(reservations)

        availabilities = []

        for i in range(res_count):
            if i == 0 and self.dt_started < res[i][dt_started_index]:
                availabilities.append((self.dt_started, res[i][dt_started_index]))
            elif i + 1 < res_count:
                if res[i][dt_ended_index] < res[i + 1][dt_started_index]:
                    availabilities.append((res[i][dt_ended_index], res[i + 1][dt_started_index]))
                # if equal, continue
                # if greater than, throw BIG error
            elif i + 1 == res_count and res[i][dt_ended_index] < self.dt_ended:
                availabilities.append((res[i][dt_ended_index], self.dt_ended))

        return availabilities


    def next_availability(self, days_offset=0, mins_offset=0):
        dt_started_index = -2
        dt_ended_index = -1

        closest_operating_datetime = datetime.now() + timedelta(
            days=days_offset,
            minutes=mins_offset
        )

        availabilities = self.get_availabilities()
        availabilities.sort(key = lambda res: res[dt_ended_index])

        for avail in availabilities:
            if closest_operating_datetime <= avail[dt_started_index]:
                return avail
        return (None, None)


    #returns true if a reservation if valid, returns false if not, returns none if expired item
    def scheduler(self, res):
        dt_started_index = -2
        dt_ended_index = -1

        availabilities = self.get_availabilities()
        availabilities.sort(key = lambda res: res[dt_ended_index])

        for avail in availabilities:
            if avail[dt_started_index] <= res[dt_started_index]:
                if res[dt_ended_index] <= avail[dt_ended_index]:
                    return True

        if self.dt_ended == datetime.now(): return None
        else: return False
