import random
from datetime import datetime, timedelta

class DateGenerator:

    TD_WEEKS = 500
    DT_LBOUND = datetime.now()
    DT_UBOUND = DT_LBOUND + timedelta(weeks=TD_WEEKS)


    def __init__(self, dt_lbound=None, dt_ubound=None):
        if dt_lbound:
            self.dt_lbound = dt_lbound
        else:
            self.dt_lbound = DateGenerator.DT_LBOUND

        if dt_ubound:
            self.dt_ubound = dt_ubound
        else:
            self.dt_ubound = DateGenerator.DT_UBOUND


    def generate_dt_day(self, dt_start=None, dt_end=None):
        if dt_start is None:
            dt_start = self.dt_lbound

        if dt_end is None:
            dt_end = dt_start + timedelta(weeks=self.TD_WEEKS)
        elif dt_end < dt_start:
            dt_end = dt_start + timedelta(weeks=self.TD_WEEKS)

        td_difference = dt_end - dt_start
        td_days = td_difference.days

        random_number_of_days = random.randrange(td_days)
        return dt_start + timedelta(days=random_number_of_days)

    # Returns a tuple of random dates where start < end
    def generate_dt_range(self):
        dt_start = self.generate_dt_day()
        dt_end = self.generate_dt_day()

        while dt_end <= dt_start:
            dt_start, dt_end = self.generate_dt_range()
        return dt_start, dt_end
