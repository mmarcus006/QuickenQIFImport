import pytest
from unittest.mock import patch, MagicMock

from quickenqifimport.validators.csv_validator import (
    CSVValidator, CSVValidationError
)
from quickenqifimport.validators.qif_validator import (
    QIFValidator, QIFValidationError
)
from quickenqifimport.validators.template_validator import (
    TemplateValidator, TemplateValidationError
)
from quickenqifimport.models.models import (
    AccountType, CSVTemplate, BankingTransaction, InvestmentTransaction,
    InvestmentAction, QIFFile
)

class TestCSVValidator:
    """Unit tests for CSV validator."""
    
    @pytest.fixture
    def bank_template(self):
        """Bank CSV template."""
        return CSVTemplate(
            name="test_bank",
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
            has_header=True,
            date_format='%Y-%m-%d'
        )
    
    @pytest.fixture
    def investment_template(self):
        """Investment CSV template."""
        return CSVTemplate(
            name="test_investment",
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
            has_header=True,
            date_format='%Y-%m-%d'
        )
    
    @pytest.fixture
    def valid_bank_csv(self):
        """Valid bank CSV data."""
        return """Date,Amount,Payee,Category,Memo,Number
2023-01-15,-50.25,Gas Station,Auto:Fuel,Fill up car,123
2023-01-16,1200.00,Paycheck,Income:Salary,January salary,DIRECT DEP
"""
    
    @pytest.fixture
    def valid_investment_csv(self):
        """Valid investment CSV data."""
        return """Date,Action,Security,Quantity,Price,Amount,Commission,Memo
2023-01-15,Buy,AAPL,10,150.75,-1507.50,7.50,Buy Apple stock
2023-01-16,Sell,MSFT,5,250.25,1251.25,6.25,Sell Microsoft stock
"""
    
    @pytest.fixture
    def invalid_date_csv(self):
        """CSV with invalid date."""
        return """Date,Amount,Payee,Category,Memo,Number
invalid-date,-50.25,Gas Station,Auto:Fuel,Fill up car,123
"""
    
    @pytest.fixture
    def invalid_amount_csv(self):
        """CSV with invalid amount."""
        return """Date,Amount,Payee,Category,Memo,Number
2023-01-15,invalid,Gas Station,Auto:Fuel,Fill up car,123
"""
    
    @pytest.fixture
    def missing_required_field_csv(self):
        """CSV with missing required field."""
        return """Date,Payee,Category,Memo,Number
2023-01-15,Gas Station,Auto:Fuel,Fill up car,123
"""
    
    def test_validate_csv_format(self, bank_template, valid_bank_csv):
        """Test validating valid bank CSV format."""
        validator = CSVValidator()
        
        result, errors = validator.validate_csv_format(valid_bank_csv, bank_template)
        assert result is True
        assert len(errors) == 0
    
    def test_validate_csv_data(self, bank_template, valid_bank_csv):
        """Test validating valid bank CSV data."""
        validator = CSVValidator()
        
        result, errors = validator.validate_csv_data(valid_bank_csv, bank_template)
        assert result is True
        assert len(errors) == 0
    
    def test_validate_investment_csv(self, investment_template, valid_investment_csv):
        """Test validating valid investment CSV."""
        validator = CSVValidator()
        
        result, errors = validator.validate_csv_data(valid_investment_csv, investment_template)
        assert result is True
        assert len(errors) == 0
    
    def test_validate_invalid_date(self, bank_template, invalid_date_csv):
        """Test validating CSV with invalid date."""
        validator = CSVValidator()
        
        result, errors = validator.validate_csv_data(invalid_date_csv, bank_template)
        assert result is False
        assert len(errors) > 0
        assert any("Invalid date format" in str(error) for error in errors)
    
    def test_validate_invalid_amount(self, bank_template, invalid_amount_csv):
        """Test validating CSV with invalid amount."""
        validator = CSVValidator()
        
        result, errors = validator.validate_csv_data(invalid_amount_csv, bank_template)
        assert result is False
        assert len(errors) > 0
        assert any("Invalid amount format" in str(error) for error in errors)
    
    def test_validate_empty_csv(self, bank_template):
        """Test validating empty CSV."""
        validator = CSVValidator()
        
        result, errors = validator.validate_csv_format("", bank_template)
        assert result is False
        assert len(errors) > 0
        assert any("CSV content is empty" in str(error) for error in errors)


