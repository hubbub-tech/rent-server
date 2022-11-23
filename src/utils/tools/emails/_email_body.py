class EmailBodyFormatter:

    def __init__(self):
        self.preview = None
        self.user = None
        self.introduction = None
        self.content = None
        self.conclusion = None
        self.optional = None

    def build(self):

        with open("src/templates/email.html", "r") as html:
            email_html = html.read()

            email_html_formatted = email_html.replace("{PREVIEW}", self.preview)
            email_html_formatted = email_html_formatted.replace("{USER}", self.user)

            email_html_formatted = email_html_formatted.replace("{INTRODUCTION}", self.introduction)
            email_html_formatted = email_html_formatted.replace("{CONTENT}", self.content)
            email_html_formatted = email_html_formatted.replace("{CONCLUSION}", self.conclusion)

            if self.optional:
                email_html_formatted = email_html_formatted.replace("{OPTIONAL}", self.optional)
            else:
                email_html_formatted = email_html_formatted.replace("{OPTIONAL}", "")

        return email_html_formatted

    def make_link(self, link, text):
        assert isinstance(link, str)
        assert isinstance(text, str)

        return f"<a href='{link}'>{text}</a>"



class EmailBodyMessenger:

    def __init__(self):
        self.subject = None
        self.to = None
        self.body = None
        self.error = None


    def to_dict(self):
        return self.__dict__




# --------------------


def get_logistics_table(date_str, item_names, timeslots):
    item_names_str = ", ".join(item_names)
    timeslots_str = ", ".join(timeslots)
    logistics_table = f"""
        <table>
            <tr>
                <th>Date</th>
                <th>Items</th>
                <th>Availability</th>
            </tr>
            <tr>
                <td>{date_str}</td>
                <td>{item_names_str}</td>
                <td>{timeslots_str}</td>
            </tr>
        </table>
            """
    return logistics_table

def get_receipt_table(transactions):
    total_cost = 0.0
    total_deposit = 0.0
    total_tax = 0.0
    receipt = """
        <table>
            <tr>
                <th>Item</th>
                <th>Start Rental</th>
                <th>End Rental</th>
                <th>Cost</th>
                <th>Safety Deposit</th>
                <th>Tax</th>
            </tr>
        """
    for transaction in transactions:
        item = transaction["item"]
        order = transaction["order"]
        reservation = transaction["reservation"]
        row = f"""
            <tr>
                <td>{item.name}</td>
                <td>{reservation.date_started.strftime('%B %-d, %Y')}</td>
                <td>{reservation.date_ended.strftime('%B %-d, %Y')}</td>
                <td>{reservation.print_charge()}</td>
                <td>{reservation.print_deposit()}</td>
                <td>{reservation.print_tax()}</td>
            </tr>
            """
        receipt += row
        total_cost += reservation._charge
        total_deposit += reservation._deposit
        total_tax += reservation._tax
    totals = f"""
        <tr>
            <td><strong>Totals</strong></td>
            <td></td>
            <td></td>
            <td><strong>${round(total_cost, 2)}</strong></td>
            <td><strong>${round(total_deposit, 2)}</strong></td>
            <td><strong>${round(total_tax, 2)}</strong></td>
        </tr>
        """
    receipt += totals + "</table>"
    return receipt

def get_active_orders_table(orders):
    active_orders_table = f"""
        <table>
            <tr>
                <th>Item</th>
                <th>End Date</th>
            </tr>
        """
    for order in orders:
        item = Items.get(order.item_id)
        link = f"https://www.hubbub.shop/inventory/i/id={item.id}"
        order_end_date_str = datetime.strftime(order.ext_date_end, "%B %-d, %Y")
        row = f"""
            <tr>
                <td><a href='{link}'>{item.name}</a></td>
                <td>{order_end_date_str}</td>
            </tr>
            """
        active_orders_table += row
    active_orders_table += "</table>"
    return active_orders_table

def get_task_update_table(task, chosen_time):
    task_date = datetime.strptime(task["task_date"], "%Y-%m-%d").date()
    task_date_str = datetime.strftime(task_date, "%B %-d, %Y")

    item_names = get_linkable_items(task)

    task_table = f"""
        <table>
            <tr>
                <td>{task['type'].capitalize()} Date</td>
                <td>{task_date_str}</td>
            </tr>
            <tr>
                <td>{task['type'].capitalize()} Time</td>
                <td>{chosen_time.strftime('%-I:%M %p')}</td>
            </tr>
            <tr>
                <td>{task['type'].capitalize()} Address</td>
                <td>{task['address']['formatted']}</td>
            </tr>
            <tr>
                <td>Item(s)</td>
                <td>{item_names}</td>
            </tr>
        </table>
        """
    return task_table

def get_cart_items(user):
    items = user.cart.contents
    cart_items_table = f"""
        <table>
            <tr>
                <th>Item</th>
            </tr>
        """
    for item in items:
        link = f"https://www.hubbub.shop/inventory/i/id={item.id}"
        row = f"""
            <tr>
                <td>
                    <a href='{link}'>{item.name}</a>
                </td>
            </tr>
            """
        cart_items_table += row
    cart_items_table += "</table>"
    return cart_items_table

def get_linkable_items(task):
    item_links =[]
    items = [order["item"] for order in task["orders"]]
    for item in items:
        link = f"https://www.hubbub.shop/inventory/i/id={item['id']}"
        item_links.append(f"<a href='{link}'>{item['name']}</a>")
    item_names = ", ".join(item_links)
    return item_names
