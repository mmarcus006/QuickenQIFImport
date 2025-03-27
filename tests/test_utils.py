import unittest
from datetime import datetime
import os
import tempfile
import json

from src.quickenqifimport.utils.date_utils import DateUtils
from src.quickenqifimport.utils.amount_utils import AmountUtils
from src.quickenqifimport.utils.file_utils import FileUtils
from src.quickenqifimport.utils.validation_utils import ValidationUtils
from src.quickenqifimport.models.csv_models import CSVTemplate


class TestDateUtils(unittest.TestCase):
    """Test cases for date utilities."""
    
    def test_parse_date(self):
        """Test parsing dates with various formats."""
        self.assertEqual(DateUtils.parse_date("01/15/2023"), datetime(2023, 1, 15))
        self.assertEqual(DateUtils.parse_date("15/01/2023", ["%d/%m/%Y"]), datetime(2023, 1, 15))
        self.assertEqual(DateUtils.parse_date("2023-01-15"), datetime(2023, 1, 15))
        
        self.assertEqual(DateUtils.parse_date("15.01.2023", ["%d.%m.%Y"]), datetime(2023, 1, 15))
        
        self.assertEqual(DateUtils.parse_date("'01/15/2023'"), datetime(2023, 1, 15))
        
        with self.assertRaises(ValueError):
            DateUtils.parse_date("invalid date")
    
    def test_format_date(self):
        """Test formatting dates."""
        date = datetime(2023, 1, 15)
        
        self.assertEqual(DateUtils.format_date(date), "01/15/2023")
        
        self.assertEqual(DateUtils.format_date(date, "%Y-%m-%d"), "2023-01-15")
        self.assertEqual(DateUtils.format_date(date, "%d/%m/%Y"), "15/01/2023")
        self.assertEqual(DateUtils.format_date(date, "%b %d, %Y"), "Jan 15, 2023")
    
    def test_convert_date_format(self):
        """Test converting date formats."""
        self.assertEqual(DateUtils.convert_date_format("01/15/2023", "%Y-%m-%d"), "2023-01-15")
        
        self.assertEqual(DateUtils.convert_date_format("15.01.2023", "%Y-%m-%d", ["%d.%m.%Y"]), "2023-01-15")
        
        with self.assertRaises(ValueError):
            DateUtils.convert_date_format("invalid date", "%Y-%m-%d")
    
    def test_is_valid_date(self):
        """Test date validation."""
        self.assertTrue(DateUtils.is_valid_date("01/15/2023"))
        self.assertTrue(DateUtils.is_valid_date("2023-01-15"))
        self.assertTrue(DateUtils.is_valid_date("15/01/2023", ["%d/%m/%Y"]))
        
        self.assertFalse(DateUtils.is_valid_date("invalid date"))
        self.assertFalse(DateUtils.is_valid_date("13/13/2023"))
        self.assertFalse(DateUtils.is_valid_date("35/01/2023"))  # Invalid day


