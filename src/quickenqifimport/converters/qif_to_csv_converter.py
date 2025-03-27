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
from ..models.csv_models import CSVTemplate


class QIFToCSVConverter:
    def __init__(self, date_format: str = "%Y-%m-%d", delimiter: str = ","):
        self.date_format = date_format
        self.delimiter = delimiter

    def convert_file(self, qif_file_path: str, csv_file_path: str, template: Optional[CSVTemplate] = None) -> None:
        """Convert a QIF file to a CSV file."""
        from ..parsers.qif_parser import QIFParser
        
        parser = QIFParser()
        qif_file = parser.parse_file(qif_file_path)
        
        csv_content = self.convert(qif_file, template)
        
        with open(csv_file_path, 'w', encoding='utf-8', newline='') as file:
            file.write(csv_content)

    def convert(self, qif_file: QIFFile, template: Optional[CSVTemplate] = None) -> str:
        """Convert a QIFFile object to CSV content."""
        if qif_file.type == QIFAccountType.BANK and qif_file.bank_transactions:
            return self._convert_bank_transactions(qif_file.bank_transactions, template)
        elif qif_file.type == QIFAccountType.CASH and qif_file.cash_transactions:
            return self._convert_cash_transactions(qif_file.cash_transactions, template)
        elif qif_file.type == QIFAccountType.CCARD and qif_file.credit_card_transactions:
            return self._convert_credit_card_transactions(qif_file.credit_card_transactions, template)
        elif qif_file.type == QIFAccountType.INVESTMENT and qif_file.investment_transactions:
            return self._convert_investment_transactions(qif_file.investment_transactions, template)
        elif qif_file.type == QIFAccountType.ASSET and qif_file.asset_transactions:
            return self._convert_asset_transactions(qif_file.asset_transactions, template)
        elif qif_file.type == QIFAccountType.LIABILITY and qif_file.liability_transactions:
            return self._convert_liability_transactions(qif_file.liability_transactions, template)
        elif qif_file.type == QIFAccountType.ACCOUNT and qif_file.accounts:
            return self._convert_accounts(qif_file.accounts, template)
        elif qif_file.type == QIFAccountType.CATEGORY and qif_file.categories:
            return self._convert_categories(qif_file.categories, template)
        elif qif_file.type == QIFAccountType.CLASS and qif_file.classes:
            return self._convert_classes(qif_file.classes, template)
        elif qif_file.type == QIFAccountType.MEMORIZED and qif_file.memorized_transactions:
            return self._convert_memorized_transactions(qif_file.memorized_transactions, template)
        else:
            raise ValueError(f"No data found for QIF file type: {qif_file.type}")

    def _convert_bank_transactions(self, transactions: List[BankTransaction], template: Optional[CSVTemplate] = None) -> str:
        """Convert bank transactions to CSV."""
        field_mapping = {
            'date': 'Date',
            'amount': 'Amount',
            'payee': 'Description',
            'number': 'Reference',
            'memo': 'Memo',
            'category': 'Category',
            'cleared_status': 'Status'
        }
        
        if template and template.field_mapping:
            field_mapping = {v: k for k, v in template.field_mapping.items()}
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(field_mapping.values()), delimiter=self.delimiter)
        writer.writeheader()
        
        for transaction in transactions:
            row = {}
            transaction_dict = transaction.model_dump()
            
            for qif_field, csv_field in field_mapping.items():
                if qif_field in transaction_dict and transaction_dict[qif_field] is not None:
                    if qif_field == 'date' and isinstance(transaction_dict[qif_field], datetime):
                        row[csv_field] = transaction_dict[qif_field].strftime(self.date_format)
                    elif qif_field == 'cleared_status' and isinstance(transaction_dict[qif_field], QIFClearedStatus):
                        row[csv_field] = self._format_cleared_status(transaction_dict[qif_field])
                    else:
                        row[csv_field] = transaction_dict[qif_field]
            
            if transaction.splits:
                if 'Memo' in row:
                    row['Memo'] = f"{row.get('Memo', '')} (Split transaction with {len(transaction.splits)} parts)"
                else:
                    row['Memo'] = f"Split transaction with {len(transaction.splits)} parts"
            
            writer.writerow(row)
            
        return output.getvalue()

    def _convert_cash_transactions(self, transactions: List[CashTransaction], template: Optional[CSVTemplate] = None) -> str:
        """Convert cash transactions to CSV."""
        return self._convert_bank_transactions(transactions, template)

    def _convert_credit_card_transactions(self, transactions: List[CreditCardTransaction], template: Optional[CSVTemplate] = None) -> str:
        """Convert credit card transactions to CSV."""
        return self._convert_bank_transactions(transactions, template)

    def _convert_asset_transactions(self, transactions: List[AssetTransaction], template: Optional[CSVTemplate] = None) -> str:
        """Convert asset transactions to CSV."""
        return self._convert_bank_transactions(transactions, template)

    def _convert_liability_transactions(self, transactions: List[LiabilityTransaction], template: Optional[CSVTemplate] = None) -> str:
        """Convert liability transactions to CSV."""
        return self._convert_bank_transactions(transactions, template)

    def _convert_investment_transactions(self, transactions: List[InvestmentTransaction], template: Optional[CSVTemplate] = None) -> str:
        """Convert investment transactions to CSV."""
        field_mapping = {
            'date': 'Date',
            'action': 'Action',
            'security': 'Security',
            'quantity': 'Quantity',
            'price': 'Price',
            'amount': 'Amount',
            'commission': 'Commission',
            'text': 'Description',
            'memo': 'Memo',
            'account': 'Account',
            'cleared_status': 'Status'
        }
        
        if template and template.field_mapping:
            field_mapping = {v: k for k, v in template.field_mapping.items()}
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(field_mapping.values()), delimiter=self.delimiter)
        writer.writeheader()
        
        for transaction in transactions:
            row = {}
            transaction_dict = transaction.model_dump()
            
            for qif_field, csv_field in field_mapping.items():
                if qif_field in transaction_dict and transaction_dict[qif_field] is not None:
                    if qif_field == 'date' and isinstance(transaction_dict[qif_field], datetime):
                        row[csv_field] = transaction_dict[qif_field].strftime(self.date_format)
                    elif qif_field == 'action' and isinstance(transaction_dict[qif_field], InvestmentAction):
                        row[csv_field] = transaction_dict[qif_field].value
                    elif qif_field == 'cleared_status' and isinstance(transaction_dict[qif_field], QIFClearedStatus):
                        row[csv_field] = self._format_cleared_status(transaction_dict[qif_field])
                    else:
                        row[csv_field] = transaction_dict[qif_field]
            
            writer.writerow(row)
            
        return output.getvalue()

    def _convert_accounts(self, accounts: List[Account], template: Optional[CSVTemplate] = None) -> str:
        """Convert accounts to CSV."""
        field_mapping = {
            'name': 'Name',
            'type': 'Type',
            'description': 'Description',
            'credit_limit': 'Credit Limit',
            'statement_date': 'Statement Date',
            'statement_balance': 'Statement Balance'
        }
        
        if template and template.field_mapping:
            field_mapping = {v: k for k, v in template.field_mapping.items()}
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(field_mapping.values()), delimiter=self.delimiter)
        writer.writeheader()
        
        for account in accounts:
            row = {}
            account_dict = account.model_dump()
            
            for qif_field, csv_field in field_mapping.items():
                if qif_field in account_dict and account_dict[qif_field] is not None:
                    if qif_field == 'statement_date' and isinstance(account_dict[qif_field], datetime):
                        row[csv_field] = account_dict[qif_field].strftime(self.date_format)
                    elif qif_field == 'type' and isinstance(account_dict[qif_field], QIFAccountType):
                        row[csv_field] = account_dict[qif_field].value
                    else:
                        row[csv_field] = account_dict[qif_field]
            
            writer.writerow(row)
            
        return output.getvalue()

    def _convert_categories(self, categories: List[Category], template: Optional[CSVTemplate] = None) -> str:
        """Convert categories to CSV."""
        field_mapping = {
            'name': 'Name',
            'description': 'Description',
            'tax_related': 'Tax Related',
            'income': 'Income',
            'expense': 'Expense',
            'budget_amount': 'Budget Amount',
            'tax_schedule': 'Tax Schedule'
        }
        
        if template and template.field_mapping:
            field_mapping = {v: k for k, v in template.field_mapping.items()}
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(field_mapping.values()), delimiter=self.delimiter)
        writer.writeheader()
        
        for category in categories:
            row = {}
            category_dict = category.model_dump()
            
            for qif_field, csv_field in field_mapping.items():
                if qif_field in category_dict and category_dict[qif_field] is not None:
                    if qif_field in ['tax_related', 'income', 'expense'] and isinstance(category_dict[qif_field], bool):
                        row[csv_field] = 'Yes' if category_dict[qif_field] else 'No'
                    else:
                        row[csv_field] = category_dict[qif_field]
            
            writer.writerow(row)
            
        return output.getvalue()

    def _convert_classes(self, classes: List[Class], template: Optional[CSVTemplate] = None) -> str:
        """Convert classes to CSV."""
        field_mapping = {
            'name': 'Name',
            'description': 'Description'
        }
        
        if template and template.field_mapping:
            field_mapping = {v: k for k, v in template.field_mapping.items()}
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(field_mapping.values()), delimiter=self.delimiter)
        writer.writeheader()
        
        for cls in classes:
            row = {}
            class_dict = cls.model_dump()
            
            for qif_field, csv_field in field_mapping.items():
                if qif_field in class_dict and class_dict[qif_field] is not None:
                    row[csv_field] = class_dict[qif_field]
            
            writer.writerow(row)
            
        return output.getvalue()

    def _convert_memorized_transactions(self, transactions: List[MemorizedTransaction], template: Optional[CSVTemplate] = None) -> str:
        """Convert memorized transactions to CSV."""
        field_mapping = {
            'transaction_type': 'Transaction Type',
            'transaction': 'Transaction Details'
        }
        
        if template and template.field_mapping:
            field_mapping = {v: k for k, v in template.field_mapping.items()}
            
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(field_mapping.values()), delimiter=self.delimiter)
        writer.writeheader()
        
        for transaction in transactions:
            row = {}
            transaction_dict = transaction.model_dump()
            
            for qif_field, csv_field in field_mapping.items():
                if qif_field in transaction_dict and transaction_dict[qif_field] is not None:
                    if qif_field == 'transaction':
                        row[csv_field] = str(transaction_dict[qif_field])
                    else:
                        row[csv_field] = transaction_dict[qif_field]
            
            writer.writerow(row)
            
        return output.getvalue()

    def _format_cleared_status(self, status: QIFClearedStatus) -> str:
        """Format cleared status for CSV output."""
        status_map = {
            QIFClearedStatus.UNCLEARED: "",
            QIFClearedStatus.CLEARED: "Cleared",
            QIFClearedStatus.CLEARED_ALT: "Cleared",
            QIFClearedStatus.RECONCILED: "Reconciled",
            QIFClearedStatus.RECONCILED_ALT: "Reconciled"
        }
        
        return status_map.get(status, "")
