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
        
        assert parse_date("2023-01-15", "%Y-%m-%d") == datetime(2023, 1, 15)
        
        with pytest.raises(DateFormatError):
            parse_date("invalid-date", "%Y-%m-%d")
        
        with pytest.raises(DateFormatError):
            parse_date("")
    
    def test_format_date(self):
        """Test formatting dates to different formats."""
        dt = datetime(2023, 1, 15)
        
        assert format_date(dt) == "01/15/2023"
        
        assert format_date(dt, "%Y-%m-%d") == "2023-01-15"
        
        assert format_date(dt, "%d-%m-%Y") == "15-01-2023"
    
    def test_detect_date_format(self):
        """Test detection of date format strings."""
        assert detect_date_format("2023-01-15") == "%Y-%m-%d"
        
        assert detect_date_format("01/15/2023") == "%m/%d/%Y"
        
        assert detect_date_format("01/15/23") == "%m/%d/%y"
        
        assert detect_date_format("15.01.2023") == "%d.%m.%Y"
        
        assert detect_date_format("2023/01/15") == "%Y/%m/%d"
        
        assert detect_date_format("2023.01") is None
        assert detect_date_format("not-a-date") is None
