from datetime import datetime
from typing import Optional, Union
import re

class DateFormatError(Exception):
    """Exception raised for errors in date format parsing."""
    pass

def parse_date(date_str: str, date_format: Optional[str] = None) -> datetime:
    """Parse a date string into a datetime object.
    
    Args:
        date_str: Date string to parse
        date_format: Optional format string for parsing. If None, tries common formats.
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        DateFormatError: If the date string cannot be parsed
    """
    if not date_str:
        raise DateFormatError("Empty date string")
        
    if date_format:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            raise DateFormatError(f"Date '{date_str}' does not match format '{date_format}'")
    
    formats = [
        '%m/%d/%y',      # MM/DD/YY
        '%m/%d/%Y',      # MM/DD/YYYY
        '%d/%m/%y',      # DD/MM/YY
        '%d/%m/%Y',      # DD/MM/YYYY
        '%Y-%m-%d',      # YYYY-MM-DD
        '%Y/%m/%d',      # YYYY/MM/DD
        '%d.%m.%Y',      # DD.MM.YYYY
        '%d.%m.%y',      # DD.MM.YY
        '%m-%d-%Y',      # MM-DD-YYYY
        '%m-%d-%y',      # MM-DD-YY
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    raise DateFormatError(f"Could not parse date '{date_str}' with any known format")
    
def format_date(date_obj: datetime, date_format: str = '%m/%d/%Y') -> str:
    """Format a datetime object as a string.
    
    Args:
        date_obj: Datetime object to format
        date_format: Format string for output
        
    Returns:
        str: Formatted date string
    """
    return date_obj.strftime(date_format)
    
def detect_date_format(date_str: str) -> Optional[str]:
    """Attempt to detect the format of a date string.
    
    Args:
        date_str: Date string to analyze
        
    Returns:
        Optional[str]: Detected format string or None if format cannot be determined
    """
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return '%Y-%m-%d'
        
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
        return '%m/%d/%Y'
        
    if re.match(r'^\d{1,2}/\d{1,2}/\d{2}$', date_str):
        return '%m/%d/%y'
        
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', date_str):
        return None
        
    if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', date_str):
        return '%d.%m.%Y'
        
    if re.match(r'^\d{4}/\d{2}/\d{2}$', date_str):
        return '%Y/%m/%d'
        
    return None
