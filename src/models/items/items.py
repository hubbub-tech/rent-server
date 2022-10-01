from blubber_orm import Models

class Items(Models):
    """
    A class to define the use of the Items type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "items"
    table_primaries = ["id"]
    sensitive_attributes = []

    def __init__(self, attrs: dict):
        self.id = attrs["id"]
        self.name = attrs["name"]
        self.manufacturer_id = attrs["manufacturer_id"]
        self.retail_price = attrs["retail_price"]
        self.is_visible = attrs["is_visible"]
        self.is_transactable = attrs["is_transactable"]
        self.is_featured = attrs["is_featured"]
        self.dt_created = attrs["dt_created"]
        self.is_locked = attrs["is_locked"]
        self.locker_id = attrs["locker_id"]
        self.description = attrs["description"]
        self.weight = attrs["weight"]
        self.weight_unit = attrs["weight_unit"]
        self.dim_height = attrs["dim_height"]
        self.dim_length = attrs["dim_length"]
        self.dim_width = attrs["dim_width"]
        self.dim_unit = attrs["dim_unit"]
        self.lister_id = attrs["lister_id"]

        self.address_lat = attrs["address_lat"]
        self.address_lng = attrs["address_lng"]


    def lock(self, user):
        SQL = """
            UPDATE items
            SET is_locked = %s, locker_id = %s
            WHERE id = %s;
            """

        data = (True, user.id, self.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()

        self.is_locked = True
        self.last_locked = user.id

    def unlock(self):
        SQL = """
            UPDATE items
            SET is_locked = %s, locker_id = %s
            WHERE id = %s;
            """

        data = (False, None, self.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()

        self.is_locked = False
        self.last_locked = None


    def get_tags(self):
        SQL = """
            SELECT title
            FROM item_tags
            WHERE item_id = %s;
            """

        data = (self.id,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            tags = cursor.fetchall()
            tags = [tag for tag_t in tags for tag in tag_t]

        return tags


    def add_tag(self, tag):
        SQL = """
            INSERT
            INTO item_tags (item_id, title)
            VALUES (%s, %s);
            """

        data = (self.id, tag.title)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()

    def remove_tag(self, tag):
        SQL = """
            DELETE
            FROM item_tags
            WHERE item_id = %s AND title = %s;
            """

        data = (self.id, tag.title)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    def to_query_address(self):
        query_address = {
            "lat": self.address_lat,
            "lng": self.address_lng
        }

        return query_address
