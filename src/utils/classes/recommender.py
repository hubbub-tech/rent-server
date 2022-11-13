import random
from blubber_orm import get_blubber
from datetime import datetime

from src.models.reservations import Reservations
from src.models.items import Items
from src.models.items import Tags

class Recommender:

    MATCH_THRESHOLD = 70

    def __init__(self):
        pass


    def on(self, item):
        assert isinstance (item, Items), "Entry must be of model type: Items."
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


    def search_by_dates(self, dt_started: datetime=None, dt_ended: datetime=None, search_key: str=None):
        if dt_started is None: datetime.min
        if dt_ended is None: datetime.max

        assert isinstance(dt_started, datetime), "Must be of type datetime."
        assert isinstance(dt_ended, datetime), "Must be of type datetime."

        SQL = """
            WITH reserved_items (id) AS
            (
                SELECT r.item_id
                FROM reservations r
                INNER JOIN items i
                ON i.id = r.item_id
                WHERE r.is_calendared = %s AND r.dt_started >= %s AND r.dt_ended <= %s
            ),
            all_items (id) AS
            (
                SELECT id
                FROM items
            )
            SELECT id
            FROM all_items
            EXCEPT ALL
            SELECT id
            FROM reserved_items;
            """

        data = (True, dt_started, dt_ended)

        blubber = get_blubber()
        with blubber.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            item_ids = cursor.fetchall()
            item_ids = [item_id for item_t in item_ids for item_id in item_t]

        # if item_ids and search_key:
        #     conds = ",".join([f"({id})" for id in item_ids])
        #
        #     SQL = f"""
        #         WITH unreserved_items (id) AS
        #         (
        #             VALUES ({conds})
        #         )
        #         SELECT i.id
        #         FROM items i
        #         WHERE i.name ILIKE %s OR i.description ILIKE %s
        #         EXCEPT ALL
        #         SELECT id
        #         FROM unreserved_items;
        #         """
        #
        #     data = (f"%{search_key}%", f"%{search_key}%")
        #
        #     with blubber.conn.cursor() as cursor:
        #         cursor.execute(SQL, data)
        #         item_ids = cursor.fetchall()
        #         item_ids = [item_id for item_t in item_ids for item_id in item_t]
        print("check here")
        items = []
        for item_id in item_ids:
            item = Items.get({ "id": item_id })
            items.append(item)
        return items
