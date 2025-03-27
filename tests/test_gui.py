import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

from src.quickenqifimport.models.qif_models import QIFAccountType
from src.quickenqifimport.models.csv_models import CSVTemplate


@unittest.skipIf(not TKINTER_AVAILABLE, "Tkinter is not available")
class TestGUI(unittest.TestCase):
    """Test cases for the GUI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        self.qif_file_path = os.path.join(self.temp_dir, "test.qif")
        self.csv_file_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(self.qif_file_path, 'w') as file:
            file.write("""!Type:Bank
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
""")
            
        with open(self.csv_file_path, 'w') as file:
            file.write("""Date,Amount,Description,Reference,Memo,Category,Account,Status
2023-01-15,100.00,Grocery Store,1234,Weekly shopping,Groceries,Checking,*
2023-01-20,-50.00,Gas Station,,Fuel purchase,Auto:Fuel,Checking,
""")
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('tkinter.Tk')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('src.quickenqifimport.ui.gui.GUI.show_message')
    def test_convert_qif_to_csv(self, mock_show_message, mock_save_dialog, mock_open_dialog, mock_tk):
        """Test converting QIF to CSV."""
        from src.quickenqifimport.ui.gui import GUI
        
        mock_open_dialog.return_value = self.qif_file_path
        output_path = os.path.join(self.temp_dir, "output.csv")
        mock_save_dialog.return_value = output_path
        
        gui = GUI()
        
        gui.convert_qif_to_csv()
        
        self.assertTrue(os.path.exists(output_path))
        mock_show_message.assert_called_once()
    
    @patch('tkinter.Tk')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.filedialog.asksaveasfilename')
    @patch('src.quickenqifimport.ui.gui.GUI.show_message')
    def test_convert_csv_to_qif(self, mock_show_message, mock_save_dialog, mock_open_dialog, mock_tk):
        """Test converting CSV to QIF."""
        from src.quickenqifimport.ui.gui import GUI
        
        mock_open_dialog.return_value = self.csv_file_path
        output_path = os.path.join(self.temp_dir, "output.qif")
        mock_save_dialog.return_value = output_path
        
        gui = GUI()
        
        gui.account_type_var = MagicMock()
        gui.account_type_var.get.return_value = "Bank"
        
        gui.convert_csv_to_qif()
        
        self.assertTrue(os.path.exists(output_path))
        mock_show_message.assert_called_once()
    
    @patch('tkinter.Tk')
    @patch('tkinter.messagebox.showinfo')
    def test_show_message(self, mock_showinfo, mock_tk):
        """Test showing a message."""
        from src.quickenqifimport.ui.gui import GUI
        
        gui = GUI()
        gui.show_message("Test Title", "Test Message")
        
        mock_showinfo.assert_called_once_with("Test Title", "Test Message")
    
    @patch('tkinter.Tk')
    @patch('tkinter.messagebox.showerror')
    def test_show_error(self, mock_showerror, mock_tk):
        """Test showing an error message."""
        from src.quickenqifimport.ui.gui import GUI
        
        gui = GUI()
        gui.show_error("Test Error")
        
        mock_showerror.assert_called_once_with("Error", "Test Error")
    
    @patch('tkinter.Tk')
    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_file(self, mock_open_dialog, mock_tk):
        """Test browsing for a file."""
        from src.quickenqifimport.ui.gui import GUI
        
        mock_open_dialog.return_value = self.csv_file_path
        
        gui = GUI()
        
        entry_mock = MagicMock()
        
        gui.browse_file(entry_mock, [("CSV Files", "*.csv")])
        
        entry_mock.delete.assert_called_once_with(0, 'end')
        entry_mock.insert.assert_called_once_with(0, self.csv_file_path)
        mock_open_dialog.assert_called_once()
    
    @patch('tkinter.Tk')
    def test_create_widgets(self, mock_tk):
        """Test widget creation."""
        from src.quickenqifimport.ui.gui import GUI
        
        gui = GUI()
        
        self.assertIsNotNone(gui.root)
        self.assertIsNotNone(gui.notebook)
        self.assertIsNotNone(gui.qif_to_csv_frame)
        self.assertIsNotNone(gui.csv_to_qif_frame)
    
    @patch('tkinter.Tk')
    @patch('src.quickenqifimport.ui.gui.GUI.create_qif_to_csv_tab')
    @patch('src.quickenqifimport.ui.gui.GUI.create_csv_to_qif_tab')
    @patch('src.quickenqifimport.ui.gui.GUI.create_template_tab')
    def test_create_tabs(self, mock_template_tab, mock_csv_to_qif_tab, mock_qif_to_csv_tab, mock_tk):
        """Test tab creation."""
        from src.quickenqifimport.ui.gui import GUI
        
        gui = GUI()
        
        mock_qif_to_csv_tab.assert_called_once()
        mock_csv_to_qif_tab.assert_called_once()
        mock_template_tab.assert_called_once()
    
    @patch('tkinter.Tk')
    @patch('src.quickenqifimport.ui.gui.GUI.run')
    def test_main(self, mock_run, mock_tk):
        """Test main function."""
        from src.quickenqifimport.ui.gui import main
        
        main()
        
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
