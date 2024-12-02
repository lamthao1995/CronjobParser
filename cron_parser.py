import sys
from typing import *

AT_LEAST_LENGTH_FIELDS = 6
CMD_INDEX = 5

TIME_RANGE_MAP = {
    "minute": [0, 59],
    "hour": [0, 23],
    "day of month": [1, 31],
    "month": [1, 12],
    "day of week": [0, 6],
    "year": [1, 9999]
}


class CronParserException(Exception):
    """
    Custom exception class for handling errors related to cron expression parsing.
    """
    pass


class Symbol:
    """
    Class to hold special symbols used in crontab expressions.
    """
    ASTERISK = "*"
    HYPHEN = "-"
    COMMA = ","
    SLASH = "/"


class CronParser:
    """
    A class to parse and validate crontab expressions.
    """
    def __init__(self):
        pass

    def _get_cmd(self, fields: List[str], is_year_part_exist: bool):
        idx = CMD_INDEX + (1 if is_year_part_exist else 0)
        return " ".join(fields[idx:])

    def is_year_part_exist(self, fields):
        if fields[CMD_INDEX][0] == Symbol.SLASH:
            return False
        return True

    def parse_cron_expression(self, cron_exp_string: str) -> dict:
        """
        Parses a crontab expression and returns a dictionary with the parsed fields.

        :param cron_exp_string: The crontab expression string (e.g., "*/5 0-23 * * * /command").
        :return: A dictionary with parsed fields as keys and their respective values as lists.
        :raises CronParserException: If the number of fields is incorrect.
        :raises ValueError: If a field contains values outside its valid range.
        """
        fields = list(cron_exp_string.split())
        if len(fields) < AT_LEAST_LENGTH_FIELDS:
            raise CronParserException("wrong data for cron parser : " + cron_exp_string)
        is_year_exist = self.is_year_part_exist(fields)
        fields_map = {
            "command": self._get_cmd(fields, is_year_exist)
        }


     #   print("data and is_year_exist ", is_year_exist, fields[CMD_INDEX])

        for i, (f_name, range_list) in enumerate(TIME_RANGE_MAP.items()):
            if not is_year_exist and i == len(TIME_RANGE_MAP) - 1:
                break
            field_value = fields[i]
            fields_map[f_name] = self._get_data_with_symbol(field_value, *range_list)
          #  print(field_value, fields_map, range_list)
            if not (range_list[0] <= min(fields_map[f_name]) and max(fields_map[f_name]) <= range_list[1]):
                raise ValueError
        return fields_map

    def _get_data_with_symbol(self, field: str, start: int, end: int) -> List[int]:
        """
        Processes a crontab field containing special symbols and returns the resolved values.

        :param field: The crontab field string (e.g., "*/5", "1,2,3", "0-10").
        :param start: The start of the valid range for the field.
        :param end: The end of the valid range for the field.
        :return: A list of integers representing the resolved values for the field.
        """
        if field == Symbol.ASTERISK:
            return CronParser.get_data_with_asterisk(start, end)
        if Symbol.COMMA and (Symbol.SLASH in field or Symbol.HYPHEN in field):
            parts = field.split(Symbol.COMMA)
            result = []

            for part in parts:
                if Symbol.HYPHEN in part and Symbol.SLASH in part:
                    range_part, step = part.split(Symbol.SLASH)
                    range_values = self._get_data_with_symbol(range_part, start, end)
                    step = int(step)
                    result.extend([x for x in range_values if (x - range_values[0]) % step == 0])

                elif Symbol.SLASH in part:
                    range_part, step = part.split(Symbol.SLASH)
                    range_values = self._get_data_with_symbol(range_part, start, end)
                    step = int(step)
                    result.extend([x for x in range_values if (x - range_values[0]) % step == 0])

                elif Symbol.HYPHEN in part:
                    result.extend(CronParser.get_data_with_hyphen(part))
                else:
                    result.append(int(part))
            return result

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
        """
        Resolves an asterisk (*) to a range of integers.

        :param start: The start of the range.
        :param end: The end of the range.
        :return: A list of integers representing all values in the range.
        """
        return list(range(start, end + 1))

    @staticmethod
    def get_data_with_comma(field: str) -> List[int]:
        """
        Resolves a comma-separated list to individual integers.

        :param field: The crontab field string containing comma-separated values (e.g., "1,2,3").
        :return: A sorted list of integers without duplicates.
        """
        return sorted(set(int(v) for v in field.split(Symbol.COMMA)))

    @staticmethod
    def get_data_with_hyphen(field: str) -> List[int]:
        """
        Resolves a hyphen-separated range to individual integers.

        :param field: The crontab field string containing a range (e.g., "1-5").
        :return: A list of integers representing the range.
        """
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
