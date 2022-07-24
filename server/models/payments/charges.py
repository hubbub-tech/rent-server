from blubber_orm import Models


class Charges(Models):

    table_name = "charges"
    table_primaries = ["id"]


    def __init__(self, attrs):
        self.id = attrs["id"]
        self.notes = attrs["notes"]
        self.amount = attrs["amount"]
        self.currency = attrs["currency"]
        self.payment_type = attrs["payment_type"]
        self.dt_created = attrs["dt_created"]
        self.order_id = attrs["order_id"]
        self.payee_id = attrs["payee_id"]
        self.payer_id = attrs["payer_id"]
        self.issue_id = attrs["issue_id"]
