import csv
from io import StringIO
from JedoxPy.Services.HeadersService import HeadersService


class CSVParser:

    @staticmethod
    def apply_types(rows, types_definition):
        for row in rows:
            for field, field_type in types_definition.items():
                if field in row and row[field] is not None:
                    row[field] = CSVParser.convert_type(row[field], field_type)
        return rows

    @staticmethod
    def convert_type(value, target_type):
        if target_type == "int":
            return int(value) if value.isdigit() else None
        elif target_type == "int_list":
            return [int(i) for i in value.split(",") if i.isdigit()]
        elif target_type == "list":
            return value.split(",")
        elif target_type == "bool":
            return bool(int(value))
        return value

    def parse(csv_data: str, header, service_method = None, payload = None):

        # clean the output
        csv_data = csv_data.rstrip(";")
        csv_data = "\n".join(line.rstrip(";") for line in csv_data.splitlines())

        f = StringIO(csv_data)
        if header:
            header_line = HeadersService().get_header(service_method, payload)
            reader = csv.DictReader(f, fieldnames=header_line, delimiter=";")

            rows = list(reader)

            types = HeadersService().get_types(service_method)

            if types is not None:
                types_definition = {key: type_ for item in types for key, type_ in item.items()}

                rows = CSVParser.apply_types(rows, types_definition)

        else:
            rows = list(csv.reader(f, delimiter=";"))

        if HeadersService().is_single_result(call_name=service_method) or service_method is None:
            return rows[0]

        return rows
