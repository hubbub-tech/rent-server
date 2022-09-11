from blubber_orm import Models

class Tags(Models):

    table_name = "tags"
    table_primaries = ["title"]
    sensitive_attributes = []

    def __init__(self, attrs):
        self.title = attrs["title"]


    def get_item_ids(self):
        SQL = """
            SELECT item_id
            FROM item_tags
            WHERE title = %s;
            """

        data = (self.title,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            item_ids = cursor.fetchall()
            item_ids = [item_id for item_t in item_ids for item_id in item_t]

        return item_ids
