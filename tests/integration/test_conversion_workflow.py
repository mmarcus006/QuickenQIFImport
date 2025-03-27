import pytest
import os
import tempfile
from datetime import datetime

from quickenqifimport.services.csv_to_qif_service import CSVToQIFService
from quickenqifimport.services.qif_to_csv_service import QIFToCSVService
from quickenqifimport.models.models import CSVTemplate, AccountType
from quickenqifimport.utils.template_utils import create_default_templates, load_template

class TestConversionWorkflow:
    """Integration tests for the conversion workflow."""
    
    @pytest.fixture
    def bank_csv_content(self):
        """Fixture for bank CSV content."""
        return """Date,Amount,Description,Reference,Notes,Category
2023-01-01,100.50,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel
2023-01-03,1200.00,Paycheck,DIRECT DEP,January salary,Income:Salary
"""
    
    @pytest.fixture
    def investment_csv_content(self):
        """Fixture for investment CSV content."""
        return """Date,Action,Security,Quantity,Price,Amount,Commission,Description,Memo,Category
2023-01-01,Buy,AAPL,10,150.75,-1507.50,7.50,Broker,Buy Apple stock,Investments:Stocks
2023-01-02,Sell,MSFT,5,250.25,1251.25,6.25,Broker,Sell Microsoft stock,Investments:Stocks
2023-01-03,Div,VTI,,,,0,Vanguard,Dividend payment,Income:Dividends
"""
    
    @pytest.fixture
    def bank_template(self):
        """Fixture for bank template."""
        return CSVTemplate(
            name="Test Bank Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
    
    @pytest.fixture
    def investment_template(self):
        """Fixture for investment template."""
        return CSVTemplate(
            name="Test Investment Template",
            account_type=AccountType.INVESTMENT,
            field_mapping={
                "date": "Date",
                "action": "Action",
                "security": "Security",
                "quantity": "Quantity",
                "price": "Price",
                "amount": "Amount",
                "commission": "Commission",
                "payee": "Description",
                "memo": "Memo",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
    
    def test_bank_csv_to_qif_to_csv_roundtrip(self, bank_csv_content, bank_template):
        """Test bank CSV to QIF to CSV roundtrip conversion."""
        csv_to_qif_service = CSVToQIFService()
        qif_to_csv_service = QIFToCSVService()
        
        qif_content = csv_to_qif_service.convert_csv_to_qif(bank_csv_content, bank_template, "Checking")
        
        csv_content = qif_to_csv_service.convert_qif_to_csv(qif_content, bank_template, "Checking")
        
        assert "Date,Amount,Description,Reference,Notes,Category" in csv_content
        assert "2023-01-01,100.5,Grocery Store,123,Weekly groceries,Food:Groceries" in csv_content
        assert "2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel" in csv_content
        assert "2023-01-03,1200.0,Paycheck,DIRECT DEP,January salary,Income:Salary" in csv_content
    
    def test_investment_csv_to_qif_to_csv_roundtrip(self, investment_csv_content, investment_template):
        """Test investment CSV to QIF to CSV roundtrip conversion."""
        csv_to_qif_service = CSVToQIFService()
        qif_to_csv_service = QIFToCSVService()
        
        qif_content = csv_to_qif_service.convert_csv_to_qif(investment_csv_content, investment_template, "Investments")
        
        csv_content = qif_to_csv_service.convert_qif_to_csv(qif_content, investment_template, "Investments")
        
        assert "Date,Action,Security,Quantity,Price,Amount,Commission,Description,Memo,Category" in csv_content
        assert "2023-01-01,Buy,AAPL,10,150.75,-1507.5,7.5,Broker,Buy Apple stock,Investments:Stocks" in csv_content
        assert "2023-01-02,Sell,MSFT,5,250.25,1251.25,6.25,Broker,Sell Microsoft stock,Investments:Stocks" in csv_content
        assert "2023-01-03,Div,VTI,,,,0.0,Vanguard,Dividend payment,Income:Dividends" in csv_content
    
    def test_file_based_conversion_workflow(self, bank_csv_content, bank_template):
        """Test file-based conversion workflow."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as csv_file, \
             tempfile.NamedTemporaryFile(suffix=".qif", delete=False) as qif_file, \
             tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as output_csv_file:
            
            csv_file.write(bank_csv_content.encode())
            csv_file.flush()
            
            try:
                csv_to_qif_service = CSVToQIFService()
                qif_to_csv_service = QIFToCSVService()
                
                csv_to_qif_service.convert_csv_file_to_qif_file(
                    csv_file.name, bank_template, qif_file.name, "Checking"
                )
                
                qif_to_csv_service.convert_qif_file_to_csv_file(
                    qif_file.name, bank_template, output_csv_file.name, "Checking"
                )
                
                with open(output_csv_file.name, "r") as f:
                    output_csv_content = f.read()
                
                assert "Date,Amount,Description,Reference,Notes,Category" in output_csv_content
                assert "2023-01-01,100.5,Grocery Store,123,Weekly groceries,Food:Groceries" in output_csv_content
                assert "2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel" in output_csv_content
                assert "2023-01-03,1200.0,Paycheck,DIRECT DEP,January salary,Income:Salary" in output_csv_content
                
            finally:
                os.unlink(csv_file.name)
                os.unlink(qif_file.name)
                os.unlink(output_csv_file.name)
    
    def test_default_templates_workflow(self):
        """Test workflow with default templates."""
        bank_template = CSVTemplate(
            name="Generic Bank Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "category": "Category",
                "memo": "Memo"
            },
            date_format="%Y-%m-%d"
        )
        
        bank_csv_content = """Date,Amount,Description,Category,Memo
2023-01-01,100.50,Grocery Store,Food:Groceries,Weekly groceries
2023-01-02,-50.25,Gas Station,Auto:Fuel,Fill up car
"""
        
        csv_to_qif_service = CSVToQIFService()
        qif_to_csv_service = QIFToCSVService()
        
        qif_content = csv_to_qif_service.convert_csv_to_qif(bank_csv_content, bank_template, "Checking")
        
        csv_content = qif_to_csv_service.convert_qif_to_csv(qif_content, bank_template, "Checking")
        
        assert "Date,Amount,Description,Category,Memo" in csv_content
        assert "2023-01-01,100.5,Grocery Store,Food:Groceries,Weekly groceries" in csv_content
        assert "2023-01-02,-50.25,Gas Station,Auto:Fuel,Fill up car" in csv_content
    
    def test_error_handling_workflow(self, bank_template):
        """Test error handling in the conversion workflow."""
        invalid_csv_content = """Date,Amount,Description
invalid-date,100.50,Grocery Store
2023-01-02,-50.25,Gas Station
"""
        
        csv_to_qif_service = CSVToQIFService()
        
        with pytest.raises(Exception):
            csv_to_qif_service.convert_csv_to_qif(invalid_csv_content, bank_template)
        
        invalid_qif_content = """!Type:Bank
Dinvalid-date
T100.50
PGrocery Store
^
"""
        
        qif_to_csv_service = QIFToCSVService()
        
        with pytest.raises(Exception):
            qif_to_csv_service.convert_qif_to_csv(invalid_qif_content, bank_template)
