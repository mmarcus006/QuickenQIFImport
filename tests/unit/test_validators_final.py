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
    
    def test_validate_bank_csv(self, bank_template, valid_bank_csv):
        """Test validating valid bank CSV."""
        validator = CSVValidator()
        
        validator.validate(valid_bank_csv, bank_template)
    
    def test_validate_investment_csv(self, investment_template, valid_investment_csv):
        """Test validating valid investment CSV."""
        validator = CSVValidator()
        
        validator.validate(valid_investment_csv, investment_template)
    
    def test_validate_invalid_date(self, bank_template, invalid_date_csv):
        """Test validating CSV with invalid date."""
        validator = CSVValidator()
        
        with pytest.raises(CSVValidationError):
            validator.validate(invalid_date_csv, bank_template)
    
    def test_validate_invalid_amount(self, bank_template, invalid_amount_csv):
        """Test validating CSV with invalid amount."""
        validator = CSVValidator()
        
        with pytest.raises(CSVValidationError):
            validator.validate(invalid_amount_csv, bank_template)
    
    def test_validate_missing_required_field(self, bank_template, missing_required_field_csv):
        """Test validating CSV with missing required field."""
        validator = CSVValidator()
        
        with pytest.raises(CSVValidationError):
            validator.validate(missing_required_field_csv, bank_template)
    
    def test_validate_empty_csv(self, bank_template):
        """Test validating empty CSV."""
        validator = CSVValidator()
        
        with pytest.raises(CSVValidationError):
            validator.validate("", bank_template)


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
    
    def test_validate_bank_qif(self, valid_bank_qif):
        """Test validating valid bank QIF."""
        validator = QIFValidator()
        
        validator.validate(valid_bank_qif)
    
    def test_validate_investment_qif(self, valid_investment_qif):
        """Test validating valid investment QIF."""
        validator = QIFValidator()
        
        validator.validate(valid_investment_qif)
    
    def test_validate_invalid_header(self, invalid_header_qif):
        """Test validating QIF with invalid header."""
        validator = QIFValidator()
        
        with pytest.raises(QIFValidationError):
            validator.validate(invalid_header_qif)
    
    def test_validate_invalid_date(self, invalid_date_qif):
        """Test validating QIF with invalid date."""
        validator = QIFValidator()
        
        with pytest.raises(QIFValidationError):
            validator.validate(invalid_date_qif)
    
    def test_validate_invalid_amount(self, invalid_amount_qif):
        """Test validating QIF with invalid amount."""
        validator = QIFValidator()
        
        with pytest.raises(QIFValidationError):
            validator.validate(invalid_amount_qif)
    
    def test_validate_missing_required_field(self, missing_required_field_qif):
        """Test validating QIF with missing required field."""
        validator = QIFValidator()
        
        with pytest.raises(QIFValidationError):
            validator.validate(missing_required_field_qif)
    
    def test_validate_empty_qif(self):
        """Test validating empty QIF."""
        validator = QIFValidator()
        
        with pytest.raises(QIFValidationError):
            validator.validate("")


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
    
    def test_validate_bank_template(self, valid_bank_template):
        """Test validating valid bank template."""
        validator = TemplateValidator()
        
        validator.validate(valid_bank_template)
    
    def test_validate_investment_template(self, valid_investment_template):
        """Test validating valid investment template."""
        validator = TemplateValidator()
        
        validator.validate(valid_investment_template)
    
    def test_validate_missing_required_field(self, missing_required_field_template):
        """Test validating template with missing required field."""
        validator = TemplateValidator()
        
        with pytest.raises(TemplateValidationError):
            validator.validate(missing_required_field_template)
    
    def test_validate_invalid_field_mapping(self, invalid_field_mapping_template):
        """Test validating template with invalid field mapping."""
        validator = TemplateValidator()
        
        with pytest.raises(TemplateValidationError):
            validator.validate(invalid_field_mapping_template)
