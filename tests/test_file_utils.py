import unittest
import os
import tempfile
import shutil
import json
from unittest.mock import patch, mock_open

from src.quickenqifimport.utils.file_utils import FileUtils
from src.quickenqifimport.models.csv_models import CSVTemplate


class TestFileUtils(unittest.TestCase):
    """Test cases for file_utils module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        self.qif_file_path = os.path.join(self.temp_dir, "test.qif")
        self.csv_file_path = os.path.join(self.temp_dir, "test.csv")
        self.txt_file_path = os.path.join(self.temp_dir, "test.txt")
        
        with open(self.qif_file_path, 'w') as file:
            file.write("!Type:Bank\nD01/15/2023\nT100.00\n^")
            
        with open(self.csv_file_path, 'w') as file:
            file.write("Date,Amount,Description\n01/15/2023,100.00,Test\n")
            
        with open(self.txt_file_path, 'w') as file:
            file.write("This is a test file.")
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_ensure_directory_exists(self):
        """Test ensuring a directory exists."""
        dir_path = os.path.join(self.temp_dir, "test_dir")
        
        self.assertFalse(os.path.exists(dir_path))
        
        FileUtils.ensure_directory_exists(dir_path)
        
        self.assertTrue(os.path.exists(dir_path))
        self.assertTrue(os.path.isdir(dir_path))
        
        FileUtils.ensure_directory_exists(dir_path)
        self.assertTrue(os.path.exists(dir_path))
    
    def test_get_file_extension(self):
        """Test getting file extensions."""
        self.assertEqual(FileUtils.get_file_extension(self.qif_file_path), "qif")
        self.assertEqual(FileUtils.get_file_extension(self.csv_file_path), "csv")
        self.assertEqual(FileUtils.get_file_extension(self.txt_file_path), "txt")
        self.assertEqual(FileUtils.get_file_extension("file"), "")
        self.assertEqual(FileUtils.get_file_extension("file."), "")
        self.assertEqual(FileUtils.get_file_extension("path/to/file.txt"), "txt")
    
    def test_is_qif_file(self):
        """Test checking if a file is a QIF file."""
        self.assertTrue(FileUtils.is_qif_file(self.qif_file_path))
        self.assertTrue(FileUtils.is_qif_file("file.qif"))
        self.assertTrue(FileUtils.is_qif_file("path/to/file.qif"))
        self.assertTrue(FileUtils.is_qif_file("file.QIF"))
        
        self.assertFalse(FileUtils.is_qif_file(self.csv_file_path))
        self.assertFalse(FileUtils.is_qif_file(self.txt_file_path))
        self.assertFalse(FileUtils.is_qif_file("file"))
    
    def test_is_csv_file(self):
        """Test checking if a file is a CSV file."""
        self.assertTrue(FileUtils.is_csv_file(self.csv_file_path))
        self.assertTrue(FileUtils.is_csv_file("file.csv"))
        self.assertTrue(FileUtils.is_csv_file("path/to/file.csv"))
        self.assertTrue(FileUtils.is_csv_file("file.CSV"))
        
        self.assertFalse(FileUtils.is_csv_file(self.qif_file_path))
        self.assertFalse(FileUtils.is_csv_file(self.txt_file_path))
        self.assertFalse(FileUtils.is_csv_file("file"))
    
    def test_save_and_load_template(self):
        """Test saving and loading templates."""
        template = CSVTemplate(
            name="Test",
            account_type="Bank",
            field_mapping={
                "Date": "date",
                "Amount": "amount",
                "Description": "payee"
            },
            description="Test template",
            date_format="%Y-%m-%d",
            delimiter=","
        )
        
        file_path = os.path.join(self.temp_dir, "test_template.json")
        
        FileUtils.save_template(template, file_path)
        
        self.assertTrue(os.path.exists(file_path))
        
        loaded_template = FileUtils.load_template(file_path)
        
        self.assertEqual(loaded_template.name, template.name)
        self.assertEqual(loaded_template.account_type, template.account_type)
        self.assertEqual(loaded_template.field_mapping, template.field_mapping)
        self.assertEqual(loaded_template.description, template.description)
        self.assertEqual(loaded_template.date_format, template.date_format)
        self.assertEqual(loaded_template.delimiter, template.delimiter)
    
    def test_list_templates(self):
        """Test listing templates."""
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f"template{i}.json")
            with open(file_path, 'w') as file:
                file.write("{}")
                
        templates = FileUtils.list_templates(self.temp_dir)
        
        self.assertEqual(len(templates), 3)
        for i in range(3):
            self.assertIn(f"template{i}.json", templates)
        
        with self.assertRaises(FileNotFoundError):
            FileUtils.list_templates(os.path.join(self.temp_dir, "nonexistent"))
    
    def test_detect_csv_delimiter(self):
        """Test detecting CSV delimiter."""
        comma_file = os.path.join(self.temp_dir, "comma.csv")
        semicolon_file = os.path.join(self.temp_dir, "semicolon.csv")
        tab_file = os.path.join(self.temp_dir, "tab.csv")
        pipe_file = os.path.join(self.temp_dir, "pipe.csv")
        
        with open(comma_file, 'w') as file:
            file.write("Date,Amount,Description\n01/15/2023,100.00,Test\n")
            
        with open(semicolon_file, 'w') as file:
            file.write("Date;Amount;Description\n01/15/2023;100.00;Test\n")
            
        with open(tab_file, 'w') as file:
            file.write("Date\tAmount\tDescription\n01/15/2023\t100.00\tTest\n")
            
        with open(pipe_file, 'w') as file:
            file.write("Date|Amount|Description\n01/15/2023|100.00|Test\n")
        
        self.assertEqual(FileUtils.detect_csv_delimiter(comma_file), ",")
        self.assertEqual(FileUtils.detect_csv_delimiter(semicolon_file), ";")
        self.assertEqual(FileUtils.detect_csv_delimiter(tab_file), "\t")
        self.assertEqual(FileUtils.detect_csv_delimiter(pipe_file), "|")
        
        no_delimiter_file = os.path.join(self.temp_dir, "no_delimiter.csv")
        with open(no_delimiter_file, 'w') as file:
            file.write("This is a test file with no delimiters\n")
            
        self.assertEqual(FileUtils.detect_csv_delimiter(no_delimiter_file), ",")
    
    def test_get_csv_headers(self):
        """Test getting CSV headers."""
        comma_file = os.path.join(self.temp_dir, "comma.csv")
        semicolon_file = os.path.join(self.temp_dir, "semicolon.csv")
        
        with open(comma_file, 'w') as file:
            file.write("Date,Amount,Description\n01/15/2023,100.00,Test\n")
            
        with open(semicolon_file, 'w') as file:
            file.write("Date;Amount;Description\n01/15/2023;100.00;Test\n")
        
        headers = FileUtils.get_csv_headers(comma_file)
        self.assertEqual(headers, ["Date", "Amount", "Description"])
        
        headers = FileUtils.get_csv_headers(semicolon_file, ";")
        self.assertEqual(headers, ["Date", "Amount", "Description"])
        
        with self.assertRaises(FileNotFoundError):
            FileUtils.get_csv_headers(os.path.join(self.temp_dir, "nonexistent.csv"))


if __name__ == "__main__":
    unittest.main()
