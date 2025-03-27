from typing import Dict, Any, List, Optional, Union, Callable
import re


class ValidationUtils:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate that all required fields are present and not empty.
        
        Args:
            data: The data to validate
            required_fields: List of required field names
            
        Returns:
            List[str]: List of missing field names
        """
        missing = []
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                missing.append(field)
        return missing
    
    @staticmethod
    def validate_field_format(value: str, pattern: str, field_name: str) -> Optional[str]:
        """
        Validate that a field matches a regular expression pattern.
        
        Args:
            value: The value to validate
            pattern: The regular expression pattern
            field_name: The name of the field (for error message)
            
        Returns:
            Optional[str]: Error message if validation fails, None otherwise
        """
        if not value:
            return None
            
        if not re.match(pattern, value):
            return f"{field_name} has invalid format"
            
        return None
    
    @staticmethod
    def validate_numeric_field(value: str, field_name: str, allow_negative: bool = True) -> Optional[str]:
        """
        Validate that a field is a valid number.
        
        Args:
            value: The value to validate
            field_name: The name of the field (for error message)
            allow_negative: Whether to allow negative numbers
            
        Returns:
            Optional[str]: Error message if validation fails, None otherwise
        """
        if not value:
            return None
            
        value = value.replace(',', '').replace(' ', '')
        
        try:
            num = float(value)
            if not allow_negative and num < 0:
                return f"{field_name} cannot be negative"
        except ValueError:
            return f"{field_name} must be a number"
            
        return None
    
    @staticmethod
    def validate_date_field(value: str, field_name: str) -> Optional[str]:
        """
        Validate that a field is a valid date.
        
        Args:
            value: The value to validate
            field_name: The name of the field (for error message)
            
        Returns:
            Optional[str]: Error message if validation fails, None otherwise
        """
        if not value:
            return None
            
        from .date_utils import DateUtils
        
        if not DateUtils.is_valid_date(value):
            return f"{field_name} must be a valid date"
            
        return None
    
    @staticmethod
    def validate_enum_field(value: str, valid_values: List[str], field_name: str, 
                           case_sensitive: bool = False) -> Optional[str]:
        """
        Validate that a field has one of the allowed values.
        
        Args:
            value: The value to validate
            valid_values: List of valid values
            field_name: The name of the field (for error message)
            case_sensitive: Whether the comparison is case-sensitive
            
        Returns:
            Optional[str]: Error message if validation fails, None otherwise
        """
        if not value:
            return None
            
        if case_sensitive:
            if value not in valid_values:
                return f"{field_name} must be one of: {', '.join(valid_values)}"
        else:
            if value.lower() not in [v.lower() for v in valid_values]:
                return f"{field_name} must be one of: {', '.join(valid_values)}"
            
        return None
    
    @staticmethod
    def validate_with_custom_function(value: Any, validator: Callable[[Any], Optional[str]], 
                                     field_name: str) -> Optional[str]:
        """
        Validate a field using a custom validation function.
        
        Args:
            value: The value to validate
            validator: A function that takes the value and returns an error message or None
            field_name: The name of the field (for error message)
            
        Returns:
            Optional[str]: Error message if validation fails, None otherwise
        """
        if value is None:
            return None
            
        return validator(value)


def validate_field_format(data: Dict[str, Any], field: str, pattern: str) -> bool:
    """
    Validate that a field in the data matches a regular expression pattern.
    
    Args:
        data: The data containing the field
        field: The name of the field to validate
        pattern: The regular expression pattern
        
    Returns:
        bool: True if the field matches the pattern
    """
    if field not in data or not data[field]:
        return False
        
    return re.match(pattern, data[field]) is not None


def validate_numeric_field(data: Dict[str, Any], field: str) -> bool:
    """
    Validate that a field in the data is a valid number.
    
    Args:
        data: The data containing the field
        field: The name of the field to validate
        
    Returns:
        bool: True if the field is a valid number
    """
    if field not in data or not data[field]:
        return False
        
    try:
        float(data[field].replace(',', '').replace(' ', ''))
        return True
    except ValueError:
        return False


def validate_date_field(data: Dict[str, Any], field: str, date_format: str) -> bool:
    """
    Validate that a field in the data is a valid date.
    
    Args:
        data: The data containing the field
        field: The name of the field to validate
        date_format: The expected date format
        
    Returns:
        bool: True if the field is a valid date
    """
    if field not in data or not data[field]:
        return False
        
    from .date_utils import DateUtils
    
    return DateUtils.is_valid_date(data[field], [date_format])


def validate_with_custom_function(data: Dict[str, Any], field: str, validator: Callable[[Any], Optional[str]]) -> bool:
    """
    Validate a field in the data using a custom validation function.
    
    Args:
        data: The data containing the field
        field: The name of the field to validate
        validator: A function that takes the value and returns None if valid or an error message
        
    Returns:
        bool: True if the field passes the validation function (validator returns None)
    """
    if field not in data:
        return False
        
    result = validator(data[field])
    return result is None


def validate_enum_field(data: Dict[str, Any], field: str, valid_values: List[str]) -> bool:
    """
    Validate that a field in the data has one of the allowed values.
    
    Args:
        data: The data containing the field
        field: The name of the field to validate
        valid_values: List of valid values
        
    Returns:
        bool: True if the field has one of the allowed values
    """
    if field not in data or not data[field]:
        return False
        
    return data[field] in valid_values