class TestAmountUtils(unittest.TestCase):
    """Test cases for amount utilities."""
    
    def test_parse_amount(self):
        """Test parsing amounts."""
        self.assertEqual(AmountUtils.parse_amount("100.00"), 100.0)
        self.assertEqual(AmountUtils.parse_amount("-50.25"), -50.25)
        
        self.assertEqual(AmountUtils.parse_amount("1,000.00"), 1000.0)
        self.assertEqual(AmountUtils.parse_amount("1,234,567.89"), 1234567.89)
        
        self.assertEqual(AmountUtils.parse_amount("$100.00"), 100.0)
        self.assertEqual(AmountUtils.parse_amount("€100.00"), 100.0)
        
        self.assertEqual(AmountUtils.parse_amount("100,00", ",", "."), 100.0)
        self.assertEqual(AmountUtils.parse_amount("1.000,00", ",", "."), 1000.0)
        
        self.assertEqual(AmountUtils.parse_amount(""), 0.0)
        
        with self.assertRaises(ValueError):
            AmountUtils.parse_amount("invalid amount")
    
    def test_format_amount(self):
        """Test formatting amounts."""
        self.assertEqual(AmountUtils.format_amount(100), "100.00")
        self.assertEqual(AmountUtils.format_amount(-50.25), "-50.25")
        
        self.assertEqual(AmountUtils.format_amount(100, 0), "100")
        self.assertEqual(AmountUtils.format_amount(100.5, 3), "100.500")
        
        self.assertEqual(AmountUtils.format_amount(1000, 2, ",", "."), "1.000,00")
        
        self.assertEqual(AmountUtils.format_amount(100, include_sign=True), "+100.00")
        self.assertEqual(AmountUtils.format_amount(-100, include_sign=True), "-100.00")
    
    def test_is_negative(self):
        """Test negative amount detection."""
        self.assertTrue(AmountUtils.is_negative("-100.00"))
        self.assertTrue(AmountUtils.is_negative("(100.00)"))
        
        self.assertFalse(AmountUtils.is_negative("100.00"))
        self.assertFalse(AmountUtils.is_negative("+100.00"))
    
    def test_convert_to_qif_format(self):
        """Test converting to QIF format."""
        self.assertEqual(AmountUtils.convert_to_qif_format(100), "100.00")
        self.assertEqual(AmountUtils.convert_to_qif_format(-50.25), "-50.25")
        
        self.assertEqual(AmountUtils.convert_to_qif_format("100.00"), "100.00")
        self.assertEqual(AmountUtils.convert_to_qif_format("1,000.00"), "1000.00")
        
        self.assertEqual(AmountUtils.convert_to_qif_format("1.000,00", ",", "."), "1000.00")


