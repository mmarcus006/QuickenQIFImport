import pytest
import os
import tempfile
from unittest.mock import patch, mock_open

from quickenqifimport.utils.file_utils import (
    read_text_file, write_text_file, read_csv_file, write_csv_file,
    load_json, save_json, load_yaml, save_yaml, FileFormatError
)

class TestFileUtils:
    """Unit tests for file utility functions."""
    
    def test_read_text_file(self):
        """Test reading text file content."""
        test_content = "Line 1\nLine 2\nLine 3"
        
        with patch("builtins.open", mock_open(read_data=test_content)):
            content = read_text_file("/path/to/file.txt")
            assert content == test_content
    
    def test_write_text_file(self):
        """Test writing content to text file."""
        test_content = "Line 1\nLine 2\nLine 3"
        
        mock = mock_open()
        with patch("builtins.open", mock):
            write_text_file("/path/to/file.txt", test_content)
            
        mock.assert_called_once_with("/path/to/file.txt", "w", encoding="utf-8")
        mock().write.assert_called_once_with(test_content)
    
    def test_read_csv_file(self):
        """Test reading CSV file content."""
        csv_content = "Header1,Header2,Header3\nValue1,Value2,Value3\nValue4,Value5,Value6"
        
        with patch("builtins.open", mock_open(read_data=csv_content)):
            result = read_csv_file("/path/to/file.csv")
            
            assert result["headers"] == ["Header1", "Header2", "Header3"]
            assert result["data"] == [["Value1", "Value2", "Value3"], ["Value4", "Value5", "Value6"]]
    
    def test_read_csv_file_no_header(self):
        """Test reading CSV file without header."""
        csv_content = "Value1,Value2,Value3\nValue4,Value5,Value6"
        
        with patch("builtins.open", mock_open(read_data=csv_content)):
            result = read_csv_file("/path/to/file.csv", has_header=False)
            
            assert result["headers"] == ["Column1", "Column2", "Column3"]
            assert result["data"] == [["Value4", "Value5", "Value6"]]
    
    def test_read_csv_file_skip_rows(self):
        """Test reading CSV file with skipping rows."""
        csv_content = "Skip1,Skip2,Skip3\nHeader1,Header2,Header3\nValue1,Value2,Value3"
        
        with patch("builtins.open", mock_open(read_data=csv_content)):
            result = read_csv_file("/path/to/file.csv", skip_rows=1)
            
            assert result["headers"] == ["Header1", "Header2", "Header3"]
            assert result["data"] == [["Value1", "Value2", "Value3"]]
    
    def test_write_csv_file(self):
        """Test writing content to CSV file."""
        headers = ["Header1", "Header2", "Header3"]
        data = [["Value1", "Value2", "Value3"], ["Value4", "Value5", "Value6"]]
        
        mock = mock_open()
        with patch("builtins.open", mock):
            write_csv_file("/path/to/file.csv", headers, data)
            
        mock.assert_called_once_with("/path/to/file.csv", "w", encoding="utf-8", newline="")
    
    def test_load_json(self):
        """Test loading JSON file."""
        json_content = '{"key1": "value1", "key2": 42, "key3": [1, 2, 3]}'
        expected_data = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        
        with patch("builtins.open", mock_open(read_data=json_content)):
            data = load_json("/path/to/file.json")
            
            assert data == expected_data
    
    def test_save_json(self):
        """Test saving data to JSON file."""
        data = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        
        mock = mock_open()
        with patch("builtins.open", mock):
            save_json("/path/to/file.json", data)
            
        mock.assert_called_once_with("/path/to/file.json", "w", encoding="utf-8")
    
    def test_load_yaml(self):
        """Test loading YAML file."""
        yaml_content = """
        key1: value1
        key2: 42
        key3:
          - 1
          - 2
          - 3
        """
        expected_data = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            data = load_yaml("/path/to/file.yaml")
            
            assert data == expected_data
    
    def test_save_yaml(self):
        """Test saving data to YAML file."""
        data = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        
        mock = mock_open()
        with patch("builtins.open", mock):
            save_yaml("/path/to/file.yaml", data)
            
        mock.assert_called_once_with("/path/to/file.yaml", "w", encoding="utf-8")
    
    def test_file_format_error(self):
        """Test FileFormatError exception."""
        with patch("builtins.open", mock_open(read_data="")):
            with pytest.raises(FileFormatError):
                read_csv_file("/path/to/file.csv")
