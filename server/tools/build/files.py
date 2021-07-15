from datetime import datetime, date
from blubber_orm import Items, Orders, Users, Reservations, Dropoffs, Pickups

def generate_receipt(order, filename):
    item = Items.get(order.item_id)
    user =  Users.get(order.lister_id)

    receipt_text = f"""
        Rental Invoice for {item.name}\n
        \n
        Hubbub Technologies, Inc\n
        hello@hubbub.shop\n\n
        \n
        Downloaded on {date.today().strftime('%Y-%m-%d')}\n
        Order Placed on {order.date_placed.strftime('%Y-%m-%d')}\n
        \n
        Details regarding your rental of {item.name}:\n
        * Rental start date: {order.res_date_start.strftime('%Y-%m-%d')}\n
        * Rental end date: {order.ext_date_start.strftime('%Y-%m-%d')}\n
        \n
        * Item name: {item.name}\n
        * Item lister: {user.name}\n
        * Rental cost: {order.reservation.print_charge()}\n
        * Rental deposit: {order.reservation.print_deposit()}\n
        * Tax: {order.reservation.print_tax()}\n
        """

    if order.is_dropoff_scheduled:
        dropoff = Dropoffs.by_order(order)
        dropoff_text = f"""
            \n
            * Dropoff date: {dropoff.dropoff_date.strftime('%Y-%m-%d')}\n
            * Dropoff address: {dropoff.logistics.address.display()}\n
            """
    else:
        dropoff_text = "* Dropoff has not been scheduled.\n"

    if order.is_pickup_scheduled:
        pickup = Pickups.by_order(order)
        pickup_text = f"""
            \n
            * Pickup date: {pickup.pickup_date.strftime('%Y-%m-%d')}\n
            * Pickup address: {pickup.logistics.address.display()}\n
            """
    else:
        pickup_text = "* Pickup has not been scheduled.\n"

    receipt_text += dropoff_text
    receipt_text += pickup_text

    receipt_file = open(f"server/temp/{filename}", 'w+')
    receipt_file.write(receipt_text)
    receipt_file.close()
    return filename
