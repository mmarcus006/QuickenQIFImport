import pytest
from unittest.mock import patch, mock_open, MagicMock
import argparse
import sys
from io import StringIO

from quickenqifimport.cli import (
    parse_args, main, list_templates, detect_file_type, 
    convert_csv_to_qif, convert_qif_to_csv
)
from quickenqifimport.models.models import AccountType, CSVTemplate

class TestCLI:
    """Unit tests for CLI functionality."""
    
    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV content."""
        return """Date,Amount,Payee,Category,Memo,Number
2023-01-15,-50.25,Gas Station,Auto:Fuel,Fill up car,123
2023-01-16,1200.00,Paycheck,Income:Salary,January salary,DIRECT DEP
"""
    
    @pytest.fixture
    def sample_qif_content(self):
        """Sample QIF content."""
        return """!Type:Bank
D01/15/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
N123
^
D01/16/2023
T1200.00
PPaycheck
MJanuary salary
LIncome:Salary
NDIRECT DEP
^
"""
    
    @pytest.fixture
    def sample_templates(self):
        """Sample CSV templates."""
        return [
            CSVTemplate(
                name="bank",
                account_type=AccountType.BANK,
                field_mapping={
                    'date': 'Date',
                    'amount': 'Amount',
                    'payee': 'Payee',
                    'category': 'Category',
                    'memo': 'Memo',
                    'number': 'Number'
                },
                delimiter=',',
                has_header=True
            ),
            CSVTemplate(
                name="investment",
                account_type=AccountType.INVESTMENT,
                field_mapping={
                    'date': 'Date',
                    'action': 'Action',
                    'security': 'Security',
                    'quantity': 'Quantity',
                    'price': 'Price',
                    'amount': 'Amount',
                    'commission': 'Commission',
                    'memo': 'Memo'
                },
                delimiter=',',
                has_header=True
            )
        ]
    
    def test_parse_args_csv_to_qif(self):
        """Test parsing arguments for CSV to QIF conversion."""
        with patch('sys.argv', ['cli.py', 'convert', 'input.csv', 'output.qif', '--template', 'bank']):
            args = parse_args()
            
            assert args.command == 'convert'
            assert args.input_file == 'input.csv'
            assert args.output_file == 'output.qif'
            assert args.template == 'bank'
            assert args.account_type is None
    
    def test_parse_args_qif_to_csv(self):
        """Test parsing arguments for QIF to CSV conversion."""
        with patch('sys.argv', ['cli.py', 'convert', 'input.qif', 'output.csv', '--account-type', 'Bank']):
            args = parse_args()
            
            assert args.command == 'convert'
            assert args.input_file == 'input.qif'
            assert args.output_file == 'output.csv'
            assert args.account_type == 'Bank'
            assert args.template is None
    
    def test_parse_args_list_templates(self):
        """Test parsing arguments for listing templates."""
        with patch('sys.argv', ['cli.py', 'list-templates']):
            args = parse_args()
            
            assert args.command == 'list-templates'
    
    def test_detect_file_type_csv(self):
        """Test detecting CSV file type."""
        assert detect_file_type('file.csv') == 'csv'
        assert detect_file_type('file.CSV') == 'csv'
        assert detect_file_type('path/to/file.csv') == 'csv'
    
    def test_detect_file_type_qif(self):
        """Test detecting QIF file type."""
        assert detect_file_type('file.qif') == 'qif'
        assert detect_file_type('file.QIF') == 'qif'
        assert detect_file_type('path/to/file.qif') == 'qif'
    
    def test_detect_file_type_unknown(self):
        """Test detecting unknown file type."""
        assert detect_file_type('file.txt') == 'unknown'
        assert detect_file_type('file') == 'unknown'
    
    @patch('quickenqifimport.cli.get_available_templates')
    def test_list_templates(self, mock_get_templates, sample_templates, capsys):
        """Test listing templates."""
        mock_get_templates.return_value = sample_templates
        
        list_templates()
        
        captured = capsys.readouterr()
        assert "Available templates:" in captured.out
        assert "bank (Bank)" in captured.out
        assert "investment (Invst)" in captured.out
    
    @patch('quickenqifimport.cli.CSVToQIFService')
    @patch('quickenqifimport.cli.get_template_by_name')
    def test_convert_csv_to_qif(self, mock_get_template, mock_service, sample_templates, sample_csv_content):
        """Test converting CSV to QIF."""
        mock_get_template.return_value = sample_templates[0]
        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.convert.return_value = "QIF content"
        
        with patch('builtins.open', mock_open(read_data=sample_csv_content)) as mock_file:
            convert_csv_to_qif('input.csv', 'output.qif', 'bank')
            
            mock_get_template.assert_called_once_with('bank')
            mock_service.assert_called_once()
            mock_service_instance.convert.assert_called_once()
            mock_file.assert_any_call('input.csv', 'r', encoding='utf-8')
            mock_file.assert_any_call('output.qif', 'w', encoding='utf-8')
    
    @patch('quickenqifimport.cli.QIFToCSVService')
    def test_convert_qif_to_csv(self, mock_service, sample_qif_content):
        """Test converting QIF to CSV."""
        mock_service_instance = MagicMock()
        mock_service.return_value = mock_service_instance
        mock_service_instance.convert.return_value = "CSV content"
        
        with patch('builtins.open', mock_open(read_data=sample_qif_content)) as mock_file:
            convert_qif_to_csv('input.qif', 'output.csv', AccountType.BANK)
            
            mock_service.assert_called_once()
            mock_service_instance.convert.assert_called_once()
            mock_file.assert_any_call('input.qif', 'r', encoding='utf-8')
            mock_file.assert_any_call('output.csv', 'w', encoding='utf-8')
    
    @patch('quickenqifimport.cli.convert_csv_to_qif')
    @patch('quickenqifimport.cli.convert_qif_to_csv')
    @patch('quickenqifimport.cli.list_templates')
    @patch('quickenqifimport.cli.parse_args')
    def test_main_csv_to_qif(self, mock_parse_args, mock_list_templates, mock_convert_qif_to_csv, mock_convert_csv_to_qif):
        """Test main function for CSV to QIF conversion."""
        args = argparse.Namespace(
            command='convert',
            input_file='input.csv',
            output_file='output.qif',
            template='bank',
            account_type=None
        )
        mock_parse_args.return_value = args
        
        main()
        
        mock_convert_csv_to_qif.assert_called_once_with('input.csv', 'output.qif', 'bank')
        mock_convert_qif_to_csv.assert_not_called()
        mock_list_templates.assert_not_called()
    
    @patch('quickenqifimport.cli.convert_csv_to_qif')
    @patch('quickenqifimport.cli.convert_qif_to_csv')
    @patch('quickenqifimport.cli.list_templates')
    @patch('quickenqifimport.cli.parse_args')
    def test_main_qif_to_csv(self, mock_parse_args, mock_list_templates, mock_convert_qif_to_csv, mock_convert_csv_to_qif):
        """Test main function for QIF to CSV conversion."""
        args = argparse.Namespace(
            command='convert',
            input_file='input.qif',
            output_file='output.csv',
            template=None,
            account_type='Bank'
        )
        mock_parse_args.return_value = args
        
        main()
        
        mock_convert_qif_to_csv.assert_called_once_with('input.qif', 'output.csv', 'Bank')
        mock_convert_csv_to_qif.assert_not_called()
        mock_list_templates.assert_not_called()
    
    @patch('quickenqifimport.cli.convert_csv_to_qif')
    @patch('quickenqifimport.cli.convert_qif_to_csv')
    @patch('quickenqifimport.cli.list_templates')
    @patch('quickenqifimport.cli.parse_args')
    def test_main_list_templates(self, mock_parse_args, mock_list_templates, mock_convert_qif_to_csv, mock_convert_csv_to_qif):
        """Test main function for listing templates."""
        args = argparse.Namespace(
            command='list-templates'
        )
        mock_parse_args.return_value = args
        
        main()
        
        mock_list_templates.assert_called_once()
        mock_convert_csv_to_qif.assert_not_called()
        mock_convert_qif_to_csv.assert_not_called()
