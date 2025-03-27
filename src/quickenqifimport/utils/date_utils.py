from datetime import datetime
from typing import Optional, List


class DateUtils:
    """Utility class for date operations."""
    
    FORMATS = [
        "%m/%d/%y",    # MM/DD/YY
        "%m/%d/%Y",    # MM/DD/YYYY
        "%d/%m/%y",    # DD/MM/YY
        "%d/%m/%Y",    # DD/MM/YYYY
        "%Y-%m-%d",    # YYYY-MM-DD
        "%d-%b-%Y",    # DD-Mon-YYYY
        "%b %d, %Y",   # Mon DD, YYYY
        "%B %d, %Y",   # Month DD, YYYY
        "%Y.%m.%d"     # YYYY.MM.DD
    ]
    
    @staticmethod
    def parse_date(date_str: str, formats: Optional[List[str]] = None) -> datetime:
        """
        Parse a date string using multiple formats.
        
        Args:
            date_str: The date string to parse
            formats: List of date formats to try, defaults to FORMATS if None
            
        Returns:
            datetime: The parsed datetime object
            
        Raises:
            ValueError: If the date string cannot be parsed with any of the formats
        """
        if formats is None:
            formats = DateUtils.FORMATS
            
        date_str = date_str.replace("'", "").strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        raise ValueError(f"Could not parse date: {date_str}")
    
    @staticmethod
    def format_date(date: datetime, format_str: str = "%m/%d/%Y") -> str:
        """
        Format a datetime object as a string.
        
        Args:
            date: The datetime object to format
            format_str: The format string to use
            
        Returns:
            str: The formatted date string
        """
        return date.strftime(format_str)
    
    @staticmethod
    def convert_date_format(date_str: str, to_format: str = "%m/%d/%Y", from_formats: Optional[List[str]] = None, input_format: Optional[str] = None) -> str:
        """
        Convert a date string from one format to another.
        
        Args:
            date_str: The date string to convert
            to_format: The target format
            from_formats: List of possible source formats, defaults to FORMATS if None
            input_format: Specific input format to use (takes precedence over from_formats)
            
        Returns:
            str: The date string in the target format
            
        Raises:
            ValueError: If the date string cannot be parsed with any of the formats
        """
        if input_format:
            try:
                date = datetime.strptime(date_str, input_format)
            except ValueError:
                raise ValueError(f"Could not parse date '{date_str}' with format '{input_format}'")
        else:
            date = DateUtils.parse_date(date_str, from_formats)
            
        return DateUtils.format_date(date, to_format)
    
    @staticmethod
    def is_valid_date(date_str: str, formats: Optional[List[str]] = None) -> bool:
        """
        Check if a date string is valid according to any of the formats.
        
        Args:
            date_str: The date string to check
            formats: List of date formats to try, defaults to FORMATS if None
            
        Returns:
            bool: True if the date string is valid, False otherwise
        """
        try:
            DateUtils.parse_date(date_str, formats)
            return True
        except ValueError:
            return False
