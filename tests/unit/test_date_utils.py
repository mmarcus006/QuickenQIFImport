import pytest
from datetime import datetime

from quickenqifimport.utils.date_utils import (
    parse_date, format_date, detect_date_format, DateFormatError
)

class TestDateUtils:
    """Unit tests for date utility functions."""
    
    def test_parse_date(self):
        """Test parsing various date formats."""
        assert parse_date("2023-01-15") == datetime(2023, 1, 15)
        
        assert parse_date("01/15/2023") == datetime(2023, 1, 15)
        
        assert parse_date("15-01-2023") == datetime(2023, 1, 15)
        
        assert parse_date("2023-01-15 14:30:00").date() == datetime(2023, 1, 15).date()
        
        dt = datetime(2023, 1, 15)
        assert parse_date(dt) == dt
        
        with pytest.raises(ValueError):
            parse_date("invalid-date")
    
    def test_format_date(self):
        """Test formatting dates to different formats."""
        dt = datetime(2023, 1, 15)
        
        assert format_date(dt) == "2023-01-15"
        
        assert format_date(dt, "%m/%d/%Y") == "01/15/2023"
        
        assert format_date(dt, "%d-%m-%Y") == "15-01-2023"
        
        assert format_date(dt, "%m/%d/%Y") == "01/15/2023"
        
        assert format_date("2023-01-15", "%m/%d/%Y") == "01/15/2023"
    
    def test_is_valid_date_format(self):
        """Test validation of date format strings."""
        assert is_valid_date_format("%Y-%m-%d") is True
        assert is_valid_date_format("%m/%d/%Y") is True
        assert is_valid_date_format("%d-%m-%Y") is True
        
        assert is_valid_date_format("YYYY-MM-DD") is False
        assert is_valid_date_format("") is False
        assert is_valid_date_format(None) is False
    
    def test_convert_date_format(self):
        """Test converting dates between different formats."""
        assert convert_date_format("2023-01-15", "%Y-%m-%d", "%m/%d/%Y") == "01/15/2023"
        
        assert convert_date_format("01/15/2023", "%m/%d/%Y", "%d-%m-%Y") == "15-01-2023"
        
        assert convert_date_format("15-01-2023", "%d-%m-%Y", "%Y-%m-%d") == "2023-01-15"
        
        with pytest.raises(ValueError):
            convert_date_format("invalid-date", "%Y-%m-%d", "%m/%d/%Y")
    
    def test_get_date_format_pattern(self):
        """Test getting regex pattern for date format validation."""
        pattern = get_date_format_pattern("%Y-%m-%d")
        assert pattern.match("2023-01-15") is not None
        assert pattern.match("2023-13-15") is None  # Invalid month
        
        pattern = get_date_format_pattern("%m/%d/%Y")
        assert pattern.match("01/15/2023") is not None
        assert pattern.match("13/15/2023") is None  # Invalid month
        
        pattern = get_date_format_pattern("%d-%m-%Y")
        assert pattern.match("15-01-2023") is not None
        assert pattern.match("15-13-2023") is None  # Invalid month
