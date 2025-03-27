import pytest
from datetime import datetime
import io
import csv

from quickenqifimport.generators.csv_generator import CSVGenerator, CSVGeneratorError
from quickenqifimport.generators.qif_generator import QIFGenerator, QIFGeneratorError
from quickenqifimport.models.models import (
    CSVTemplate, AccountType, BankingTransaction, InvestmentTransaction,
    SplitTransaction, QIFFile, AccountDefinition
)

class TestCSVGenerator:
    """Tests for the CSVGenerator class."""
    
    def test_generate_banking_csv(self):
        """Test generating a CSV file from banking transactions."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Grocery Store",
                number="123",
                memo="Weekly groceries",
                category="Food:Groceries"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 2),
                amount=-50.25,
                payee="Gas Station",
                memo="Fill up car",
                category="Auto:Fuel"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 3),
                amount=1200.00,
                payee="Paycheck",
                number="DIRECT DEP",
                memo="January salary",
                category="Income:Salary"
            )
        ]
        
        template = CSVTemplate(
            name="Test Template",
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
        
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv(transactions, template)
        
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        
        assert reader.fieldnames == ["Date", "Amount", "Description", "Reference", "Notes", "Category"]
        
        assert len(rows) == 3
        
        assert rows[0]["Date"] == "2023-01-01"
        assert rows[0]["Amount"] == "100.5"
        assert rows[0]["Description"] == "Grocery Store"
        assert rows[0]["Reference"] == "123"
        assert rows[0]["Notes"] == "Weekly groceries"
        assert rows[0]["Category"] == "Food:Groceries"
        
        assert rows[1]["Date"] == "2023-01-02"
        assert rows[1]["Amount"] == "-50.25"
        assert rows[1]["Description"] == "Gas Station"
        assert rows[1]["Reference"] == ""  # Empty field
        assert rows[1]["Notes"] == "Fill up car"
        assert rows[1]["Category"] == "Auto:Fuel"
    
    def test_generate_investment_csv(self):
        """Test generating a CSV file from investment transactions."""
        transactions = [
            InvestmentTransaction(
                date=datetime(2023, 1, 1),
                action="Buy",
                security="AAPL",
                quantity=10,
                price=150.75,
                amount=-1507.50,
                commission=7.50,
                payee="Broker",
                memo="Buy Apple stock",
                category="Investments:Stocks"
            ),
            InvestmentTransaction(
                date=datetime(2023, 1, 2),
                action="Sell",
                security="MSFT",
                quantity=5,
                price=250.25,
                amount=1251.25,
                commission=6.25,
                payee="Broker",
                memo="Sell Microsoft stock",
                category="Investments:Stocks"
            ),
            InvestmentTransaction(
                date=datetime(2023, 1, 3),
                action="Div",
                security="VTI",
                amount=25.00,
                payee="Vanguard",
                memo="Dividend payment",
                category="Income:Dividends"
            )
        ]
        
        template = CSVTemplate(
            name="Test Template",
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
        
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv(transactions, template)
        
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)
        
        assert reader.fieldnames == [
            "Date", "Action", "Security", "Quantity", "Price", "Amount", 
            "Commission", "Description", "Memo", "Category"
        ]
        
        assert len(rows) == 3
        
        assert rows[0]["Date"] == "2023-01-01"
        assert rows[0]["Action"] == "Buy"
        assert rows[0]["Security"] == "AAPL"
        assert rows[0]["Quantity"] == "10"
        assert rows[0]["Price"] == "150.75"
        assert rows[0]["Amount"] == "-1507.5"
        assert rows[0]["Commission"] == "7.5"
        assert rows[0]["Description"] == "Broker"
        assert rows[0]["Memo"] == "Buy Apple stock"
        assert rows[0]["Category"] == "Investments:Stocks"
        
        assert rows[2]["Date"] == "2023-01-03"
        assert rows[2]["Action"] == "Div"
        assert rows[2]["Security"] == "VTI"
        assert rows[2]["Quantity"] == ""  # Empty field
        assert rows[2]["Price"] == ""  # Empty field
        assert rows[2]["Amount"] == "25.0"
        assert rows[2]["Commission"] == ""  # Empty field
    
    def test_generate_csv_with_custom_delimiter(self):
        """Test generating a CSV file with a custom delimiter."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Grocery Store",
                memo="Weekly groceries"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 2),
                amount=-50.25,
                payee="Gas Station",
                memo="Fill up car"
            )
        ]
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            delimiter=";",
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "memo": "Notes"
            },
            date_format="%Y-%m-%d"
        )
        
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv(transactions, template)
        
        assert "Date;Amount;Description;Notes" in csv_content
        assert "2023-01-01;100.5;Grocery Store;Weekly groceries" in csv_content
    
    def test_generate_csv_with_different_date_format(self):
        """Test generating a CSV file with a different date format."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 15),
                amount=100.50,
                payee="Grocery Store"
            ),
            BankingTransaction(
                date=datetime(2023, 2, 28),
                amount=-50.25,
                payee="Gas Station"
            )
        ]
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            date_format="%m/%d/%Y"
        )
        
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv(transactions, template)
        
        assert "01/15/2023" in csv_content
        assert "02/28/2023" in csv_content
    
    def test_generate_csv_with_missing_field_mapping(self):
        """Test generating a CSV file with a missing field mapping."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Grocery Store",
                memo="Weekly groceries"
            )
        ]
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "payee": "Description",
                "memo": "Notes"
            },
            date_format="%Y-%m-%d"
        )
        
        generator = CSVGenerator()
        
        with pytest.raises(CSVGeneratorError):
            generator.generate_csv(transactions, template)
    
    def test_generate_csv_with_empty_transactions(self):
        """Test generating a CSV file with empty transactions."""
        transactions = []
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "memo": "Notes"
            },
            date_format="%Y-%m-%d"
        )
        
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv(transactions, template)
        
        assert "Date,Amount,Description,Notes" in csv_content
        assert len(csv_content.strip().split("\n")) == 1


