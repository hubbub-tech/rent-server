import random
import unittest
from collections import Counter
from blubber_orm import get_blubber

from src.utils.classes import DateGenerator

from src.models import Users
from src.models import Calendars
from src.models import Reservations


class TestCalendars(unittest.TestCase):

    def test_add(self):
        dt_started_index = 0
        dt_ended_index = 1

        calendars = Calendars.get_all()
        item_calendar = random.choice(calendars)

        del calendars

        users = Users.get_all()
        test_user = random.choice(users)

        del users

        self.test_get_availabilities()
        availabilities = item_calendar.get_availabilities()

        first_avail_range = availabilities[0]

        test_reservation_data = {
            "item_id": item_calendar.id,
            "dt_started": first_avail_range[dt_started_index],
            "dt_ended": first_avail_range[dt_ended_index],
            "renter_id": test_user.id
        }

        reservation = Reservations.insert(test_reservation_data)

        item_calendar.add(reservation)
        availabilities_tupled = item_calendar.get_availabilities()

        for avail in availabilities_tupled:

            same_dt_start = avail[dt_started_index] == reservation.dt_started
            same_dt_end = avail[dt_ended_index] == reservation.dt_ended

            self.assertFalse(same_dt_start and same_dt_end)

        item_calendar.remove(reservation)
        Reservations.delete(test_reservation_data)


    def test_remove(self):
        reservations = Reservations.get_all()
        reservation = random.choice(reservations)

        del reservations

        item_calendar = Calendars.get({ "id": reservation.item_id })

        item_calendar.remove(reservation)

        self.test_get_reservations()
        reservations_tupled = item_calendar.get_reservations()

        for res_tuple in reservations_tupled:

            res_data = {
                "item_id": res_tuple[0],
                "renter_id": res_tuple[1],
                "dt_started": res_tuple[2],
                "dt_ended": res_tuple[3]
            }

            sample = Reservations.get(res_data)

            self.assertFalse(reservation == sample)

        item_calendar.add(reservation)


    # NOTE: cannot have test dependencies
    def test_get_reservations(self):

        item_id_index = 0
        renter_id_index = 1
        dt_started_index = 2
        dt_ended_index = 3

        reservations_calendared = Reservations.filter({ "is_calendared": True })

        item_ids = []
        for res in reservations_calendared:
            item_ids.append(res.item_id)

        counter_item_ids = Counter(item_ids)

        # Counter.most_common() -> list[tuple]
        mode_item_id = counter_item_ids.most_common(1)[0][0]

        item_calendar = Calendars.get({ "id": mode_item_id })

        # Test for output
        reservations = item_calendar.get_reservations()
        is_type_list = isinstance(reservations, list)
        self.assertTrue(is_type_list)

        # Test for bounding
        with self.assertRaises(AssertionError):
            dt_failure_lbound = item_calendar.dt_ended
            dt_failure_ubound = item_calendar.dt_started

            item_calendar.get_reservations(
                dt_lbound=dt_failure_lbound,
                dt_ubound=dt_failure_ubound
            )

        # Test for overlaps
        i = 0
        prev_res = None
        reservations = item_calendar.get_reservations()
        while i < len(reservations):
            curr_res = reservations[i]

            if prev_res:
                no_overlaps = prev_res[dt_ended_index] <= curr_res[dt_started_index]
                self.assertTrue(no_overlaps)

            prev_res = curr_res
            i += 1

        # Test inputs
        reservations = item_calendar.get_reservations()
        if len(reservations) > 1:
            second_res = reservations[1]
            dt_lbound = second_res[dt_started_index]
            dt_ubound = second_res[dt_ended_index]

            reservations_lbounded = item_calendar.get_reservations(dt_lbound=dt_lbound)
            first_res = reservations_lbounded[0]

            is_lbounded = first_res[dt_started_index] == dt_lbound
            self.assertTrue(is_lbounded)

            reservations_ubounded = item_calendar.get_reservations(dt_ubound=dt_ubound)
            last_res = reservations_ubounded[-1]

            is_ubounded = last_res[dt_ended_index] == dt_ubound
            self.assertTrue(is_ubounded)

            reservations_asc = item_calendar.get_reservations() # defaults to descending=False
            is_ascending = reservations_asc[0][dt_started_index] < reservations_asc[1][dt_started_index]
            self.assertTrue(is_ascending)

            reservations_desc = item_calendar.get_reservations(descending=True)
            is_descending = reservations_desc[0][dt_started_index] > reservations_desc[1][dt_started_index]
            self.assertTrue(is_descending)
        else:
            raise Exception("Did not test get_reservation() params.")


    def test_check_reservation(self):

        dt_started_index = 0
        dt_ended_index = 1

        reservations = Reservations.filter({ "is_calendared": True })
        first_item_id = reservations[0].item_id

        item_calendar = Calendars.get({ "id": first_item_id })

        # Check for a known failure
        is_available = item_calendar.check_reservation(
            res_dt_start=reservations[0].dt_started,
            res_dt_end=reservations[0].dt_ended,
        )

        self.assertFalse(is_available)

        dt_generator = DateGenerator()
        dt_range = dt_generator.generate_dt_range()

        self.test_get_availabilities()
        availabilities = item_calendar.get_availabilities()

        # Check for known success
        if availabilities:
            test_avail = availabilities[0]

            is_available = item_calendar.check_reservation(
                res_dt_start=test_avail[dt_started_index],
                res_dt_end=test_avail[dt_ended_index],
            )

            self.assertTrue(is_available)



    def test_get_availabilities(self):

        dt_started_index = -2
        dt_ended_index = -1

        reservations = Reservations.get_all()
        reservation = random.choice(reservations)

        item_calendar = Calendars.get({ "id": reservation.item_id })

        self.test_get_reservations()
        reservations = item_calendar.get_reservations()

        availabilities = item_calendar.get_availabilities()

        total_calendar = reservations + availabilities
        total_calendar.sort(key = lambda dt_range: dt_range[dt_ended_index])

        prev_dt_range = None
        for curr_dt_range in total_calendar:
            if prev_dt_range:
                is_sequential = prev_dt_range[dt_ended_index] <= curr_dt_range[dt_started_index]
                self.assertTrue(is_sequential)

            prev_dt_range = curr_dt_range
            continue
