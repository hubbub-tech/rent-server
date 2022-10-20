from blubber_orm import Models

class Carts(Models):
    """
    A class to define the use of the Carts type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    table_name = "carts"
    table_primaries = ["id"]
    sensitive_attributes = ["checkout_session_key"]

    def __init__(self, attrs: dict):
        self.id = attrs["id"]
        self.total_charge = attrs["total_charge"]
        self.total_deposit = attrs["total_deposit"]
        self.total_tax = attrs["total_tax"]
        self.checkout_session_key = attrs["checkout_session_key"]


    def total(self):
        return self.total_charge + self.total_deposit + self.total_tax


    def get_item_ids(self, reserved_only: bool=False) -> list:

        if reserved_only:
            SQL = """
                SELECT item_id
                FROM reservations
                WHERE is_in_cart = %s AND renter_id = %s AND is_calendared = %s;
                """

            data = (True, self.id, False)

        else:
            SQL = """
                SELECT item_id
                FROM item_carts
                WHERE cart_id = %s;
                """

            data = (self.id, )

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)

            # list of tuples
            item_ids = cursor.fetchall()
            item_ids = [item_id for item_t in item_ids for item_id in item_t]


        return item_ids


    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation: Models):
        assert isinstance(reservation, Models), "reservation must be of type Models"
        assert reservation.table_name == "reservations", "Invalid Model type."

        cart_items = self.get_item_ids()
        if reservation.item_id not in cart_items: return

        SQL = """
            DELETE
            FROM item_carts
            WHERE cart_id = %s AND item_id = %s;
            """

        data = (self.id, reservation.item_id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)


        self.total_charge -= reservation.est_charge
        self.total_deposit -= reservation.est_deposit
        self.total_tax -= reservation.est_tax

        SQL = """
            UPDATE carts
            SET total_charge = %s, total_deposit = %s, total_tax = %s
            WHERE id = %s;
            """

        data = (self.total_charge, self.total_deposit, self.total_tax, self.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations
            SET is_in_cart = %s
            WHERE item_id = %s AND renter_id = %s AND dt_started = %s AND dt_ended = %s;
            """

        data = (
            False,
            reservation.item_id,
            reservation.renter_id,
            reservation.dt_started,
            reservation.dt_ended
        )

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()



    def add(self, reservation: Models):
        assert isinstance(reservation, Models), "reservation must be of type Models"
        assert reservation.table_name == "reservations", "Invalid Model type."

        reserved_cart_items = self.get_item_ids(reserved_only=True)
        assert reservation.item_id not in reserved_cart_items, "You can only have one of these items in cart"

        cart_items = self.get_item_ids(reserved_only=False)
        if reservation.item_id in cart_items:
            self.remove_without_reservation(reservation.item_id)

        SQL = """
            INSERT
            INTO item_carts (cart_id, item_id)
            VALUES (%s, %s);
            """

        data = (self.id, reservation.item_id) #sensitive to tuple order

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)

        self.total_charge += reservation.est_charge
        self.total_deposit += reservation.est_deposit
        self.total_tax += reservation.est_tax

        SQL = """
            UPDATE carts
            SET total_charge = %s, total_deposit = %s, total_tax = %s
            WHERE id = %s;
            """

        data = (self.total_charge, self.total_deposit, self.total_tax, self.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations
            SET is_in_cart = %s
            WHERE item_id = %s AND renter_id = %s AND dt_started = %s AND dt_ended = %s;
            """

        data = (
            True,
            reservation.item_id,
            reservation.renter_id,
            reservation.dt_started,
            reservation.dt_ended
        )

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()



    def remove_without_reservation(self, item: Models):
        """This resolves the non-commital 'add to cart' where the user didn't reserve."""

        assert isinstance(item, Models), "item must be of type Models"
        assert item.table_name == "items", "Invalid Model type."

        reserved_cart_items = self.get_item_ids(reserved_only=True)
        assert item.id not in reserved_cart_items, "Please use remove() to remove this item."

        cart_items = self.get_item_ids(reserved_only=False)
        if item.id not in cart_items: return # Fail silently

        SQL = """
            DELETE
            FROM item_carts
            WHERE cart_id = %s AND item_id = %s;
            """

        data = (self.id, item.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()


    #NOTE to add a reservation to this later, "remove_without_reservation()" then re-add with "add()"
    def add_without_reservation(self, item):
        """This is a non-commital add to cart where the user doesn't have to reserve immediately."""

        assert isinstance(item, Models), "item must be of type Models"
        assert item.table_name == "items", "Invalid Model type."

        cart_items = self.get_item_ids()
        if item.id in cart_items: return

        SQL = """
            INSERT
            INTO item_carts (cart_id, item_id)
            VALUES (%s, %s);
            """

        data = (self.id, item.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            Models.db.conn.commit()



    def contains(self, item):
        """Check if the cart contains this item."""

        SQL = """
            SELECT *
            FROM item_carts
            WHERE cart_id = %s AND item_id = %s;
            """
        data = (self.id, item.id)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            result = cursor.fetchone()

        return result is not None



    def __len__(self):
        SQL = """
            SELECT count(*)
            FROM item_carts
            WHERE cart_id = %s;
            """

        data = (self.id,)

        with Models.db.conn.cursor() as cursor:
            cursor.execute(SQL, data)
            result = cursor.fetchone()

            count = result[0]

        return count
