from blubber_orm import Models
from datetime import datetime, timedelta

class Calendars(Models):
    """
    A class to define the use of the Calendars type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "calendars"
    table_primaries = ["id"]
    sensitive_attributes = []

    def __init__(self, attrs: dict):
        self.id = attrs["id"]
        self.dt_started = attrs["dt_started"]
        self.dt_ended = attrs["dt_ended"]


    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        SQL = """
            UPDATE reservations
            SET is_calendared = %s
            WHERE item_id = %s AND renter_id = %s AND dt_started = %s AND dt_ended = %s;
            """

        data = (
            False,
            reservation.item_id,
            reservation.renter_id,
            reservation.dt_started,
            reservation.dt_ended
        )

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


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

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def get_reservations(self, dt_lbound=None, dt_ubound=None, descending=True):
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
        if dt_ubound is None: dt_ubound = self.dt_ended

        assert dt_lbound < dt_ubound, "Invalid bounds set."

        if descending: order_direction = 'DESC'
        else: order_direction = 'ASC'

        SQL = f"""
            SELECT item_id, renter_id, dt_started, dt_ended
            FROM reservations
            WHERE item_id = %s AND dt_started >= %s AND dt_ended <= %s AND is_calendared = %s
            ORDER BY dt_started {order_direction};
            """

        data = (self.id, dt_lbound, dt_ubound, True)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            reservations_pkeys = cursor.fetchall()

        return reservations_pkeys


    #returns true if a reservation if valid, returns false if not, returns none if expired item
    def check_reservation(self, res_dt_start: datetime, res_dt_end: datetime, days_buffer=0, hours_buffer=0):
        dt_started_index = -2
        dt_ended_index = -1

        availabilities = self.get_availabilities(days_buffer=days_buffer, hours_buffer=hours_buffer)
        availabilities.sort(key = lambda avail: avail[dt_ended_index])

        for avail in availabilities:
            if avail[dt_started_index] <= res_dt_start:
                if res_dt_end <= avail[dt_ended_index]:
                    return True

        if self.dt_ended == datetime.now(): return None
        else: return False


    def best_match_reservation(self, res_dt_start: datetime, res_dt_end: datetime, days_buffer=0, hours_buffer=0):
        dt_started_index = -2
        dt_ended_index = -1

        availabilities = self.get_availabilities(days_buffer=days_buffer, hours_buffer=hours_buffer)
        availabilities.sort(key = lambda avail: avail[dt_ended_index])

        for avail in availabilities:
            if avail[dt_started_index] <= res_dt_start:
                if res_dt_end <= avail[dt_ended_index]:
                    return (res_dt_start, res_dt_end)
                elif res_dt_start < avail[dt_ended_index]:
                    return (res_dt_start, avail[dt_ended_index])
            elif avail[dt_started_index] < res_dt_end:
                if res_dt_end <= avail[dt_ended_index]:
                    return (avail[dt_started_index], res_dt_end)
                else:
                    return tuple(avail)

        return self.next_availability(days_buffer=0, hours_buffer=0)



    #determining if an item is available day-by-day
    def check_datetime(self, dt_comparison: datetime=datetime.now()):
        dt_started_index = -2
        dt_ended_index = -1

        reservations = self.get_reservations()
        res_count = len(reservations)

        if res_count > 0:
            for res in reservations:
                if res[dt_started_index] <= dt_comparison and \
                    dt_comparison <= res[dt_ended_index]:
                    return False
        return True


    def get_availabilities(self, days_buffer=0, hours_buffer=0):
        dt_started_index = -2
        dt_ended_index = -1

        td_buffer = timedelta(days=days_buffer, hours=hours_buffer)

        reservations = self.get_reservations()
        if reservations == []: return [(self.dt_started + td_buffer, self.dt_ended)]

        reservations.sort(key = lambda res: res[dt_ended_index])

        res_count = len(reservations)

        availabilities = []

        for i in range(res_count):
            if i + 1 == res_count and reservations[i][dt_ended_index] + td_buffer < self.dt_ended:
                availabilities.append((reservations[i][dt_ended_index] + td_buffer, self.dt_ended))
            elif i == 0 and self.dt_started + td_buffer < reservations[i][dt_started_index]:
                availabilities.append((self.dt_started + td_buffer, reservations[i][dt_started_index]))
            elif i + 1 < res_count:
                if reservations[i][dt_ended_index] + td_buffer < reservations[i + 1][dt_started_index]:
                    availabilities.append((reservations[i][dt_ended_index] + td_buffer, reservations[i + 1][dt_started_index]))
                # if equal, continue
                # if greater than, throw BIG error

        return availabilities


    def next_availability(self, days_buffer=0, hours_buffer=0):
        dt_started_index = -2
        dt_ended_index = -1

        closest_operating_datetime = datetime.now()

        availabilities = self.get_availabilities(days_buffer=days_buffer, hours_buffer=hours_buffer)
        availabilities.sort(key = lambda res: res[dt_ended_index])

        for avail in availabilities:
            if closest_operating_datetime <= avail[dt_started_index]:
                return avail
        # return (None, None)
        return availabilities[-1]


    def available_days_in_next(self, days):
        dt_started_index = -2
        dt_ended_index = -1

        dt_ubound = datetime.now() + timedelta(days=days)
        dt_lbound = datetime.now()

        reservations = self.get_reservations()
        available_days = 0

        dt_current = dt_lbound
        while dt_current < dt_ubound:
            is_available = self.check_datetime(dt_current)

            if is_available: available_days += 1

            dt_current += timedelta(days=1)

        return available_days






    def __len__(self):
        SQL = """
            SELECT count(*)
            FFROM reservations
            WHERE item_id = %s AND is_calendared = %s;
            """

        data = (self.id, True)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            result = cursor.fetchone()

        return result[0]
