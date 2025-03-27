import unittest
import os
import tempfile
import shutil
from datetime import datetime
from decimal import Decimal

from src.quickenqifimport.utils.date_utils import DateUtils
from src.quickenqifimport.utils.amount_utils import AmountUtils
from src.quickenqifimport.utils.file_utils import FileUtils
from src.quickenqifimport.utils.validation_utils import ValidationUtils
from src.quickenqifimport.models.csv_models import CSVTemplate


class TestDateUtils(unittest.TestCase):
    """Test cases for date_utils module."""
    
    def test_parse_date_valid_formats(self):
        """Test parsing dates in various formats."""
        test_cases = [
            ("2023-01-15", datetime(2023, 1, 15)),
            ("01/15/2023", datetime(2023, 1, 15)),
            ("15/01/2023", datetime(2023, 1, 15)),
            ("15-Jan-2023", datetime(2023, 1, 15)),
            ("Jan 15, 2023", datetime(2023, 1, 15)),
            ("January 15, 2023", datetime(2023, 1, 15)),
            ("2023.01.15", datetime(2023, 1, 15))
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = DateUtils.parse_date(date_str)
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
    
    def test_is_valid_date(self):
        """Test date validation."""
        self.assertTrue(DateUtils.is_valid_date("2023-01-15", ["%Y-%m-%d"]))
        self.assertTrue(DateUtils.is_valid_date("01/15/2023", ["%m/%d/%Y"]))
        self.assertFalse(DateUtils.is_valid_date("2023-13-15", ["%Y-%m-%d"]))
        self.assertFalse(DateUtils.is_valid_date("01/32/2023", ["%m/%d/%Y"]))
        self.assertFalse(DateUtils.is_valid_date("not a date", ["%Y-%m-%d"]))


class TestAmountUtils(unittest.TestCase):
    """Test cases for amount_utils module."""
    
    def test_parse_amount_valid(self):
        """Test parsing valid amounts."""
        test_cases = [
            ("100.00", Decimal("100.00")),
            ("100", Decimal("100")),
            ("100.5", Decimal("100.5")),
            ("-100.00", Decimal("-100.00")),
            ("$100.00", Decimal("100.00")),
            ("$-100.00", Decimal("-100.00")),
            ("-$100.00", Decimal("-100.00")),
            ("1,000.00", Decimal("1000.00")),
            ("1,000,000.00", Decimal("1000000.00")),
            ("(100.00)", Decimal("-100.00"))
        ]
        
        for amount_str, expected in test_cases:
            with self.subTest(amount_str=amount_str):
                result = AmountUtils.parse_amount(amount_str)
                self.assertEqual(result, expected)
    
    def test_parse_amount_invalid(self):
        """Test parsing invalid amounts."""
        with self.assertRaises(ValueError):
            AmountUtils.parse_amount("not an amount")
    
    def test_format_amount(self):
        """Test formatting amounts."""
        test_cases = [
            (Decimal("100.00"), "100.00"),
            (Decimal("-100.00"), "-100.00"),
            (Decimal("1000.00"), "1,000.00"),
            (Decimal("1000000.00"), "1,000,000.00"),
            (Decimal("100"), "100.00"),
            (Decimal("100.5"), "100.50")
        ]
        
        for amount, expected in test_cases:
            with self.subTest(amount=amount):
                result = AmountUtils.format_amount(amount)
                self.assertEqual(result, expected)
    
    def test_convert_to_qif_format(self):
        """Test converting amounts to QIF format."""
        test_cases = [
            ("100.00", "100.00"),
            ("-100.00", "-100.00"),
            ("$100.00", "100.00"),
            ("$-100.00", "-100.00"),
            ("-$100.00", "-100.00"),
            ("1,000.00", "1000.00"),
            ("(100.00)", "-100.00")
        ]
        
        for amount_str, expected in test_cases:
            with self.subTest(amount_str=amount_str):
                result = AmountUtils.convert_to_qif_format(amount_str)
                self.assertEqual(result, expected)
    
    def test_is_negative(self):
        """Test checking if an amount is negative."""
        self.assertTrue(AmountUtils.is_negative(str(Decimal("-100.00"))))
        self.assertTrue(AmountUtils.is_negative("-100.00"))
        self.assertTrue(AmountUtils.is_negative("(100.00)"))
        self.assertTrue(AmountUtils.is_negative("-$100.00"))
        
        self.assertFalse(AmountUtils.is_negative(str(Decimal("100.00"))))
        self.assertFalse(AmountUtils.is_negative("100.00"))
        self.assertFalse(AmountUtils.is_negative("$100.00"))


class TestFileUtils(unittest.TestCase):
    """Test cases for file_utils module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_file_extension(self):
        """Test getting file extensions."""
        self.assertEqual(FileUtils.get_file_extension("file.txt"), "txt")
        self.assertEqual(FileUtils.get_file_extension("file.csv"), "csv")
        self.assertEqual(FileUtils.get_file_extension("file.qif"), "qif")
        self.assertEqual(FileUtils.get_file_extension("file"), "")
        self.assertEqual(FileUtils.get_file_extension("file."), "")
        self.assertEqual(FileUtils.get_file_extension("path/to/file.txt"), "txt")
    
    def test_is_qif_file(self):
        """Test checking if a file is a QIF file."""
        self.assertTrue(FileUtils.is_qif_file("file.qif"))
        self.assertTrue(FileUtils.is_qif_file("path/to/file.qif"))
        self.assertTrue(FileUtils.is_qif_file("file.QIF"))
        
        self.assertFalse(FileUtils.is_qif_file("file.csv"))
        self.assertFalse(FileUtils.is_qif_file("file.txt"))
        self.assertFalse(FileUtils.is_qif_file("file"))
    
    def test_is_csv_file(self):
        """Test checking if a file is a CSV file."""
        self.assertTrue(FileUtils.is_csv_file("file.csv"))
        self.assertTrue(FileUtils.is_csv_file("path/to/file.csv"))
        self.assertTrue(FileUtils.is_csv_file("file.CSV"))
        
        self.assertFalse(FileUtils.is_csv_file("file.qif"))
        self.assertFalse(FileUtils.is_csv_file("file.txt"))
        self.assertFalse(FileUtils.is_csv_file("file"))
    
    def test_ensure_directory_exists(self):
        """Test ensuring a directory exists."""
        dir_path = os.path.join(self.temp_dir, "test_dir")
        
        self.assertFalse(os.path.exists(dir_path))
        
        FileUtils.ensure_directory_exists(dir_path)
        
        self.assertTrue(os.path.exists(dir_path))
        self.assertTrue(os.path.isdir(dir_path))
        
        FileUtils.ensure_directory_exists(dir_path)
        self.assertTrue(os.path.exists(dir_path))
    
    def test_save_and_load_template(self):
        """Test saving and loading templates."""
        template = CSVTemplate(
            name="Test",
            account_type="Bank",
            field_mapping={
                "Date": "date",
                "Amount": "amount",
                "Description": "payee"
            },
            description="Test template",
            date_format="%Y-%m-%d",
            delimiter=","
        )
        
        file_path = os.path.join(self.temp_dir, "test_template.json")
        
        FileUtils.save_template(template, file_path)
        
        self.assertTrue(os.path.exists(file_path))
        
        loaded_template = FileUtils.load_template(file_path)
        
        self.assertEqual(loaded_template.name, template.name)
        self.assertEqual(loaded_template.account_type, template.account_type)
        self.assertEqual(loaded_template.field_mapping, template.field_mapping)
        self.assertEqual(loaded_template.description, template.description)
        self.assertEqual(loaded_template.date_format, template.date_format)
        self.assertEqual(loaded_template.delimiter, template.delimiter)
    
    def test_list_templates(self):
        """Test listing templates."""
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f"template{i}.json")
            with open(file_path, 'w') as file:
                file.write("{}")
                
        templates = FileUtils.list_templates(self.temp_dir)
        
        self.assertEqual(len(templates), 3)
        for i in range(3):
            self.assertIn(f"template{i}.json", templates)
        
        with self.assertRaises(FileNotFoundError):
            FileUtils.list_templates(os.path.join(self.temp_dir, "nonexistent"))


class TestValidationUtils(unittest.TestCase):
    """Test cases for validation_utils module."""
    
    def test_validate_required_fields(self):
        """Test validating required fields."""
        data = {
            "field1": "value1",
            "field2": "value2",
            "field3": ""
        }
        
        self.assertEqual(ValidationUtils.validate_required_fields(data, ["field1", "field2"]), [])
        
        self.assertTrue(len(ValidationUtils.validate_required_fields(data, ["field1", "field4"])) > 0)
        
        self.assertTrue(len(ValidationUtils.validate_required_fields(data, ["field1", "field3"])) > 0)
    
    def test_validate_field_format(self):
        """Test validating field format."""
        import re
        
        data = {
            "email": "test@example.com",
            "phone": "123-456-7890",
            "invalid_email": "not an email"
        }
        
        self.assertIsNone(ValidationUtils.validate_field_format(
            data["email"], r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "email"
        ))
        
        self.assertIsNotNone(ValidationUtils.validate_field_format(
            data["invalid_email"], r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "invalid_email"
        ))
        
        with self.assertRaises(KeyError):
            ValidationUtils.validate_field_format(
                data["nonexistent"], r".*", "nonexistent"
            )
    
    def test_validate_date_field(self):
        """Test validating date fields."""
        data = {
            "valid_date": "2023-01-15",
            "invalid_date": "not a date"
        }
        
        self.assertIsNone(ValidationUtils.validate_date_field(
            data["valid_date"], "valid_date"
        ))
        
        self.assertIsNotNone(ValidationUtils.validate_date_field(
            data["invalid_date"], "invalid_date"
        ))
        
        with self.assertRaises(KeyError):
            ValidationUtils.validate_date_field(
                data["nonexistent"], "nonexistent"
            )
    
    def test_validate_numeric_field(self):
        """Test validating numeric fields."""
        data = {
            "valid_number": "100.00",
            "invalid_number": "not a number"
        }
        
        self.assertIsNone(ValidationUtils.validate_numeric_field(
            data["valid_number"], "valid_number"
        ))
        
        self.assertIsNotNone(ValidationUtils.validate_numeric_field(
            data["invalid_number"], "invalid_number"
        ))
        
        with self.assertRaises(KeyError):
            ValidationUtils.validate_numeric_field(
                data["nonexistent"], "nonexistent"
            )
    
    def test_validate_enum_field(self):
        """Test validating enum fields."""
        data = {
            "valid_enum": "value1",
            "invalid_enum": "value3"
        }
        
        valid_values = ["value1", "value2"]
        
        self.assertIsNone(ValidationUtils.validate_enum_field(
            data["valid_enum"], valid_values, "valid_enum"
        ))
        
        self.assertIsNotNone(ValidationUtils.validate_enum_field(
            data["invalid_enum"], valid_values, "invalid_enum"
        ))
        
        with self.assertRaises(KeyError):
            ValidationUtils.validate_enum_field(
                data["nonexistent"], valid_values, "nonexistent"
            )
    
    def test_validate_with_custom_function(self):
        """Test validating with a custom function."""
        data = {
            "even_number": "2",
            "odd_number": "3"
        }
        
        def is_even(value):
            try:
                num = int(value)
                if num % 2 == 0:
                    return None
                else:
                    return "Number must be even"
            except ValueError:
                return "Not a valid number"
        
        self.assertIsNone(ValidationUtils.validate_with_custom_function(
            data["even_number"], is_even, "even_number"
        ))
        
        self.assertEqual(
            ValidationUtils.validate_with_custom_function(data["odd_number"], is_even, "odd_number"),
            "Number must be even"
        )
        
        with self.assertRaises(KeyError):
            ValidationUtils.validate_with_custom_function(
                data["nonexistent"], is_even, "nonexistent"
            )


if __name__ == "__main__":
    unittest.main()
