import unittest
from cron_parser import CronParser, CronParserException


class TestCronParser(unittest.TestCase):
    def setUp(self):
        """Initialize the CronParser instance for testing."""
        self.parser = CronParser()

    def test_valid_cron_expression(self):
        """Test a valid cron expression."""
        cron_expression = "*/15 0 1,15 * 1-5 /usr/bin/find"
        expected_output = {
            "minute": [0, 15, 30, 45],
            "hour": [0],
            "day of month": [1, 15],
            "month": list(range(1, 13)),
            "day of week": [1, 2, 3, 4, 5],
            "command": "/usr/bin/find"
        }
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result, expected_output)

    def test_valid_cron_expression_with_year(self):
        """Test a valid cron expression."""
        cron_expression = "*/15 0 1,15 * 1-5 2011,2012 /usr/bin/find -v"
        expected_output = {
            "minute": [0, 15, 30, 45],
            "hour": [0],
            "day of month": [1, 15],
            "month": list(range(1, 13)),
            "day of week": [1, 2, 3, 4, 5],
            "command": "/usr/bin/find -v",
            "year": [2011, 2012]
        }
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result, expected_output)

    def test_asterisk(self):
        """Test handling of '*' symbol."""
        cron_expression = "* * * * * /bin/echo"
        expected_output = {
            "minute": list(range(0, 60)),
            "hour": list(range(0, 24)),
            "day of month": list(range(1, 32)),
            "month": list(range(1, 13)),
            "day of week": list(range(0, 7)),
            "command": "/bin/echo"
        }
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result, expected_output)

    def test_special_cmd(self):
        """Test handling of '*' symbol."""
        cron_expression = "* * * * * /bin/echo -v"
        expected_output = {
            "minute": list(range(0, 60)),
            "hour": list(range(0, 24)),
            "day of month": list(range(1, 32)),
            "month": list(range(1, 13)),
            "day of week": list(range(0, 7)),
            "command": "/bin/echo -v"
        }
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result, expected_output)

    def test_invalid_field_count(self):
        """Test a cron expression with the wrong number of fields."""
        cron_expression = "* * * /usr/bin/find"
        with self.assertRaises(CronParserException) as context:
            self.parser.parse_cron_expression(cron_expression)
        self.assertIn("wrong data for cron parser", str(context.exception))

    def test_hyphen(self):
        """Test handling of '-' symbol."""
        cron_expression = "0-30/5 * * * * /usr/bin/find"
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result["minute"], [0, 5, 10, 15, 20, 25, 30])

    def test_comma(self):
        """Test handling of ',' symbol."""
        cron_expression = "0 0 1,15 * * /usr/bin/find"
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result["day of month"], [1, 15])

    def test_slash(self):
        """Test handling of '/' symbol."""
        cron_expression = "*/10 * * * * /usr/bin/find"
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result["minute"], [0, 10, 20, 30, 40, 50])

    def test_invalid_value(self):
        """Test a cron expression with an invalid value."""
        cron_expression = "70 * * * * /usr/bin/find"
        with self.assertRaises(ValueError):
            self.parser.parse_cron_expression(cron_expression)

    def test_command_only(self):
        """Test handling of just the command field."""
        cron_expression = "* * * * * /bin/echo"
        result = self.parser.parse_cron_expression(cron_expression)
        self.assertEqual(result["command"], "/bin/echo")

    def test_empty_expression(self):
        """Test empty cron expression."""
        cron_expression = ""
        with self.assertRaises(CronParserException):
            self.parser.parse_cron_expression(cron_expression)
