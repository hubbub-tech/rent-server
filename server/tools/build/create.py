from datetime import datetime, date
from blubber_orm import Users, Profiles, Carts
from blubber_orm import Items, Details, Calendars, Tags
from blubber_orm import Addresses, Reservations
from blubber_orm import Orders, Extensions
from blubber_orm import Logistics, Dropoffs, Pickups

from werkzeug.security import check_password_hash, generate_password_hash

from server.tools.settings import exp_decay, generate_proposed_period
from server.tools.settings import DEPOSIT, TAX, DISCOUNT
#done
def create_user(insert_data):
    user_address = Addresses.filter(insert_data["address"])
    #NOTE: an empty list returns false not none
    if not user_address:
        user_address = Addresses.insert(insert_data["address"])

    new_user = Users.insert(insert_data["user"])

    insert_data["profile"]["id"] = new_user.id
    insert_data["cart"]["id"] = new_user.id

    Profiles.insert(insert_data["profile"])
    Carts.insert(insert_data["cart"])
    return new_user

#done
def create_item(insert_data):
    item_address = Addresses.filter(insert_data["address"])
    #NOTE: an empty list returns false not none
    if not item_address:
        item_address = Addresses.insert(insert_data["address"])

    new_item = Items.insert(insert_data["item"])
    #TODO: add tags to item after creation
    lister = Users.get(new_item.lister_id)
    lister.make_lister()
    insert_data["details"]["id"] = new_item.id
    insert_data["calendar"]["id"] = new_item.id

    Calendars.insert(insert_data["calendar"])
    Details.insert(insert_data["details"])

    for tag_name in insert_data["tags"]:
        tag = Tags.get(tag_name)
        if tag is None:
            tag = Tags.insert({"tag_name": tag_name})
        new_item.add_tag(tag)
    return new_item

def create_review(review_data):
    new_review = Reviews.insert(review_data)
    return new_review

def create_reservation(insert_data, discount=False):
    item = Items.get(insert_data["item_id"])
    _reservation = Reservations.filter(insert_data)
    if _reservation:
        reservation, = _reservation
    else:
        rental_duration = (insert_data["date_ended"] - insert_data["date_started"]).days
        insert_data["charge"] = exp_decay(item.price, rental_duration)
        insert_data["deposit"] = insert_data["charge"] * DEPOSIT
        insert_data["tax"] = insert_data["charge"] * TAX
        if discount:
            insert_data["charge"] *= (1 - DISCOUNT)
            insert_data["tax"] *= (1 - DISCOUNT)
        reservation = Reservations.insert(insert_data)

    #scheduler() checks if the res conflicts with other reservations
    is_valid_reservation = item.calendar.scheduler(reservation)

    if is_valid_reservation:
        action_message = "Great, the item is available! If it isn't in your cart already make sure you 'Add to Cart'!"
        waitlist_message = None
    else:
        #TODO: maybe delete the reservation if it isnt schedulable?
        #tells users when an item is available if the res conflicts
        reservation = None
        first_sentence = "The time you entered is already booked."
        action_message, waitlist_message = generate_proposed_period(item, first_sentence)

    return reservation, action_message, waitlist_message

def create_extension(insert_data):
    reservation_keys = {
        "date_started": insert_data["res_date_start"],
        "date_ended": insert_data["res_date_end"],
        "renter_id": insert_data["renter_id"],
        "item_id": insert_data["item_id"]
    }
    order = Orders.get(insert_data["order_id"])
    Reservations.set(reservation_keys, {"is_extended": True})
    new_extension = Extensions.insert(insert_data)

    pickup = Pickups.by_order(order)
    if pickup:
        pickup.cancel(order)
    return new_extension

def create_order(insert_data):
    new_order = Orders.insert(insert_data)
    renter = Users.get(new_order.renter_id)
    renter.make_renter()
    return new_order

def create_logistics(insert_data, orders, dropoff=None, pickup=None):
    logistics_address = Addresses.filter(insert_data["address"])
    #NOTE: an empty list returns false not none
    if not logistics_address:
        logistics_address = Addresses.insert(insert_data["address"])

    new_logistics = Logistics.insert(insert_data["logistics"])
    if dropoff:
        dropoff_data = {
            "dt_sched": new_logistics.dt_scheduled,
            "renter_id": new_logistics.renter_id,
            "dropoff_date": dropoff
        }
        new_dropoff_logistics = Dropoffs.insert(dropoff_data)
        new_dropoff_logistics.schedule_orders(orders)
        result = new_dropoff_logistics
    elif pickup:
        pickup_data = {
            "dt_sched": new_logistics.dt_scheduled,
            "renter_id": new_logistics.renter_id,
            "pickup_date": pickup
        }
        new_pickup_logistics = Pickups.insert(pickup_data)
        new_pickup_logistics.schedule_orders(orders)
        result = new_pickup_logistics
    else:
        Logistics.delete({
            "dt_sched": new_logistics.dt_scheduled,
            "renter_id": new_logistics.renter_id
        })
        result = None
    return result