class TestFileUtils(unittest.TestCase):
    """Test cases for file utilities."""
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        temp_dir = os.path.join(tempfile.gettempdir(), "quickenqifimport_test")
        
        try:
            FileUtils.ensure_directory_exists(temp_dir)
            
            self.assertTrue(os.path.exists(temp_dir))
            self.assertTrue(os.path.isdir(temp_dir))
            
            FileUtils.ensure_directory_exists(temp_dir)
            self.assertTrue(os.path.exists(temp_dir))
        finally:
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
    
    def test_get_file_extension(self):
        """Test file extension extraction."""
        self.assertEqual(FileUtils.get_file_extension("file.txt"), "txt")
        self.assertEqual(FileUtils.get_file_extension("file.csv"), "csv")
        self.assertEqual(FileUtils.get_file_extension("file.qif"), "qif")
        
        self.assertEqual(FileUtils.get_file_extension("/path/to/file.txt"), "txt")
        
        self.assertEqual(FileUtils.get_file_extension("file.TXT"), "txt")
        
        self.assertEqual(FileUtils.get_file_extension("file"), "")
        
        self.assertEqual(FileUtils.get_file_extension("file.tar.gz"), "gz")
    
    def test_is_qif_file(self):
        """Test QIF file detection."""
        self.assertTrue(FileUtils.is_qif_file("file.qif"))
        self.assertTrue(FileUtils.is_qif_file("/path/to/file.qif"))
        self.assertTrue(FileUtils.is_qif_file("file.QIF"))
        
        self.assertFalse(FileUtils.is_qif_file("file.txt"))
        self.assertFalse(FileUtils.is_qif_file("file"))
    
    def test_is_csv_file(self):
        """Test CSV file detection."""
        self.assertTrue(FileUtils.is_csv_file("file.csv"))
        self.assertTrue(FileUtils.is_csv_file("/path/to/file.csv"))
        self.assertTrue(FileUtils.is_csv_file("file.CSV"))
        
        self.assertFalse(FileUtils.is_csv_file("file.txt"))
        self.assertFalse(FileUtils.is_csv_file("file"))
    
    def test_save_and_load_template(self):
        """Test template saving and loading."""
        template = CSVTemplate(
            name="Test",
            description="Test template",
            account_type="Bank",
            field_mapping={
                "Date": "date",
                "Amount": "amount"
            }
        )
        
        temp_file = tempfile.mktemp(suffix='.json')
        
        try:
            FileUtils.save_template(template, temp_file)
            
            self.assertTrue(os.path.exists(temp_file))
            
            loaded_template = FileUtils.load_template(temp_file)
            
            self.assertEqual(loaded_template.name, template.name)
            self.assertEqual(loaded_template.description, template.description)
            self.assertEqual(loaded_template.account_type, template.account_type)
            self.assertEqual(loaded_template.field_mapping, template.field_mapping)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_list_templates(self):
        """Test template listing."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            for i in range(3):
                with open(os.path.join(temp_dir, f"template{i}.json"), 'w') as file:
                    file.write("{}")
                    
            with open(os.path.join(temp_dir, "not_a_template.txt"), 'w') as file:
                file.write("")
                
            templates = FileUtils.list_templates(temp_dir)
            
            self.assertEqual(len(templates), 3)
            for i in range(3):
                self.assertIn(f"template{i}.json", templates)
            self.assertNotIn("not_a_template.txt", templates)
        finally:
            for file in os.listdir(temp_dir):
                os.unlink(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)


class TestValidationUtils(unittest.TestCase):
    """Test cases for validation utilities."""
    
    def test_validate_required_fields(self):
        """Test required field validation."""
        data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        missing = ValidationUtils.validate_required_fields(data, ["field1", "field2"])
        self.assertEqual(missing, [])
        
        missing = ValidationUtils.validate_required_fields(data, ["field1", "field4"])
        self.assertEqual(missing, ["field4"])
        
        data = {"field1": "value1", "field2": "", "field3": None}
        missing = ValidationUtils.validate_required_fields(data, ["field1", "field2", "field3"])
        self.assertEqual(missing, ["field2", "field3"])
    
    def test_validate_field_format(self):
        """Test field format validation."""
        error = ValidationUtils.validate_field_format("2023-01-15", r"\d{4}-\d{2}-\d{2}", "Date")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_field_format("01/15/2023", r"\d{4}-\d{2}-\d{2}", "Date")
        self.assertEqual(error, "Date has invalid format")
        
        error = ValidationUtils.validate_field_format("", r"\d{4}-\d{2}-\d{2}", "Date")
        self.assertIsNone(error)
    
    def test_validate_numeric_field(self):
        """Test numeric field validation."""
        error = ValidationUtils.validate_numeric_field("100.00", "Amount")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_numeric_field("-50.25", "Amount")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_numeric_field("-50.25", "Amount", allow_negative=False)
        self.assertEqual(error, "Amount cannot be negative")
        
        error = ValidationUtils.validate_numeric_field("not a number", "Amount")
        self.assertEqual(error, "Amount must be a number")
        
        error = ValidationUtils.validate_numeric_field("", "Amount")
        self.assertIsNone(error)
    
    def test_validate_date_field(self):
        """Test date field validation."""
        error = ValidationUtils.validate_date_field("2023-01-15", "Date")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_date_field("invalid date", "Date")
        self.assertEqual(error, "Date must be a valid date")
        
        error = ValidationUtils.validate_date_field("", "Date")
        self.assertIsNone(error)
    
    def test_validate_with_custom_function(self):
        """Test validation with custom function."""
        def validate_even(value):
            if value % 2 != 0:
                return "Value must be even"
            return None
            
        error = ValidationUtils.validate_with_custom_function(2, validate_even, "Number")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_with_custom_function(3, validate_even, "Number")
        self.assertEqual(error, "Value must be even")
        
        error = ValidationUtils.validate_with_custom_function(None, validate_even, "Number")
        self.assertIsNone(error)
    
    def test_validate_enum_field(self):
        """Test enum field validation."""
        valid_values = ["apple", "banana", "cherry"]
        
        error = ValidationUtils.validate_enum_field("apple", valid_values, "Fruit")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_enum_field("orange", valid_values, "Fruit")
        self.assertEqual(error, "Fruit must be one of: apple, banana, cherry")
        
        error = ValidationUtils.validate_enum_field("APPLE", valid_values, "Fruit", case_sensitive=False)
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_enum_field("APPLE", valid_values, "Fruit", case_sensitive=True)
        self.assertEqual(error, "Fruit must be one of: apple, banana, cherry")
        
        error = ValidationUtils.validate_enum_field("", valid_values, "Fruit")
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
