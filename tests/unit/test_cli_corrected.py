import pytest
from unittest.mock import patch, mock_open, MagicMock
import argparse
import sys
import os
from io import StringIO

from quickenqifimport.cli import (
    parse_args, main, detect_file_type, get_account_type,
    load_template_from_arg, convert_csv_to_qif, convert_qif_to_csv
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
    def sample_template(self):
        """Sample CSV template."""
        return CSVTemplate(
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
        )
    
    def test_detect_file_type(self):
        """Test detecting file type from extension."""
        assert detect_file_type('file.csv') == 'csv'
        assert detect_file_type('file.CSV') == 'csv'
        assert detect_file_type('file.qif') == 'qif'
        assert detect_file_type('file.QIF') == 'qif'
        assert detect_file_type('file.txt') == 'unknown'
        assert detect_file_type('file') == 'unknown'
    
    def test_get_account_type(self):
        """Test getting account type from string."""
        assert get_account_type('bank') == AccountType.BANK
        assert get_account_type('cash') == AccountType.CASH
        assert get_account_type('credit_card') == AccountType.CREDIT_CARD
        assert get_account_type('investment') == AccountType.INVESTMENT
        assert get_account_type('asset') == AccountType.ASSET
        assert get_account_type('liability') == AccountType.LIABILITY
        assert get_account_type('invalid') == AccountType.BANK  # Default value
    
    def test_parse_args(self):
        """Test parsing arguments."""
        with patch('sys.argv', ['cli.py', 'input.csv', 'output.qif', '--template', 'bank']):
            args = parse_args()
            
            assert args.input_file == 'input.csv'
            assert args.output_file == 'output.qif'
            assert args.template == 'bank'
            assert args.type == 'bank'  # Default value
    
    def test_load_template_from_arg_file(self, sample_template):
        """Test loading template from file path."""
        with patch('os.path.exists', return_value=True), \
             patch('quickenqifimport.cli.load_yaml', return_value=sample_template.model_dump()), \
             patch('quickenqifimport.cli.CSVTemplate', return_value=sample_template):
            
            template = load_template_from_arg('template.yaml', AccountType.BANK)
            assert template == sample_template
    
    def test_load_template_from_arg_name(self, sample_template):
        """Test loading template from name."""
        with patch('os.path.exists', return_value=False), \
             patch('quickenqifimport.cli.load_template', return_value=sample_template):
            
            template = load_template_from_arg('bank', AccountType.BANK)
            assert template == sample_template
    
    def test_convert_csv_to_qif(self, sample_csv_content, sample_template):
        """Test converting CSV to QIF."""
        with patch('quickenqifimport.cli.CSVToQIFService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            convert_csv_to_qif('input.csv', 'output.qif', sample_template)
            
            mock_service_class.assert_called_once()
            mock_service.convert_csv_file_to_qif_file.assert_called_once()
    
    def test_convert_qif_to_csv(self, sample_qif_content, sample_template):
        """Test converting QIF to CSV."""
        with patch('quickenqifimport.cli.QIFToCSVService') as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            
            convert_qif_to_csv('input.qif', 'output.csv', sample_template)
            
            mock_service_class.assert_called_once()
            mock_service.convert_qif_file_to_csv_file.assert_called_once()
    
    def test_main_csv_to_qif(self, sample_template):
        """Test main function for CSV to QIF conversion."""
        args = MagicMock()
        args.input_file = 'input.csv'
        args.output_file = 'output.qif'
        args.template = 'bank'
        args.type = 'bank'
        args.account = None
        args.list_templates = False
        args.verbose = False
        args.direction = None
        
        with patch('quickenqifimport.cli.parse_args', return_value=args), \
             patch('os.path.exists', return_value=True), \
             patch('quickenqifimport.cli.load_template_from_arg', return_value=sample_template), \
             patch('quickenqifimport.cli.convert_csv_to_qif') as mock_convert_csv_to_qif, \
             patch('quickenqifimport.cli.convert_qif_to_csv') as mock_convert_qif_to_csv:
            
            main()
            
            mock_convert_csv_to_qif.assert_called_once()
            mock_convert_qif_to_csv.assert_not_called()
    
    def test_main_qif_to_csv(self, sample_template):
        """Test main function for QIF to CSV conversion."""
        args = MagicMock()
        args.input_file = 'input.qif'
        args.output_file = 'output.csv'
        args.template = 'bank'
        args.type = 'bank'
        args.account = None
        args.list_templates = False
        args.verbose = False
        args.direction = None
        
        with patch('quickenqifimport.cli.parse_args', return_value=args), \
             patch('os.path.exists', return_value=True), \
             patch('quickenqifimport.cli.load_template_from_arg', return_value=sample_template), \
             patch('quickenqifimport.cli.convert_csv_to_qif') as mock_convert_csv_to_qif, \
             patch('quickenqifimport.cli.convert_qif_to_csv') as mock_convert_qif_to_csv:
            
            main()
            
            mock_convert_qif_to_csv.assert_called_once()
            mock_convert_csv_to_qif.assert_not_called()
    
    def test_main_list_templates(self):
        """Test main function for listing templates."""
        args = MagicMock()
        args.list_templates = True
        args.verbose = False
        
        with patch('quickenqifimport.cli.parse_args', return_value=args), \
             patch('quickenqifimport.cli.list_templates', return_value=['bank', 'investment']) as mock_list_templates, \
             patch('builtins.print') as mock_print:
            
            main()
            
            mock_list_templates.assert_called_once()
            mock_print.assert_any_call("Available templates:")
