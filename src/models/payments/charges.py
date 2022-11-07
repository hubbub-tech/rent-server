from blubber_orm import Models


class Charges(Models):

    table_name = "charges"
    table_primaries = ["id"]
    sensitive_attributes = []


    def __init__(self, attrs):
        self.id = attrs["id"]
        self.notes = attrs["notes"]
        self.amount = attrs["amount"]
        self.currency = attrs["currency"]
        self.txn_token = attrs["txn_token"]
        self.txn_processor = attrs["txn_processor"]
        self.is_paid = attrs["is_paid"]
        self.dt_created = attrs["dt_created"]
        self.order_id = attrs["order_id"]
        self.payee_id = attrs["payee_id"]
        self.payer_id = attrs["payer_id"]
        self.issue_id = attrs["issue_id"]