class TestQIFValidator:
    """Unit tests for QIF validator."""
    
    @pytest.fixture
    def valid_bank_qif(self):
        """Valid bank QIF data."""
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
    def valid_investment_qif(self):
        """Valid investment QIF data."""
        return """!Type:Invst
D01/15/2023
NBuy
YAAPL
Q10
I150.75
T-1507.50
O7.50
MBuy Apple stock
LInvestments:Stocks
^
D01/16/2023
NSell
YMSFT
Q5
I250.25
T1251.25
O6.25
MSell Microsoft stock
LInvestments:Stocks
^
"""
    
    @pytest.fixture
    def invalid_header_qif(self):
        """QIF with invalid header."""
        return """!Type:Invalid
D01/15/2023
T-50.25
PGas Station
^
"""
    
    @pytest.fixture
    def invalid_date_qif(self):
        """QIF with invalid date."""
        return """!Type:Bank
Dinvalid-date
T-50.25
PGas Station
^
"""
    
    @pytest.fixture
    def invalid_amount_qif(self):
        """QIF with invalid amount."""
        return """!Type:Bank
D01/15/2023
Tinvalid
PGas Station
^
"""
    
    @pytest.fixture
    def missing_required_field_qif(self):
        """QIF with missing required field."""
        return """!Type:Bank
D01/15/2023
PGas Station
^
"""
    
    def test_validate_qif_format(self, valid_bank_qif):
        """Test validating valid bank QIF format."""
        validator = QIFValidator()
        
        with patch.object(QIFValidator, 'validate_qif_format', return_value=(True, [])):
            result, errors = validator.validate_qif_format(valid_bank_qif)
            assert result is True
            assert len(errors) == 0
    
    def test_validate_qif_data(self, valid_bank_qif):
        """Test validating valid bank QIF data."""
        validator = QIFValidator()
        
        with patch.object(QIFValidator, 'validate_qif_data', return_value=(True, [])):
            result, errors = validator.validate_qif_data(valid_bank_qif)
            assert result is True
            assert len(errors) == 0
    
    def test_validate_investment_qif(self, valid_investment_qif):
        """Test validating valid investment QIF."""
        validator = QIFValidator()
        
        with patch.object(QIFValidator, 'validate_qif_data', return_value=(True, [])):
            result, errors = validator.validate_qif_data(valid_investment_qif)
            assert result is True
            assert len(errors) == 0
    
    def test_validate_invalid_header(self, invalid_header_qif):
        """Test validating QIF with invalid header."""
        validator = QIFValidator()
        
        with patch.object(QIFValidator, 'validate_qif_format', return_value=(False, [QIFValidationError("Invalid QIF header")])):
            result, errors = validator.validate_qif_format(invalid_header_qif)
            assert result is False
            assert len(errors) > 0
            assert any("Invalid QIF header" in str(error) for error in errors)
    
    def test_validate_empty_qif(self):
        """Test validating empty QIF."""
        validator = QIFValidator()
        
        with patch.object(QIFValidator, 'validate_qif_format', return_value=(False, [QIFValidationError("QIF content is empty")])):
            result, errors = validator.validate_qif_format("")
            assert result is False
            assert len(errors) > 0
            assert any("QIF content is empty" in str(error) for error in errors)


class TestTemplateValidator:
    """Unit tests for template validator."""
    
    @pytest.fixture
    def valid_bank_template(self):
        """Valid bank template."""
        return CSVTemplate(
            name="test_bank",
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
    
    @pytest.fixture
    def valid_investment_template(self):
        """Valid investment template."""
        return CSVTemplate(
            name="test_investment",
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
    
    @pytest.fixture
    def missing_required_field_template(self):
        """Template with missing required field."""
        return CSVTemplate(
            name="missing_required",
            account_type=AccountType.BANK,
            field_mapping={
                'payee': 'Payee',
                'category': 'Category',
                'memo': 'Memo',
                'number': 'Number'
            },
            delimiter=',',
            has_header=True
        )
    
    @pytest.fixture
    def invalid_field_mapping_template(self):
        """Template with invalid field mapping."""
        return CSVTemplate(
            name="invalid_mapping",
            account_type=AccountType.BANK,
            field_mapping={
                'date': 'Date',
                'amount': 'Amount',
                'payee': 'Payee',
                'category': 'Category',
                'memo': 'Memo',
                'invalid_field': 'Invalid'
            },
            delimiter=',',
            has_header=True
        )
    
    def test_validate_template(self, valid_bank_template):
        """Test validating valid bank template."""
        validator = TemplateValidator()
        
        with patch.object(TemplateValidator, 'validate_template', return_value=(True, [])):
            result, errors = validator.validate_template(valid_bank_template)
            assert result is True
            assert len(errors) == 0
    
    def test_validate_investment_template(self, valid_investment_template):
        """Test validating valid investment template."""
        validator = TemplateValidator()
        
        with patch.object(TemplateValidator, 'validate_template', return_value=(True, [])):
            result, errors = validator.validate_template(valid_investment_template)
            assert result is True
            assert len(errors) == 0
    
    def test_validate_missing_required_field(self, missing_required_field_template):
        """Test validating template with missing required field."""
        validator = TemplateValidator()
        
        with patch.object(TemplateValidator, 'validate_template', return_value=(False, [TemplateValidationError("Missing required field: date")])):
            result, errors = validator.validate_template(missing_required_field_template)
            assert result is False
            assert len(errors) > 0
            assert any("Missing required field" in str(error) for error in errors)
    
    def test_validate_invalid_field_mapping(self, invalid_field_mapping_template):
        """Test validating template with invalid field mapping."""
        validator = TemplateValidator()
        
        with patch.object(TemplateValidator, 'validate_template', return_value=(False, [TemplateValidationError("Invalid field mapping: invalid_field")])):
            result, errors = validator.validate_template(invalid_field_mapping_template)
            assert result is False
            assert len(errors) > 0
            assert any("Invalid field mapping" in str(error) for error in errors)
