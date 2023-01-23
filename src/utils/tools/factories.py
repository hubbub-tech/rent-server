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
from src.models import Issues

from src.utils.classes import PriceCalculator
from src.utils.settings import DEPOSIT, TAX, DISCOUNT


def create_address(insert_data: dict):
    address = Addresses.get({
        "lat": insert_data["lat"],
        "lng": insert_data["lng"]
    })
    if address is None:
        address = Addresses.insert(insert_data)

    return address

def create_user(insert_data: dict):
    new_user = Users.insert(insert_data)
    Carts.insert({ "id": new_user.id })

    new_user.add_role(role="renters")
    return new_user


def create_item(insert_data: dict, calendar_data: dict, tags: list):
    new_item = Items.insert(insert_data)

    calendar_data["id"] = new_item.id
    Calendars.insert(calendar_data)

    for tag_title in tags:
        tag = Tags.get({"title": tag_title})
        if tag is None:
            tag = Tags.insert({"title": tag_title})

        new_item.add_tag(tag)
    return new_item


def create_review(insert_data: dict):
    new_review = Reviews.insert(insert_data)
    return new_review


def create_reservation(insert_data: dict, strict_mode: bool=False):
    if insert_data["dt_started"] >= insert_data["dt_ended"]: return

    item = Items.get({"id": insert_data["item_id"]})
    reservation = Reservations.unique(insert_data)

    if strict_mode:
        reservation = Reservations.insert(insert_data)
        return reservation

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

def create_extension(insert_data: dict):
    reservation_keys = {
        "dt_started": insert_data["res_dt_start"],
        "dt_ended": insert_data["res_dt_end"],
        "renter_id": insert_data["renter_id"],
        "item_id": insert_data["item_id"]
    }

    Reservations.set(reservation_keys, {"is_extension": True})
    new_extension = Extensions.insert(insert_data)

    return new_extension


def create_order(insert_data: dict):
    new_order = Orders.insert(insert_data)

    renter = Users.get({ "id": new_order.renter_id })
    return new_order


def create_logistics(insert_data: dict):
    logistics = Logistics.unique(insert_data)
    if logistics is None:
        receiver = Users.get({ "id": insert_data["receiver_id"] })
        sender = Users.get({ "id": insert_data["sender_id"] })

        receiver.add_role(role="receivers")
        sender.add_role(role="senders")

        logistics = Logistics.insert(insert_data)
    print(logistics)
    return logistics


def create_issue(insert_data: dict):
    new_issue = Issues.insert(insert_data)
    return new_issue

def create_charge(insert_data: dict):
    return None
