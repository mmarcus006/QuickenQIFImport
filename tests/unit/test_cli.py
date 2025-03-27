import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from quickenqifimport.cli import (
    parse_args, main, convert_csv_to_qif, convert_qif_to_csv,
    get_account_type, load_template_from_arg
)
from quickenqifimport.models.models import CSVTemplate, AccountType

class TestCLI:
    """Unit tests for the CLI module."""
    
    def test_parse_args(self):
        """Test argument parsing."""
        with patch('sys.argv', ['qif_converter', 'input.csv', 'output.qif']):
            args = parse_args()
            assert args.input_file == 'input.csv'
            assert args.output_file == 'output.qif'
    
    def test_get_account_type(self):
        """Test account type conversion."""
        assert get_account_type('bank') == AccountType.BANK
        assert get_account_type('cash') == AccountType.CASH
        assert get_account_type('credit_card') == AccountType.CREDIT_CARD
        assert get_account_type('investment') == AccountType.INVESTMENT
        assert get_account_type('asset') == AccountType.ASSET
        assert get_account_type('liability') == AccountType.LIABILITY
        assert get_account_type('unknown') == AccountType.BANK  # Default
    
    @patch('quickenqifimport.cli.load_yaml')
    @patch('quickenqifimport.cli.load_template')
    @patch('os.path.exists')
    def test_load_template_from_arg_file(self, mock_exists, mock_load_template, mock_load_yaml):
        """Test loading template from file."""
        mock_exists.return_value = True
        mock_load_yaml.return_value = {
            'name': 'test_template',
            'account_type': 'Bank',
            'field_mapping': {'date': 'Date'}
        }
        
        template = load_template_from_arg('template.yaml', AccountType.BANK)
        
        mock_exists.assert_called_once_with('template.yaml')
        mock_load_yaml.assert_called_once_with('template.yaml')
        assert template.name == 'test_template'
    
    @patch('quickenqifimport.cli.load_template')
    @patch('os.path.exists')
    def test_load_template_from_arg_name(self, mock_exists, mock_load_template):
        """Test loading template from name."""
        mock_exists.return_value = False
        mock_template = MagicMock(spec=CSVTemplate)
        mock_load_template.return_value = mock_template
        
        template = load_template_from_arg('bank_template', AccountType.BANK)
        
        mock_exists.assert_called_once_with('bank_template')
        mock_load_template.assert_called_once_with('bank_template')
        assert template == mock_template
    
    @patch('quickenqifimport.cli.CSVToQIFService')
    def test_convert_csv_to_qif(self, mock_service_class):
        """Test CSV to QIF conversion."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_template = MagicMock(spec=CSVTemplate)
        
        with tempfile.NamedTemporaryFile(suffix='.csv') as input_file, \
             tempfile.NamedTemporaryFile(suffix='.qif') as output_file:
            
            convert_csv_to_qif(input_file.name, output_file.name, mock_template, 'Checking')
            
            mock_service.convert_csv_file_to_qif_file.assert_called_once_with(
                input_file.name, mock_template, output_file.name, 'Checking'
            )
    
    @patch('quickenqifimport.cli.QIFToCSVService')
    def test_convert_qif_to_csv(self, mock_service_class):
        """Test QIF to CSV conversion."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_template = MagicMock(spec=CSVTemplate)
        
        with tempfile.NamedTemporaryFile(suffix='.qif') as input_file, \
             tempfile.NamedTemporaryFile(suffix='.csv') as output_file:
            
            convert_qif_to_csv(input_file.name, output_file.name, mock_template, 'Checking')
            
            mock_service.convert_qif_file_to_csv_file.assert_called_once_with(
                input_file.name, mock_template, output_file.name, 'Checking'
            )
    
    @patch('quickenqifimport.cli.list_templates')
    def test_main_list_templates(self, mock_list_templates):
        """Test main function with list_templates flag."""
        mock_list_templates.return_value = ['bank_template', 'investment_template']
        
        with patch('sys.argv', ['qif_converter', 'input.csv', 'output.qif', '--list-templates']):
            with patch('builtins.print') as mock_print:
                main()
                
                mock_list_templates.assert_called_once()
                mock_print.assert_any_call("Available templates:")
    
    @patch('quickenqifimport.cli.convert_csv_to_qif')
    @patch('quickenqifimport.cli.convert_qif_to_csv')
    @patch('quickenqifimport.cli.load_template_from_arg')
    @patch('os.path.exists')
    def test_main_csv_to_qif(self, mock_exists, mock_load_template, mock_qif_to_csv, mock_csv_to_qif):
        """Test main function with CSV to QIF conversion."""
        mock_exists.return_value = True
        mock_template = MagicMock(spec=CSVTemplate)
        mock_load_template.return_value = mock_template
        
        with patch('sys.argv', ['qif_converter', 'input.csv', 'output.qif', '--template', 'bank_template']):
            main()
            
            mock_exists.assert_called_with('input.csv')
            mock_load_template.assert_called_once()
            mock_csv_to_qif.assert_called_once()
            mock_qif_to_csv.assert_not_called()
    
    @patch('quickenqifimport.cli.convert_csv_to_qif')
    @patch('quickenqifimport.cli.convert_qif_to_csv')
    @patch('quickenqifimport.cli.load_template_from_arg')
    @patch('os.path.exists')
    def test_main_qif_to_csv(self, mock_exists, mock_load_template, mock_qif_to_csv, mock_csv_to_qif):
        """Test main function with QIF to CSV conversion."""
        mock_exists.return_value = True
        mock_template = MagicMock(spec=CSVTemplate)
        mock_load_template.return_value = mock_template
        
        with patch('sys.argv', ['qif_converter', 'input.qif', 'output.csv', '--template', 'bank_template']):
            main()
            
            mock_exists.assert_called_with('input.qif')
            mock_load_template.assert_called_once()
            mock_qif_to_csv.assert_called_once()
            mock_csv_to_qif.assert_not_called()
