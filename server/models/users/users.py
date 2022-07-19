import copy
from blubber_orm import Models

class Users(Models):
    """
    A class to define the use of the Users type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "users"
    table_primaries = ["id"]

    def __init__(self, attrs: dict):
        self.id = attrs["id"]
        self.name = attrs["name"]
        self.phone = attrs["phone"]
        self.email = attrs["email"]
        self.bio = attrs["bio"]
        self.profile_pic = attrs["profile_pic"]
        self.dt_joined = attrs["dt_joined"]
        self.dt_last_active = attrs["dt_last_active"]
        self.is_blocked = attrs["is_blocked"]
        self.session_key = attrs["session_key"]

        self.address_line_1 = attrs["address_line_1"]
        self.address_line_2 = attrs["address_line_2"]
        self.address_city = attrs["address_city"]
        self.address_country = attrs["address_country"]
        self.address_zip = attrs["address_zip"]

        self._password = attrs.get("password")


    @classmethod
    def get_all(cls, role=None):
        if role is None: return super().get_all()

        valid_roles = ["payees", "payers", "couriers", "renters", "listers"]
        assert role in valid_roles

        SQL = f"""
            SELECT *
            FROM {role};
            """

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL)
            user_tuples = cursor.fetchall()
            user_tuples = copy.deepcopy(user_ids)

            users = []
            for user_t in user_tuples:
                id, *_ = user_t
                user = Users.get({"id": id})
                users.append(user)
        return users
