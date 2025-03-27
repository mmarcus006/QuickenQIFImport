from typing import List, Dict, Any, Optional, TextIO, Union
import csv
import io
from datetime import datetime

from ..models.qif_models import (
    QIFFile, QIFAccountType, QIFClearedStatus, InvestmentAction,
    BankTransaction, CashTransaction, CreditCardTransaction,
    AssetTransaction, LiabilityTransaction, InvestmentTransaction,
    Account, Category, Class, MemorizedTransaction, SplitTransaction
)
from ..models.csv_models import CSVTemplate, CSVBankTransaction, CSVInvestmentTransaction


class CSVToQIFConverter:
    def __init__(self, date_format: str = "%Y-%m-%d"):
        self.date_format = date_format

    def convert_file(self, csv_file_path: str, qif_file_path: str, account_type: QIFAccountType, template: Optional[CSVTemplate] = None) -> None:
        """Convert a CSV file to a QIF file."""
        from ..parsers.csv_parser import CSVParser
        
        parser = CSVParser(date_format=self.date_format)
        
        if account_type in [QIFAccountType.BANK, QIFAccountType.CASH, QIFAccountType.CCARD, QIFAccountType.ASSET, QIFAccountType.LIABILITY]:
            transactions = parser.parse_bank_transactions(csv_file_path, template)
            qif_content = self.convert_bank_transactions(transactions, account_type)
        elif account_type == QIFAccountType.INVESTMENT:
            transactions = parser.parse_investment_transactions(csv_file_path, template)
            qif_content = self.convert_investment_transactions(transactions)
        else:
            rows = parser.parse_file(csv_file_path, template)
            qif_content = self.convert_generic(rows, account_type)
        
        with open(qif_file_path, 'w', encoding='utf-8') as file:
            file.write(qif_content)

    def convert_bank_transactions(self, transactions: List[CSVBankTransaction], account_type: QIFAccountType = QIFAccountType.BANK) -> str:
        """Convert bank transactions to QIF format."""
        output = []
        
        output.append(f"!Type:{account_type.value}")
        
        for transaction in transactions:
            if transaction.date:
                date_str = transaction.date.strftime("%m/%d/%Y")
                output.append(f"D{date_str}")
                
            output.append(f"T{transaction.amount:.2f}")
            
            if transaction.reference:
                output.append(f"N{transaction.reference}")
                
            if transaction.description:
                output.append(f"P{transaction.description}")
                
            if transaction.memo:
                output.append(f"M{transaction.memo}")
                
            if transaction.category:
                output.append(f"L{transaction.category}")
                
            if transaction.status:
                output.append(f"C{self._parse_cleared_status(transaction.status)}")
                
            if transaction.account_name and transaction.account_name.startswith('[') and transaction.account_name.endswith(']'):
                output.append(f"L{transaction.account_name}")
                
            output.append("^")
            
        return "\n".join(output)

    def convert_investment_transactions(self, transactions: List[CSVInvestmentTransaction]) -> str:
        """Convert investment transactions to QIF format."""
        output = []
        
        output.append(f"!Type:{QIFAccountType.INVESTMENT.value}")
        
        for transaction in transactions:
            if transaction.date:
                date_str = transaction.date.strftime("%m/%d/%Y")
                output.append(f"D{date_str}")
                
            output.append(f"N{transaction.action}")
            
            if transaction.security:
                output.append(f"Y{transaction.security}")
                
            if transaction.price is not None:
                output.append(f"I{transaction.price:.2f}")
                
            if transaction.quantity is not None:
                output.append(f"Q{transaction.quantity:.2f}")
                
            if transaction.amount is not None:
                output.append(f"T{transaction.amount:.2f}")
                
            if transaction.commission is not None:
                output.append(f"O{transaction.commission:.2f}")
                
            if transaction.description:
                output.append(f"P{transaction.description}")
                
            if transaction.memo:
                output.append(f"M{transaction.memo}")
                
            if transaction.category:
                output.append(f"L{transaction.category}")
                
            if transaction.account:
                if transaction.account.startswith('[') and transaction.account.endswith(']'):
                    output.append(f"L{transaction.account}")
                else:
                    output.append(f"L{transaction.account}")
                
            if transaction.status:
                output.append(f"C{self._parse_cleared_status(transaction.status)}")
                
            output.append("^")
            
        return "\n".join(output)

    def convert_generic(self, rows: List[Dict[str, Any]], account_type: QIFAccountType) -> str:
        """Convert generic CSV data to QIF format based on account type."""
        output = []
        
        output.append(f"!Type:{account_type.value}")
        
        if account_type == QIFAccountType.ACCOUNT:
            field_mapping = {
                'Name': 'N',
                'Type': 'T',
                'Description': 'D',
                'Credit Limit': 'L',
                'Statement Date': '/',
                'Statement Balance': '$'
            }
        elif account_type == QIFAccountType.CATEGORY:
            field_mapping = {
                'Name': 'N',
                'Description': 'D',
                'Tax Related': 'T',
                'Income': 'I',
                'Expense': 'E',
                'Budget Amount': 'B',
                'Tax Schedule': 'R'
            }
        elif account_type == QIFAccountType.CLASS:
            field_mapping = {
                'Name': 'N',
                'Description': 'D'
            }
        else:
            field_mapping = {
                'Reference': 'N',
                'Description': 'P',
                'Memo': 'M',
                'Category': 'L',
                'Date': 'D',
                'Amount': 'T'
            }
            
        for row in rows:
            if account_type in [QIFAccountType.BANK, QIFAccountType.CASH, QIFAccountType.CCARD]:
                has_reference = False
                for field in ['Reference', 'reference']:
                    if field in row and row[field]:
                        has_reference = True
                        break
                if not has_reference:
                    output.append("N")
            
            for csv_field, qif_field in field_mapping.items():
                value = None
                if csv_field in row:
                    value = row[csv_field]
                elif csv_field.lower() in row:
                    value = row[csv_field.lower()]
                
                if value:
                    if csv_field in ['Tax Related', 'Income', 'Expense']:
                        if str(value).lower() in ['yes', 'true', '1']:
                            output.append(f"{qif_field}")
                    elif csv_field == 'Date':
                        try:
                            date = datetime.strptime(value, self.date_format)
                            output.append(f"{qif_field}{date.strftime('%m/%d/%Y')}")
                        except ValueError:
                            try:
                                from dateutil.parser import parse as parse_date
                                date = parse_date(value)
                                output.append(f"{qif_field}{date.strftime('%m/%d/%Y')}")
                            except:
                                pass
                    else:
                        output.append(f"{qif_field}{value}")
            
            output.append("^")
            
        return "\n".join(output)

    def _parse_cleared_status(self, status: str) -> str:
        """Parse cleared status string to QIF format."""
        status_lower = status.lower() if status else ""
        
        if status_lower in ["cleared", "c", "*"]:
            return "*"
        elif status_lower in ["reconciled", "r", "x"]:
            return "X"
        else:
            return ""