class TestQIFGenerator:
    """Tests for the QIFGenerator class."""
    
    def test_generate_bank_qif(self):
        """Test generating QIF content from banking transactions."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Grocery Store",
                number="123",
                memo="Weekly groceries",
                category="Food:Groceries",
                cleared_status="*"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 2),
                amount=-50.25,
                payee="Gas Station",
                memo="Fill up car",
                category="Auto:Fuel"
            )
        ]
        
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif(transactions, AccountType.BANK, "Checking")
        
        assert "!Type:Bank" in qif_content
        assert "D01/01/2023" in qif_content
        assert "T100.50" in qif_content
        assert "PGrocery Store" in qif_content
        assert "N123" in qif_content
        assert "MWeekly groceries" in qif_content
        assert "LFood:Groceries" in qif_content
        assert "C" in qif_content
        assert "D01/02/2023" in qif_content
        assert "T-50.25" in qif_content
        assert "PGas Station" in qif_content
        assert "MFill up car" in qif_content
        assert "LAuto:Fuel" in qif_content
        
        assert qif_content.count("^") == 2
    
    def test_generate_investment_qif(self):
        """Test generating QIF content from investment transactions."""
        transactions = [
            InvestmentTransaction(
                date=datetime(2023, 1, 1),
                action="Buy",
                security="AAPL",
                quantity=10,
                price=150.75,
                amount=-1507.50,
                commission=7.50,
                payee="Broker",
                memo="Buy Apple stock",
                category="Investments:Stocks",
                cleared_status="*"
            ),
            InvestmentTransaction(
                date=datetime(2023, 1, 2),
                action="Sell",
                security="MSFT",
                quantity=5,
                price=250.25,
                amount=1251.25,
                commission=6.25,
                payee="Broker",
                memo="Sell Microsoft stock",
                category="Investments:Stocks"
            )
        ]
        
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif(transactions, AccountType.INVESTMENT, "Investment Account")
        
        assert "!Type:Invst" in qif_content
        assert "D01/01/2023" in qif_content
        assert "N" in qif_content
        assert "YAAPL" in qif_content
        assert "Q10" in qif_content
        assert "I150.75" in qif_content
        assert "T-1507.50" in qif_content
        assert "O7.50" in qif_content
        assert "PBroker" in qif_content
        assert "MBuy Apple stock" in qif_content
        assert "LInvestments:Stocks" in qif_content
        assert "C" in qif_content
        assert "D01/02/2023" in qif_content
        assert "N" in qif_content
        assert "YMSFT" in qif_content
        assert "Q5" in qif_content
        assert "I250.25" in qif_content
        assert "T1251.25" in qif_content
        assert "O6.25" in qif_content
        
        assert qif_content.count("^") == 2
    
    def test_generate_qif_with_split_transactions(self):
        """Test generating QIF content with split transactions."""
        split1 = SplitTransaction(
            category="Food:Groceries",
            amount=60.00,
            memo="Food items"
        )
        
        split2 = SplitTransaction(
            category="Household:Supplies",
            amount=40.50,
            memo="Cleaning supplies"
        )
        
        transaction = BankingTransaction(
            date=datetime(2023, 1, 1),
            amount=100.50,
            payee="Grocery Store",
            memo="Split purchase",
            splits=[split1, split2]
        )
        
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif([transaction], AccountType.BANK, "Checking")
        
        assert "!Type:Bank" in qif_content
        assert "D01/01/2023" in qif_content
        assert "T100.50" in qif_content
        assert "PGrocery Store" in qif_content
        assert "MSplit purchase" in qif_content
        assert "SFood:Groceries" in qif_content
        assert "$60.00" in qif_content
        assert "EFood items" in qif_content
        assert "SHousehold:Supplies" in qif_content
        assert "$40.50" in qif_content
        assert "ECleaning supplies" in qif_content
        
        assert qif_content.count("^") == 1
    
    def test_generate_qif_with_account_info(self):
        """Test generating QIF content with account information."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Grocery Store"
            )
        ]
        
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif(
            transactions, 
            AccountType.BANK, 
            "Checking",
            include_account_info=True
        )
        
        assert "!Account" in qif_content
        assert "NChecking" in qif_content
        assert "TBank" in qif_content
        assert "!Type:Bank" in qif_content
    
    def test_generate_qif_with_multiple_accounts(self):
        """Test generating QIF content with multiple accounts."""
        qif_file = QIFFile()
        
        qif_file.accounts = [
            AccountDefinition(name="Checking", type=AccountType.BANK),
            AccountDefinition(name="Savings", type=AccountType.BANK),
            AccountDefinition(name="Investments", type=AccountType.INVESTMENT)
        ]
        
        qif_file.bank_transactions = {
            "Checking": [
                BankingTransaction(
                    date=datetime(2023, 1, 1),
                    amount=100.50,
                    payee="Grocery Store"
                )
            ],
            "Savings": [
                BankingTransaction(
                    date=datetime(2023, 1, 2),
                    amount=500.00,
                    payee="Transfer"
                )
            ]
        }
        
        qif_file.investment_transactions = {
            "Investments": [
                InvestmentTransaction(
                    date=datetime(2023, 1, 3),
                    action="Buy",
                    security="AAPL",
                    quantity=10,
                    price=150.75,
                    amount=-1507.50
                )
            ]
        }
        
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif_file(qif_file)
        
        assert "!Account" in qif_content
        assert "NChecking" in qif_content
        assert "TBank" in qif_content
        assert "!Type:Bank" in qif_content
        assert "D01/01/2023" in qif_content
        assert "T100.50" in qif_content
        assert "PGrocery Store" in qif_content
        
        assert "NSavings" in qif_content
        assert "D01/02/2023" in qif_content
        assert "T500.00" in qif_content
        assert "PTransfer" in qif_content
        
        assert "NInvestments" in qif_content
        assert "TInvst" in qif_content
        assert "!Type:Invst" in qif_content
        assert "D01/03/2023" in qif_content
        assert "N" in qif_content
        assert "YAAPL" in qif_content
        assert "Q10" in qif_content
        assert "I150.75" in qif_content
        assert "T-1507.50" in qif_content
    
    def test_generate_qif_with_empty_transactions(self):
        """Test generating QIF content with empty transactions."""
        transactions = []
        
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif(transactions, AccountType.BANK, "Checking")
        
        assert "!Type:Bank" in qif_content
        assert len(qif_content.strip().split("\n")) == 1
    
    def test_generate_qif_with_invalid_account_type(self):
        """Test generating QIF content with an invalid account type."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Grocery Store"
            )
        ]
        
        generator = QIFGenerator()
        
        with pytest.raises(QIFGeneratorError):
            generator.generate_qif(transactions, "InvalidType", "Checking")
