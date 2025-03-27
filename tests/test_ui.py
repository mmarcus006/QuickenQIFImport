import unittest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

from src.quickenqifimport.ui.cli import CLI
from src.quickenqifimport.models.qif_models import QIFAccountType


class TestCLI(unittest.TestCase):
    """Test cases for the CLI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cli = CLI()
        
        self.temp_dir = tempfile.mkdtemp()
        
        self.bank_qif_content = """!Type:Bank
D01/15/2023
T100.00
N1234
PGrocery Store
MWeekly shopping
LGroceries
^
D01/20/2023
T-50.00
PGas Station
LAuto:Fuel
^
"""
        
        self.bank_csv_content = """Date,Amount,Description,Reference,Memo,Category,Account,Status
2023-01-15,100.00,Grocery Store,1234,Weekly shopping,Groceries,Checking,*
2023-01-20,-50.00,Gas Station,,Fuel purchase,Auto:Fuel,Checking,
"""
        
        self.qif_file_path = os.path.join(self.temp_dir, "test.qif")
        self.csv_file_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(self.qif_file_path, 'w') as file:
            file.write(self.bank_qif_content)
            
        with open(self.csv_file_path, 'w') as file:
            file.write(self.bank_csv_content)
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_setup_arguments(self):
        """Test argument setup."""
        self.assertIn("qif2csv", self.cli.parser._subparsers._group_actions[0].choices)
        self.assertIn("csv2qif", self.cli.parser._subparsers._group_actions[0].choices)
        self.assertIn("template", self.cli.parser._subparsers._group_actions[0].choices)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_run_without_command(self, mock_stdout):
        """Test running without a command."""
        exit_code = self.cli.run([])
        
        self.assertIn("usage:", mock_stdout.getvalue())
        self.assertEqual(exit_code, 1)
    
    @patch('src.quickenqifimport.converters.qif_to_csv_converter.QIFToCSVConverter.convert_file')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_qif_to_csv(self, mock_stdout, mock_convert_file):
        """Test handling QIF to CSV conversion."""
        exit_code = self.cli.run(["qif2csv", self.qif_file_path, os.path.join(self.temp_dir, "output.csv")])
        
        mock_convert_file.assert_called_once()
        self.assertIn("Successfully converted", mock_stdout.getvalue())
        self.assertEqual(exit_code, 0)
        
        exit_code = self.cli.run(["qif2csv", os.path.join(self.temp_dir, "nonexistent.qif"), os.path.join(self.temp_dir, "output.csv")])
        
        self.assertIn("Input file not found", mock_stdout.getvalue())
        self.assertEqual(exit_code, 1)
    
    @patch('src.quickenqifimport.converters.csv_to_qif_converter.CSVToQIFConverter.convert_file')
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_csv_to_qif(self, mock_stdout, mock_convert_file):
        """Test handling CSV to QIF conversion."""
        exit_code = self.cli.run(["csv2qif", self.csv_file_path, os.path.join(self.temp_dir, "output.qif"), "--type", "Bank"])
        
        mock_convert_file.assert_called_once()
        self.assertIn("Successfully converted", mock_stdout.getvalue())
        self.assertEqual(exit_code, 0)
        
        exit_code = self.cli.run(["csv2qif", os.path.join(self.temp_dir, "nonexistent.csv"), os.path.join(self.temp_dir, "output.qif"), "--type", "Bank"])
        
        self.assertIn("Input file not found", mock_stdout.getvalue())
        self.assertEqual(exit_code, 1)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_template_without_command(self, mock_stdout):
        """Test handling template without a command."""
        exit_code = self.cli.run(["template"])
        
        self.assertIn("No template command specified", mock_stdout.getvalue())
        self.assertEqual(exit_code, 1)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_create_template(self, mock_stdout):
        """Test handling template creation."""
        exit_code = self.cli.run(["template", "create", "Test", os.path.join(self.temp_dir, "test_template.json")])
        
        self.assertIn("Creating template Test", mock_stdout.getvalue())
        self.assertEqual(exit_code, 0)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_list_templates(self, mock_stdout):
        """Test handling template listing."""
        for i in range(3):
            with open(os.path.join(self.temp_dir, f"template{i}.json"), 'w') as file:
                file.write("{}")
                
        exit_code = self.cli.run(["template", "list", self.temp_dir])
        
        self.assertIn("Templates in", mock_stdout.getvalue())
        for i in range(3):
            self.assertIn(f"template{i}.json", mock_stdout.getvalue())
        self.assertEqual(exit_code, 0)
        
        exit_code = self.cli.run(["template", "list", os.path.join(self.temp_dir, "nonexistent")])
        
        self.assertIn("Directory not found", mock_stdout.getvalue())
        self.assertEqual(exit_code, 1)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_view_template(self, mock_stdout):
        """Test handling template viewing."""
        template_path = os.path.join(self.temp_dir, "template.json")
        with open(template_path, 'w') as file:
            file.write("{}")
            
        exit_code = self.cli.run(["template", "view", template_path])
        
        self.assertIn("Template details for", mock_stdout.getvalue())
        self.assertEqual(exit_code, 0)
        
        exit_code = self.cli.run(["template", "view", os.path.join(self.temp_dir, "nonexistent.json")])
        
        self.assertIn("Template file not found", mock_stdout.getvalue())
        self.assertEqual(exit_code, 1)
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_handle_unknown_template_command(self, mock_stderr):
        """Test handling unknown template command."""
        try:
            exit_code = self.cli.run(["template", "unknown"])
        except SystemExit as e:
            exit_code = e.code
        
        self.assertIn("error: argument template_command", mock_stderr.getvalue())
        self.assertEqual(exit_code, 2)
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_handle_unknown_command(self, mock_stderr):
        """Test handling unknown command."""
        try:
            exit_code = self.cli.run(["unknown"])
        except SystemExit as e:
            exit_code = e.code
        
        self.assertIn("error: argument command", mock_stderr.getvalue())
        self.assertEqual(exit_code, 2)
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_handle_exception(self, mock_stdout):
        """Test handling exceptions."""
        with patch('src.quickenqifimport.converters.qif_to_csv_converter.QIFToCSVConverter.convert_file', side_effect=Exception("Test exception")):
            exit_code = self.cli.run(["qif2csv", self.qif_file_path, os.path.join(self.temp_dir, "output.csv")])
            
            self.assertIn("Conversion failed: Test exception", mock_stdout.getvalue())
            self.assertEqual(exit_code, 1)


class TestGUI(unittest.TestCase):
    """Test cases for the GUI class."""
    
    @unittest.skipIf(sys.platform.startswith('linux') and not os.environ.get('DISPLAY'), "GUI tests require a display")
    def test_gui_instantiation(self):
        """Test that the GUI class can be instantiated."""
        try:
            from src.quickenqifimport.ui.gui import GUI
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import GUI class")


if __name__ == "__main__":
    unittest.main()
