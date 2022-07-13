from blubber_orm import Models

class Carts(Models):
    """
    A class to define the use of the Carts type from Hubbub Shop's relational database.
    Create, read, update, destroy have been implemented by the Models class.

    """

    def __init__(self, attrs: dict):
        self.id = attrs["id"]
        self.total_charge = attrs["total_charge"]
        self.total_deposit = attrs["total_deposit"]
        self.total_tax = attrs["total_tax"]


    def get_item_ids(reserved_only=False):

        if reserved_only:
            SQL = "SELECT item_id FROM reservations WHERE is_in_cart = %s AND renter_id = %s AND is_calendared = %s;"
            data = (True, self.id, False)

        else:
            SQL = "SELECT item_id FROM item_carts WHERE cart_id = %s;"
            data = (self.id, )

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            item_ids = cursor.fetchall()

        return item_ids


    #for remove() and add(), you need to pass the specific res, bc no way to tell otherwise
    def remove(self, reservation):
        #ASSERT reservation.item_id is associated with cart_id
        SQL = "DELETE FROM item_carts WHERE cart_id = %s AND item_id = %s;"
        data = (self.id, reservation.item_id)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)


        self.total_charge -= reservation.charge
        self.total_deposit -= reservation.deposit
        self.total_tax -= reservation.tax

        SQL = "UPDATE carts SET total_charge = %s, total_deposit = %s, total_tax = %s WHERE id = %s;"
        data = (self.total_charge, self.total_deposit, self.total_tax, self.id)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations SET is_in_cart = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (
            False,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended
        )

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)

            Models.database.connection.commit()



    def add(self, reservation):
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO item_carts (cart_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.id, reservation.item_id) #sensitive to tuple order

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)

        self.total_charge += reservation.charge
        self.total_deposit += reservation.deposit
        self.total_tax += reservation.tax

        SQL = "UPDATE carts SET total_charge = %s, total_deposit = %s, total_tax = %s WHERE id = %s;"
        data = (self.total_charge, self.total_deposit, self.total_tax, self.id)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)

        SQL = """
            UPDATE reservations SET is_in_cart = %s
                WHERE item_id = %s AND renter_id = %s AND date_started = %s AND date_ended = %s;"""
        data = (
            True,
            reservation.item_id,
            reservation.renter_id,
            reservation.date_started,
            reservation.date_ended
        )

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)

            Models.database.connection.commit()



    def remove_without_reservation(self, item):
        """This resolves the non-commital 'add to cart' where the user didn't reserve."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "DELETE FROM item_carts WHERE cart_id = %s AND item_id = %s;"
        data = (self.id, item.id)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)

            Models.database.connection.commit()


    #NOTE to add a reservation to this later, "remove_without_reservation()" then re-add with "add()"
    def add_without_reservation(self, item):
        """This is a non-commital add to cart where the user doesn't have to reserve immediately."""
        #ASSERT reservation.item_id is NOT associated with cart_id
        SQL = "INSERT INTO item_carts (cart_id, item_id) VALUES (%s, %s);" #does this return a tuple or single value?
        data = (self.id, item.id)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)

            Models.database.connection.commit()



    def contains(self, item):
        """Check if the cart contains this item."""

        SQL = f"SELECT * FROM item_carts WHERE cart_id = %s AND item_id = %s;"
        data = (self.id, item.id)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            result = Models.database.cursor.fetchone()

        return result is not None
