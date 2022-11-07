import random

from src.models import Items
from src.models import Tags

class Recommender:

    def __init__(self):
        pass


    def on(self, item):
        # Split the item name by spaces
        search_tokens = item.name.split(" ")

        # Take the last word in the name--this is likely to be an identifier as to what it is
        last_token = search_tokens[-1]

        items_by_name = Items.like("name", last_token)
        items_by_description = Items.like("description", last_token)
        unfiltered_items = items_by_name + items_by_description

        memo = []
        filtered_items = []
        for item in unfiltered_items:
            if (item.is_visible and item.is_transactable) and item.id not in memo:
                memo.append(item.id)
                filtered_items.append(item)

        # get recommendations
        size = 3
        recommendations = []
        if len(filtered_items) > size:
            recommendations = random.sample(filtered_items, size)
        else:
            recommendations = filtered_items
        return recommendations


    def search_for(self, search_key):
        if search_key == 'all':
            searched_items = Items.filter({"is_transactable": True, "is_visible": True})
            return searched_items

        tags = Tags.like("title", search_key)

        unfiltered_item_ids = []
        for tag in tags:
            unfiltered_item_ids += tag.get_item_ids()

        # search by item details description
        items_by_name = Items.like("name", search_key)
        items_by_description = Items.like("description", search_key)

        unfiltered_item_ids += [item.id for item in items_by_name]
        unfiltered_item_ids += [item.id for item in items_by_description]

        # remove duplicates
        memo = []
        filtered_items = []
        for item_id in unfiltered_item_ids:
            if item_id not in memo:
                memo.append(item_id)
                item = Items.get({"id": item_id})

                if item.is_transactable and item.is_visible:
                    filtered_items.append(item)
        return filtered_items
