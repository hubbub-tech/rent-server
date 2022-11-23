import time
import random
import unittest
from blubber_orm import get_blubber

from src.models import Items
from src.models import Users
from src.models import Tags


class TestItems(unittest.TestCase):

    def test_lock(self):
        items = Items.get_all()
        item = random.choice(items)

        del items

        users = Users.get_all()
        user = random.choice(users)

        del users


        with self.assertRaises(AssertionError):
            item.lock(user.id)

        item.lock(user)

        item_is_locked = item.is_locked
        item_is_locked_by_user = user.id == item.locker_id

        self.assertTrue(item_is_locked)
        self.assertTrue(item_is_locked_by_user)

        self.test_unlock()
        item.unlock()



    def test_unlock(self):
        items = Items.get_all()
        item = random.choice(items)

        del items

        users = Users.get_all()
        user = random.choice(users)

        del users

        item.lock(user)
        item.unlock()

        item_is_locked = item.is_locked
        item_is_locked_by_user = user.id == item.locker_id

        self.assertFalse(item_is_locked)
        self.assertFalse(item_is_locked_by_user)

        item.unlock()
        item_is_locked = item.is_locked
        item_is_locked_by_user = user.id == item.locker_id

        self.assertFalse(item_is_locked)
        self.assertFalse(item_is_locked_by_user)



    def test_get_tags(self):

        has_no_tags = True
        items = Items.get_all()

        time_start = time.time()
        while has_no_tags == True:
            item = random.choice(items)
            tag_titles = item.get_tags()

            time_elapsed = time.time() - time_start
            if tag_titles == []: continue
            if time_elapsed > 60: break
            has_no_tags = False
            del items

            for tag_title in tag_titles:
                is_type_str = isinstance(tag_title, str)
                self.assertTrue(is_type_str)


    def test_add_tag(self):
        items = Items.get_all()
        item = random.choice(items)

        del items

        self.test_remove_tag()
        tag_titles = item.get_tags()

        if tag_titles:
            tag_title = tag_titles[0]
            tag_to_add = Tags.get({ "title": tag_title })
            item.remove_tag(tag_to_add)

            item.add_tag(tag_to_add)

            tag_titles = item.get_tags()
            is_added = tag_to_add.title in tag_titles
            self.assertTrue(is_added)
        else:
            tags = Tags.get_all()
            tag_to_add = random.choice(tags)

            item.add_tag(tag_to_add)

            tag_titles = item.get_tags()
            is_added = tag_to_add.title in tag_titles
            self.assertTrue(is_added)

            item.remove_tag(tag_to_add)



    def test_remove_tag(self):
        items = Items.get_all()
        item = random.choice(items)

        del items

        tag_titles = item.get_tags()
        if tag_titles:
            tag_title = tag_titles[0]
            tag_to_remove = Tags.get({ "title": tag_title })
            item.remove_tag(tag_to_remove)

            tag_titles = item.get_tags()
            is_removed = tag_to_remove.title not in tag_titles
            self.assertTrue(is_removed)

            item.add_tag(tag_to_remove)



    def test_to_query_address(self):
        items = Items.get_all()
        item = random.choice(items)

        del items

        item_address_data = item.to_query_address()
        is_type_dict = isinstance(item_address_data, dict)

        self.assertTrue(is_type_dict)

        self.assertTrue("lat" in item_address_data.keys())
        self.assertTrue("lng" in item_address_data.keys())
