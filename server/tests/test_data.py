import blubber_orm.dev as dev
from blubber_orm import Users, Items, Reservations, Tags

from server.tools.build import create_user, create_item

def make_dummy_data():
    for i in range(50):
        #create dummy user data
        user_data = dev.generate_identity()
        new_user = create_user(user_data)

        #create dummy item data
        item_data = dev.generate_item()
        item_data["lister_id"] = new_user.id
        item_data["item"]["address_street"] = new_user.address.street
        item_data["item"]["address_num"] = new_user.address.num
        item_data["item"]["address_apt"] = new_user.address.apt
        item_data["item"]["address_zip"] = new_user.address.zip_code
        item_data["tags"] = ["all", "home"]
        item_data["is_listed_from_user_address"] = True
        new_item = create_item(item_data)
