from blubber_orm import Items, Orders, Addresses
from blubber_orm import Dropoffs, Pickups, Logistics

def complete_task(order, task, address=None):
    is_valid = False
    message = f"The task on order #{order.id} has failed."
    if isinstance(task, Dropoffs):
        order.complete_dropoff()
        Items.set(order.item_id, {
            "address_line_1": task.logistics.address.line_1,
            "address_line_2": task.logistics.address.line_2,
            "address_zip": task.logistics.address.zip_code
        })
        is_valid = True
        message = f"The dropoff on order #{order.id} has been completed."
    elif isinstance(task, Pickups):
        #TODO: to where the courier is taking it.
        if address:
            order.complete_pickup()
            Items.set(order.item_id, {
                "address_line_1": address.line_1,
                "address_line_2": address.line_2,
                "address_zip": address.zip_code
            })
            is_valid = True
            message = f"The task on order #{order.id} has been completed."
    else:
        raise Exception("The only valid task types are: 'Dropoffs' and 'Pickups'.")
    return {
        "is_valid": is_valid,
        "message": message
    }
