from math import log, exp

class PriceCalculator:

    def exp_decay(retail_price, time_now, discount=.50, time_total=28):
        #Where discount is issued at time_total
        base_price = retail_price / 10
        if time_now > 180:
            time_total = 56
        compound = retail_price / 90
        a = compound * 10 ** (-log((1 - discount), 10) / (time_total - 1))
        r = 1 - (compound / a)
        y = a * (1 - r) ** time_now #per_day_price_now
        #calculate the cost of the rental to the user
        integ_time = y / log(1 - r)
        integ_0 = a * (1 - r) / log(1 - r)
        cost_to_date = base_price + integ_time - integ_0
        if cost_to_date < base_price:
            return base_price
        return cost_to_date
