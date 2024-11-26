import sys
from typing import *

LENGTH_FIELDS = 6

TIME_RANGE_MAP = {
    "minute": [0, 59],
    "hour": [0, 23],
    "day of month": [1, 31],
    "month": [1, 12],
    "day of week": [0, 6]
}


class CronParserException(Exception):
    pass


class Symbol:
    ASTERISK = "*"
    HYPHEN = "-"
    COMMA = ","
    SLASH = "/"


class CronParser:
    def __init__(self):
        pass

    def parse_cron_expression(self, cron_exp_string: str) -> dict:
        fields = list(cron_exp_string.split())
        if len(fields) != LENGTH_FIELDS:
            raise CronParserException("wrong data for cron parser : " + cron_exp_string)

        fields_map = {
            "command": fields[5]
        }
        for i, (f_name, range_list) in enumerate(TIME_RANGE_MAP.items()):
            field_value = fields[i]
            fields_map[f_name] = self._get_data_with_symbol(field_value, *range_list)
            if not (range_list[0] <= min(fields_map[f_name]) and max(fields_map[f_name]) <= range_list[1]):
                raise ValueError
        return fields_map

    def _get_data_with_symbol(self, field: str, start: int, end: int) -> List[int]:
        if field == Symbol.ASTERISK:
            return CronParser.get_data_with_asterisk(start, end)
        if Symbol.COMMA in field:
            return CronParser.get_data_with_comma(field)
        if Symbol.HYPHEN in field and Symbol.SLASH in field:
            # Handle range with step, e.g., "0-30/5"
            range_part, step = field.split(Symbol.SLASH)
            range_values = self._get_data_with_symbol(range_part, start, end)
            step = int(step)
            return [x for x in range_values if (x - range_values[0]) % step == 0]
        if Symbol.HYPHEN in field:
            return CronParser.get_data_with_hyphen(field)
        if Symbol.SLASH in field:
            base, step = field.split(Symbol.SLASH)
            base_list = self._get_data_with_symbol(base, start, end)
            step_int = int(step)
            return [x for x in base_list if (x - start) % step_int == 0]

        return [int(field)]

    @staticmethod
    def get_data_with_asterisk(start: int, end: int) -> List[int]:
        return list(range(start, end + 1))

    @staticmethod
    def get_data_with_comma(field: str) -> List[int]:
        return sorted(set(int(v) for v in field.split(Symbol.COMMA)))

    @staticmethod
    def get_data_with_hyphen(field: str) -> List[int]:
        start, end = (int(v) for v in field.split(Symbol.HYPHEN))
        return list(range(start, end + 1))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Cron Parser Usage : ", sys.argv,  " ", len(sys.argv))
        sys.exit(1)
    cron_expression = sys.argv[1]
    try:
        parser = CronParser()
        result_map = parser.parse_cron_expression(cron_expression)
        command = result_map.pop("command")
        for field_name, values in result_map.items():
            print(f"{field_name.ljust(14)}{' '.join(map(str, values))}")
        print(f"command       {command}")

    except CronParserException as e:
        print(f"CronParserException Error: {e}")
    except Exception as ex:
        print(f"Exception Error: {ex}")
