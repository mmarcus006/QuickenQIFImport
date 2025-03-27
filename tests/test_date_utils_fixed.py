import unittest
from datetime import datetime
from src.quickenqifimport.utils.date_utils import DateUtils


class TestDateUtils(unittest.TestCase):
    """Test cases for date_utils module."""
    
    def test_parse_date_valid_formats(self):
        """Test parsing dates in various formats."""
        test_cases = [
            ("01/15/23", datetime(2023, 1, 15)),
            ("01/15/2023", datetime(2023, 1, 15)),
            ("15/01/23", datetime(2023, 1, 15)),
            ("15/01/2023", datetime(2023, 1, 15)),
            ("2023-01-15", datetime(2023, 1, 15))
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = DateUtils.parse_date(date_str)
                self.assertEqual(result, expected)
    
    def test_parse_date_with_custom_formats(self):
        """Test parsing dates with custom formats."""
        custom_formats = ["%d-%b-%Y", "%b %d, %Y", "%B %d, %Y", "%Y.%m.%d"]
        test_cases = [
            ("15-Jan-2023", datetime(2023, 1, 15)),
            ("Jan 15, 2023", datetime(2023, 1, 15)),
            ("January 15, 2023", datetime(2023, 1, 15)),
            ("2023.01.15", datetime(2023, 1, 15))
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = DateUtils.parse_date(date_str, custom_formats)
                self.assertEqual(result, expected)
    
    def test_parse_date_invalid(self):
        """Test parsing invalid date formats."""
        with self.assertRaises(ValueError):
            DateUtils.parse_date("not a date")
    
    def test_format_date(self):
        """Test formatting dates."""
        date = datetime(2023, 1, 15)
        
        self.assertEqual(DateUtils.format_date(date, "%Y-%m-%d"), "2023-01-15")
        self.assertEqual(DateUtils.format_date(date, "%m/%d/%Y"), "01/15/2023")
        self.assertEqual(DateUtils.format_date(date, "%d/%m/%Y"), "15/01/2023")
        self.assertEqual(DateUtils.format_date(date, "%b %d, %Y"), "Jan 15, 2023")
    
    def test_convert_date_format(self):
        """Test converting date formats."""
        self.assertEqual(
            DateUtils.convert_date_format("2023-01-15", "%m/%d/%Y"),
            "01/15/2023"
        )
        self.assertEqual(
            DateUtils.convert_date_format("01/15/2023", "%Y-%m-%d"),
            "2023-01-15"
        )
        
        self.assertEqual(
            DateUtils.convert_date_format("15-01-2023", "%m/%d/%Y", ["%d-%m-%Y"]),
            "01/15/2023"
        )
    
    def test_is_valid_date(self):
        """Test date validation."""
        self.assertTrue(DateUtils.is_valid_date("2023-01-15", ["%Y-%m-%d"]))
        self.assertTrue(DateUtils.is_valid_date("01/15/2023", ["%m/%d/%Y"]))
        self.assertFalse(DateUtils.is_valid_date("2023-13-15", ["%Y-%m-%d"]))
        self.assertFalse(DateUtils.is_valid_date("01/32/2023", ["%m/%d/%Y"]))
        self.assertFalse(DateUtils.is_valid_date("not a date", ["%Y-%m-%d"]))
        
        self.assertTrue(DateUtils.is_valid_date("2023-01-15", ["%d/%m/%Y", "%Y-%m-%d"]))
        self.assertTrue(DateUtils.is_valid_date("15/01/2023", ["%d/%m/%Y", "%Y-%m-%d"]))
        self.assertFalse(DateUtils.is_valid_date("not a date", ["%d/%m/%Y", "%Y-%m-%d"]))


if __name__ == "__main__":
    unittest.main()
