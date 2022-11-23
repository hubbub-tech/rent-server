import json

class EmailTable:

    def __init__(self, rows: list, title: str=None):

        self.headers = None
        for row in rows:
            assert isinstance(row, EmailTableRow)

            if self.headers is None:
                self.headers = row.headers
                continue

            assert row.headers == self.headers, "Your rows must all be of the same type."

        self.rows = rows
        self.title = title


    def to_html(self):
        assert self.headers
        assert self.rows

        table_headers = []
        for header in self.headers:
            header_to_html = "<th>"
            header_to_html += str(header)
            header_to_html += "</th>"
            table_headers.append(header_to_html)

        table_rows = []
        for row in self.rows:

            row_data = []
            for element in row.data:
                data_to_html = "<td>"
                data_to_html += str(element)
                data_to_html += "</td>"
                row_data.append(data_to_html)

            row_to_html = "<tr>"
            row_to_html += "".join(row_data)
            row_to_html += "</tr>"
            table_rows.append(row_to_html)

        table_to_html = "<table>"
        table_to_html += "".join(table_headers)
        table_to_html += "".join(table_rows)
        table_to_html += "</table>"

        if self.title:
            title_to_html = f"<h3>{self.title}</h3>"
            table_to_html = title_to_html + table_to_html

        return table_to_html


class EmailTableRow:

    def __init__(self, data: dict):
        assert self.is_serializable(data)

        headers = list(data.keys())
        data = list(data.values())

        self.headers = headers
        self.data = data


    @staticmethod
    def is_serializable(data):
        try: json.dumps(data)
        except: return False
        else: return True
