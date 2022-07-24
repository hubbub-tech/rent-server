from blubber_orm import Models



class Reservations(Models):


    table_name = "reservations"
    table_primaries = ["item_id", "renter_id", "dt_started", "dt_ended"]

    def __init__(self, attrs):
        self.dt_started = attrs["dt_started"]
        self.dt_ended = attrs["dt_ended"]
        self.item_id = attrs["item_id"]
        self.renter_id = attrs["renter_id"]

        self.dt_created = attrs["dt_created"]
        self.charge = attrs["charge"]
        self.deposit = attrs["deposit"]
        self.tax = attrs["tax"]

        self.is_valid = attrs["is_valid"]
        self.is_in_cart = attrs["is_in_cart"]
        self.is_extension = attrs["is_extension"]
        self.is_calendared = attrs["is_calendared"]


    def get_last_version(self):
        SQL = """
            SELECT (next_item_id, next_renter_id, next_dt_start, next_dt_end)
            FROM res_history
            WHERE item_id = %s AND renter_id = %s AND dt_started = %s AND dt_ended = %s;
            """

        data = (self.item_id, self.renter_id, self.dt_started, self.dt_ended)

        with Models.database.connection.cursor() as cursor:
            cursor.execute(SQL, data)
            last_version_res = cursor.fetchall()


        item_id_index = 0
        renter_id_index = 1
        dt_started_index = 2
        dt_ended_index = 3

        if last_version_res:
            last_version_res_pkeys = {
                "item_id": last_version_res[item_id_index],
                "renter_id": last_version_res[renter_id_index],
                "dt_started": last_version_res[dt_started_index],
                "dt_ended": last_version_res[dt_ended_index],
            }

            # If the last version has been deleted, this should return 'None'
            last_version_res = Reservations.get(last_version_res_pkeys)

        return last_version_res


    @property
    def total(self):
        return self.charge + self.deposit + self.tax


    def __len__(self):
        return (self.dt_ended.date() - self.dt_started.date()).days
