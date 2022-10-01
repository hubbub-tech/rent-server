from math import log

class PriceCalculator:

    def __init__(self, discount_rate=.50, days_to_floor=28):
        self.base_percent = 10
        self.discount_rate = discount_rate
        self.days_to_floor = days_to_floor


    def get_rental_cost(self, retail_price, duration):
        """
        An exponential decay function for per-day cost, integrated over rental duration.

        base price -> minimum amount that we want a rental to cost.
        compound price -> distance between base price and retail price.

        The pricing function describes the rate at which the rental cost approaches retail price.

        Per-day cost is modeled on an exponential decay function. If the points on the curve are
        the cost per-day, then the area under the curve is the cost over the duration.

        To calculate rental cost, we integrate the exponential function y = a * (1 - r) ^ x.

        'days_to_floor' and 'discount_rate' affect the pace of the decay--tweak these to change
        the rate at which rental cost approaches retail price.

        """

        base_price = retail_price / self.base_percent
        compound_price = retail_price / (100 - self.base_percent)

        if duration > 180: self.days_to_floor *= 2

        a = compound_price * 10 ** (-log((1 - self.discount_rate), 10) / (self.days_to_floor - 1))
        r = 1 - (compound_price / a)

        # Exponential Growth function: y = a * (1 - r) ^ x
        y = a * (1 - r) ** duration #per_day_price_now

        # Integrate over the rental duration
        integ_time = y / log(1 - r)
        integ_0 = a * (1 - r) / log(1 - r)

        # Get cost of the rental over duration
        cost_to_date = base_price + integ_time - integ_0

        if cost_to_date < base_price: return base_price

        return cost_to_date
