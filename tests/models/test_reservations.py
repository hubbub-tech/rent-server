import time
import random
import unittest
from blubber_orm import get_blubber

from src.models import ReservationsArchived
from src.models import Reservations


class TestReservations(unittest.TestCase):

    def test_archived(self):

        reservations = Reservations.filter({ "is_calendared": True })
        reservation = random.choice(reservations)

        reservation.archive()

        res_archived = ReservationsArchived.get({
            "renter_id": reservation.renter_id,
            "item_id": reservation.item_id,
            "dt_started": reservation.dt_started,
            "dt_ended": reservation.dt_ended
        })

        self.assertFalse(res_archived is None)

        is_archived_type = isinstance(res_archived, ReservationsArchived)
        self.assertEqual(is_archived_type)
