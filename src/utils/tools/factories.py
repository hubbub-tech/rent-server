from src.models import Users
from src.models import Carts
from src.models import Items
from src.models import Calendars
from src.models import Addresses
from src.models import Logistics
from src.models import Reservations
from src.models import Orders
from src.models import Extensions
from src.models import Reviews
from src.models import Tags

from src.utils.classes import PriceCalculator
from src.utils.settings import DEPOSIT, TAX, DISCOUNT


def create_address(insert_data):
    address = Addresses.unique(insert_data)
    if address is None:
        address = Addresses.insert(insert_data)

    return address

def create_user(insert_data):
    new_user = Users.insert(insert_data["user"])

    insert_data["cart"]["id"] = new_user.id

    Carts.insert(insert_data["cart"])
    return new_user


def create_item(insert_data):
    new_item = Items.insert(insert_data["item"])

    lister = Users.get({"id": new_item.lister_id})
    lister.add_role(role="listers")

    insert_data["calendar"]["id"] = new_item.id

    Calendars.insert(insert_data["calendar"])

    for tag_title in insert_data["tags"]:
        tag = Tags.get({"title": tag_title})
        if tag is None:
            tag = Tags.insert({"title": tag_title})

        new_item.add_tag(tag)
    return new_item


def create_review(review_data):
    new_review = Reviews.insert(review_data)
    return new_review


def create_reservation(insert_data):
    item = Items.get({"id": insert_data["item_id"]})
    reservation = Reservations.unique(insert_data)

    if reservation is None:
        dt_ended = insert_data["dt_ended"]
        dt_started = insert_data["dt_started"]
        duration = (dt_ended - dt_started).days

        price_calculator = PriceCalculator()
        insert_data["est_charge"] = price_calculator.get_rental_cost(item.retail_price, duration)
        insert_data["est_deposit"] = insert_data["est_charge"] * DEPOSIT
        insert_data["est_tax"] = insert_data["est_charge"] * TAX

        reservation = Reservations.insert(insert_data)

    return reservation

def create_extension(insert_data):
    reservation_keys = {
        "dt_started": insert_data["res_dt_start"],
        "dt_ended": insert_data["res_dt_end"],
        "renter_id": insert_data["renter_id"],
        "item_id": insert_data["item_id"]
    }

    Reservations.set(reservation_keys, {"is_extension": True})
    new_extension = Extensions.insert(insert_data)

    return new_extension


def create_order(insert_data):
    new_order = Orders.insert(insert_data)

    renter = Users.get({ "id": new_order.renter_id })
    renter.add_role(role="renters")
    return new_order


def create_logistics(insert_data):
    logistics = Logistics.insert(insert_data)
    return logistics


def create_charge(charge_data):
    return None
