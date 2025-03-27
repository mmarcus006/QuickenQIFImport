import unittest
from src.quickenqifimport.utils.validation_utils import ValidationUtils


class TestValidationUtils(unittest.TestCase):
    """Test cases for validation_utils module."""
    
    def test_validate_required_fields(self):
        """Test validating required fields."""
        data = {
            "field1": "value1",
            "field2": "value2",
            "field3": ""
        }
        
        missing = ValidationUtils.validate_required_fields(data, ["field1", "field2"])
        self.assertEqual(missing, [])
        
        missing = ValidationUtils.validate_required_fields(data, ["field1", "field4"])
        self.assertEqual(missing, ["field4"])
        
        missing = ValidationUtils.validate_required_fields(data, ["field1", "field3"])
        self.assertEqual(missing, ["field3"])
    
    def test_validate_field_format(self):
        """Test validating field format."""
        error = ValidationUtils.validate_field_format(
            "test@example.com", 
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "Email"
        )
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_field_format(
            "not an email", 
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "Email"
        )
        self.assertEqual(error, "Email has invalid format")
        
        error = ValidationUtils.validate_field_format(
            "", 
            r".*",
            "Field"
        )
        self.assertIsNone(error)
    
    def test_validate_numeric_field(self):
        """Test validating numeric fields."""
        error = ValidationUtils.validate_numeric_field("100.00", "Amount")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_numeric_field("-100.00", "Amount")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_numeric_field("1,000.00", "Amount")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_numeric_field("not a number", "Amount")
        self.assertEqual(error, "Amount must be a number")
        
        error = ValidationUtils.validate_numeric_field("-100.00", "Amount", allow_negative=False)
        self.assertEqual(error, "Amount cannot be negative")
        
        error = ValidationUtils.validate_numeric_field("", "Amount")
        self.assertIsNone(error)
    
    def test_validate_date_field(self):
        """Test validating date fields."""
        from unittest.mock import patch
        
        with patch('src.quickenqifimport.utils.date_utils.DateUtils.is_valid_date') as mock_is_valid_date:
            mock_is_valid_date.return_value = True
            error = ValidationUtils.validate_date_field("2023-01-15", "Date")
            self.assertIsNone(error)
            
            mock_is_valid_date.return_value = False
            error = ValidationUtils.validate_date_field("not a date", "Date")
            self.assertEqual(error, "Date must be a valid date")
            
            error = ValidationUtils.validate_date_field("", "Date")
            self.assertIsNone(error)
    
    def test_validate_enum_field(self):
        """Test validating enum fields."""
        valid_values = ["value1", "value2"]
        
        error = ValidationUtils.validate_enum_field("value1", valid_values, "Field")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_enum_field("value3", valid_values, "Field")
        self.assertEqual(error, "Field must be one of: value1, value2")
        
        error = ValidationUtils.validate_enum_field("VALUE1", valid_values, "Field")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_enum_field("VALUE1", valid_values, "Field", case_sensitive=True)
        self.assertEqual(error, "Field must be one of: value1, value2")
        
        error = ValidationUtils.validate_enum_field("", valid_values, "Field")
        self.assertIsNone(error)
    
    def test_validate_with_custom_function(self):
        """Test validating with a custom function."""
        def is_even(value):
            try:
                num = int(value)
                if num % 2 == 0:
                    return None
                else:
                    return "Number must be even"
            except ValueError:
                return "Not a valid number"
        
        error = ValidationUtils.validate_with_custom_function("2", is_even, "Number")
        self.assertIsNone(error)
        
        error = ValidationUtils.validate_with_custom_function("3", is_even, "Number")
        self.assertEqual(error, "Number must be even")
        
        error = ValidationUtils.validate_with_custom_function("not a number", is_even, "Number")
        self.assertEqual(error, "Not a valid number")
        
        error = ValidationUtils.validate_with_custom_function(None, is_even, "Number")
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
