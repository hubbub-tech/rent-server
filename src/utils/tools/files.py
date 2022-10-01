from datetime import datetime, date

from src.models import Items
from src.models import Users
from src.models import Addresses
from src.models import Logistics
from src.models import Reservations

from src.utils.settings import SMTP

def get_receipt(order):
    item = Items.get({"id": order.item_id})
    lister =  Users.get({"id": item.lister_id})

    reservation_pkeys = order.to_query_reservation()
    reservation = Reservations.get(reservation_pkeys)

    receipt_text = f"""
        Rental Invoice for {item.name}\n
        \n
        Hubbub Technologies, Inc\n
        {SMTP.DEFAULT_RECEIVER}\n\n
        \n
        Downloaded on {date.today().strftime('%Y-%m-%d')}\n
        Order Placed on {order.dt_placed.strftime('%Y-%m-%d')}\n
        \n
        Details regarding your rental of {item.name}:\n
        * Rental start date: {order.res_dt_start.strftime('%Y-%m-%d')}\n
        * Rental end date: {order.ext_dt_end.strftime('%Y-%m-%d')}\n
        \n
        * Item name: {item.name}\n
        * Item lister: {lister.name}\n
        * Rental cost: {reservation.est_charge}\n
        * Rental deposit: {reservation.est_deposit}\n
        * Tax: {reservation.est_tax}\n
        """

    dropoff_id = order.get_dropoff_id()
    pickup_id = order.get_pickup_id()

    if dropoff_id:
        dropoff = Logistics.get({"id": dropoff_id})

        to_addr_pkeys = dropoff.to_query_address("to")
        to_address = Addresses.get(to_addr_pkeys)

        if dropoff.dt_received:
            dropoff_text = f"""
                \n
                * Dropoff date: {dropoff.dt_received.strftime('%Y-%m-%d')}\n
                * Dropoff address: {to_address.formatted}\n
                """
        else:
            dropoff_text = "* Dropoff has been scheduled.\n"
    else:
        dropoff_text = "* Dropoff has not been scheduled.\n"

    if pickup_id:
        pickup = Logistics.get({"id": pickup_id})

        from_addr_pkeys = dropoff.to_query_address("from")
        from_address = Addresses.get(from_addr_pkeys)

        if pickup.dt_received:
            pickup_text = f"""
                \n
                * Pickup date: {pickup.dt_sent.strftime('%Y-%m-%d')}\n
                * Pickup address: {from_address.formatted}\n
                """
        else:
            pickup_text = "* Pickup has been scheduled.\n"
    else:
        pickup_text = "* Pickup has not been scheduled.\n"

    receipt_text += dropoff_text
    receipt_text += pickup_text

    return receipt_text
