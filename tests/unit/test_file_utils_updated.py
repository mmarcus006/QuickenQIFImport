import pytest
import os
import tempfile
import json
import yaml
from unittest.mock import patch, mock_open

from quickenqifimport.utils.file_utils import (
    read_text_file, write_text_file, read_csv_file, write_csv_file,
    load_json, save_json, load_yaml, save_yaml, FileFormatError
)

class TestFileUtils:
    """Unit tests for file utility functions."""
    
    @pytest.fixture
    def sample_text(self):
        """Sample text content."""
        return "This is a sample text file.\nIt has multiple lines.\n"
    
    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV content."""
        return """Name,Age,City
John,30,New York
Jane,25,Los Angeles
Bob,40,Chicago
"""
    
    @pytest.fixture
    def sample_json_data(self):
        """Sample JSON data."""
        return {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001"
            },
            "phones": [
                "555-1234",
                "555-5678"
            ]
        }
    
    @pytest.fixture
    def sample_yaml_data(self):
        """Sample YAML data."""
        return {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zip": "10001"
            },
            "phones": [
                "555-1234",
                "555-5678"
            ]
        }
    
    def test_read_text_file(self, sample_text):
        """Test reading a text file."""
        with patch('builtins.open', mock_open(read_data=sample_text)):
            content = read_text_file('test.txt')
            assert content == sample_text
    
    def test_write_text_file(self, sample_text):
        """Test writing a text file."""
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            write_text_file('test.txt', sample_text)
            mock_file.assert_called_once_with('test.txt', 'w', encoding='utf-8')
            mock_file().write.assert_called_once_with(sample_text)
    
    def test_read_csv_file_with_header(self, sample_csv_content):
        """Test reading a CSV file with header."""
        with patch('builtins.open', mock_open(read_data=sample_csv_content)):
            result = read_csv_file('test.csv', delimiter=',', has_header=True)
            
            assert 'headers' in result
            assert 'data' in result
            assert result['headers'] == ['Name', 'Age', 'City']
            assert len(result['data']) == 3
            assert result['data'][0] == ['John', '30', 'New York']
    
    def test_read_csv_file_without_header(self, sample_csv_content):
        """Test reading a CSV file without header."""
        with patch('builtins.open', mock_open(read_data=sample_csv_content)):
            result = read_csv_file('test.csv', delimiter=',', has_header=False)
            
            assert 'headers' in result
            assert 'data' in result
            assert result['headers'] == ['Column1', 'Column2', 'Column3']
            assert len(result['data']) == 4  # Including the header row as data
    
    def test_read_csv_file_with_skip_rows(self, sample_csv_content):
        """Test reading a CSV file with skipping rows."""
        with patch('builtins.open', mock_open(read_data=sample_csv_content)):
            result = read_csv_file('test.csv', delimiter=',', has_header=True, skip_rows=1)
            
            assert 'headers' in result
            assert 'data' in result
            assert result['headers'] == ['John', '30', 'New York']
            assert len(result['data']) == 2
    
    def test_read_csv_file_empty(self):
        """Test reading an empty CSV file."""
        with patch('builtins.open', mock_open(read_data="")):
            with pytest.raises(FileFormatError):
                read_csv_file('test.csv', has_header=True)
    
    def test_write_csv_file(self):
        """Test writing a CSV file."""
        headers = ['Name', 'Age', 'City']
        data = [
            ['John', '30', 'New York'],
            ['Jane', '25', 'Los Angeles'],
            ['Bob', '40', 'Chicago']
        ]
        
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            write_csv_file('test.csv', headers, data, delimiter=',')
            mock_file.assert_called_once_with('test.csv', 'w', encoding='utf-8', newline='')
    
    def test_load_json(self, sample_json_data):
        """Test loading JSON data from a file."""
        json_str = json.dumps(sample_json_data)
        with patch('builtins.open', mock_open(read_data=json_str)):
            data = load_json('test.json')
            assert data == sample_json_data
    
    def test_save_json(self, sample_json_data):
        """Test saving data to a JSON file."""
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            save_json('test.json', sample_json_data, indent=2)
            mock_file.assert_called_once_with('test.json', 'w', encoding='utf-8')
    
    def test_load_yaml(self, sample_yaml_data):
        """Test loading YAML data from a file."""
        yaml_str = yaml.dump(sample_yaml_data)
        with patch('builtins.open', mock_open(read_data=yaml_str)):
            data = load_yaml('test.yaml')
            assert data == sample_yaml_data
    
    def test_save_yaml(self, sample_yaml_data):
        """Test saving data to a YAML file."""
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            save_yaml('test.yaml', sample_yaml_data)
            mock_file.assert_called_once_with('test.yaml', 'w', encoding='utf-8')
    
    def test_integration_with_temp_files(self, sample_text, sample_json_data, sample_yaml_data):
        """Integration test with temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            text_file = os.path.join(temp_dir, 'test.txt')
            write_text_file(text_file, sample_text)
            assert read_text_file(text_file) == sample_text
            
            json_file = os.path.join(temp_dir, 'test.json')
            save_json(json_file, sample_json_data)
            assert load_json(json_file) == sample_json_data
            
            yaml_file = os.path.join(temp_dir, 'test.yaml')
            save_yaml(yaml_file, sample_yaml_data)
            assert load_yaml(yaml_file) == sample_yaml_data
