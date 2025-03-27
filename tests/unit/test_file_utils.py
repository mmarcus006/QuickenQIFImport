import pytest
import os
import tempfile
from unittest.mock import patch, mock_open

from quickenqifimport.utils.file_utils import (
    read_file, write_file, ensure_directory_exists,
    get_file_extension, is_csv_file, is_qif_file,
    get_template_directory, list_template_files
)

class TestFileUtils:
    """Unit tests for file utility functions."""
    
    def test_read_file(self):
        """Test reading file content."""
        test_content = "Line 1\nLine 2\nLine 3"
        
        with patch("builtins.open", mock_open(read_data=test_content)):
            content = read_file("/path/to/file.txt")
            assert content == test_content
    
    def test_write_file(self):
        """Test writing content to file."""
        test_content = "Line 1\nLine 2\nLine 3"
        
        mock = mock_open()
        with patch("builtins.open", mock):
            write_file("/path/to/file.txt", test_content)
            
        mock.assert_called_once_with("/path/to/file.txt", "w", encoding="utf-8")
        mock().write.assert_called_once_with(test_content)
    
    def test_ensure_directory_exists(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "test_dir")
            
            assert not os.path.exists(test_dir)
            
            ensure_directory_exists(test_dir)
            
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)
            
            ensure_directory_exists(test_dir)
    
    def test_get_file_extension(self):
        """Test extracting file extension."""
        assert get_file_extension("/path/to/file.txt") == ".txt"
        assert get_file_extension("/path/to/file.csv") == ".csv"
        assert get_file_extension("/path/to/file.qif") == ".qif"
        assert get_file_extension("/path/to/file") == ""
        assert get_file_extension("/path.to/file") == ""
    
    def test_is_csv_file(self):
        """Test CSV file detection."""
        assert is_csv_file("/path/to/file.csv") is True
        assert is_csv_file("/path/to/file.CSV") is True
        assert is_csv_file("/path/to/file.txt") is False
        assert is_csv_file("/path/to/file") is False
    
    def test_is_qif_file(self):
        """Test QIF file detection."""
        assert is_qif_file("/path/to/file.qif") is True
        assert is_qif_file("/path/to/file.QIF") is True
        assert is_qif_file("/path/to/file.txt") is False
        assert is_qif_file("/path/to/file") is False
    
    def test_get_template_directory(self):
        """Test getting template directory path."""
        with patch("os.path.dirname") as mock_dirname:
            mock_dirname.return_value = "/path/to/package"
            
            template_dir = get_template_directory()
            assert template_dir.endswith("templates")
    
    def test_list_template_files(self):
        """Test listing template files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            template1 = os.path.join(temp_dir, "template1.csv")
            template2 = os.path.join(temp_dir, "template2.csv")
            non_template = os.path.join(temp_dir, "file.txt")
            
            with open(template1, "w") as f:
                f.write("test")
            with open(template2, "w") as f:
                f.write("test")
            with open(non_template, "w") as f:
                f.write("test")
            
            with patch("quickenqifimport.utils.file_utils.get_template_directory") as mock_get_dir:
                mock_get_dir.return_value = temp_dir
                
                templates = list_template_files()
                
                assert len(templates) == 2
                assert os.path.basename(templates[0]) in ["template1.csv", "template2.csv"]
                assert os.path.basename(templates[1]) in ["template1.csv", "template2.csv"]
                assert os.path.basename(templates[0]) != os.path.basename(templates[1])
