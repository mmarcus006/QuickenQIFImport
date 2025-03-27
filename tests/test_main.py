import unittest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

from src.quickenqifimport.__main__ import main


class TestMain(unittest.TestCase):
    """Test cases for the main module."""
    
    @patch('sys.argv', ['quickenqifimport'])
    @patch('src.quickenqifimport.core.app.App.run_cli')
    def test_main_cli(self, mock_run_cli):
        """Test main function with CLI."""
        mock_run_cli.return_value = 0
        
        try:
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)
            
        mock_run_cli.assert_called_once()
    
    @patch('sys.argv', ['quickenqifimport', '--gui'])
    @patch('src.quickenqifimport.core.app.App.run_gui')
    @patch('src.quickenqifimport.ui.gui.TKINTER_AVAILABLE', True)
    def test_main_gui(self, mock_run_gui):
        """Test main function with GUI."""
        mock_run_gui.return_value = 0
        
        main()
        
        mock_run_gui.assert_called_once()
    
    @patch('sys.argv', ['quickenqifimport', '--unknown'])
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_unknown_arg(self, mock_stderr):
        """Test main function with unknown argument."""
        with self.assertRaises(SystemExit) as cm:
            main()
            
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("error: unrecognized arguments", mock_stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
