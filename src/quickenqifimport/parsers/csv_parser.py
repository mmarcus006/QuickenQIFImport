import csv
from datetime import datetime
from typing import List, Dict, Optional, Union, TextIO, Any
import os
from dateutil.parser import parse as parse_date

from ..models.csv_models import CSVBankTransaction, CSVInvestmentTransaction, CSVTemplate
from ..models.qif_models import QIFClearedStatus, InvestmentAction


class CSVParser:
    def __init__(self, date_format: str = "%Y-%m-%d", delimiter: str = ","):
        self.date_format = date_format
        self.delimiter = delimiter

    def parse_file(self, file_path: Union[str, TextIO], template: Optional[CSVTemplate] = None) -> List[Dict[str, Any]]:
        """Parse a CSV file and return a list of dictionaries."""
        if isinstance(file_path, str):
            with open(file_path, 'r', encoding='utf-8') as file:
                return self.parse(file, template)
        else:
            return self.parse(file_path, template)

    def parse(self, file_content: Union[str, TextIO], template: Optional[CSVTemplate] = None) -> List[Dict[str, Any]]:
        """Parse CSV content and return a list of dictionaries."""
        if isinstance(file_content, str):
            import io
            file_content = io.StringIO(file_content)

        delimiter = template.delimiter if template else self.delimiter
        
        reader = csv.DictReader(file_content, delimiter=delimiter)
        rows = list(reader)
        
        if template:
            mapped_rows = []
            for row in rows:
                mapped_row = {}
                for csv_field, qif_field in template.field_mapping.items():
                    if csv_field in row:
                        mapped_row[qif_field] = row[csv_field]
                mapped_rows.append(mapped_row)
            return mapped_rows
        
        return rows

    def parse_bank_transactions(self, file_path: Union[str, TextIO], template: Optional[CSVTemplate] = None) -> List[CSVBankTransaction]:
        """Parse a CSV file and return a list of bank transactions."""
        rows = self.parse_file(file_path, template)
        transactions = []
        
        date_format = template.date_format if template else self.date_format
        
        for row in rows:
            try:
                date_str = row.get('date', row.get('Date', ''))
                if not date_str:
                    raise ValueError(f"Missing date field in row: {row}")
                    
                try:
                    date = datetime.strptime(date_str, date_format)
                except ValueError:
                    try:
                        date = parse_date(date_str)
                    except:
                        raise ValueError(f"Could not parse date: {date_str}")
                
                amount_str = row.get('amount', row.get('Amount', '0'))
                amount = float(amount_str.replace(',', ''))
                
                transaction = CSVBankTransaction(
                    date=date,
                    amount=amount,
                    description=row.get('description', row.get('Description', '')),
                    reference=row.get('reference', row.get('Reference')),
                    memo=row.get('memo', row.get('Memo')),
                    category=row.get('category', row.get('Category')),
                    account_name=row.get('account_name', row.get('Account')),
                    status=row.get('status', row.get('Status'))
                )
                
                transactions.append(transaction)
            except (ValueError, KeyError) as e:
                print(f"Error parsing row: {row}. Error: {e}")
                continue
                
        return transactions

    def parse_investment_transactions(self, file_path: Union[str, TextIO], template: Optional[CSVTemplate] = None) -> List[CSVInvestmentTransaction]:
        """Parse a CSV file and return a list of investment transactions."""
        rows = self.parse_file(file_path, template)
        transactions = []
        
        date_format = template.date_format if template else self.date_format
        
        for row in rows:
            try:
                date_str = row.get('date', row.get('Date', ''))
                if not date_str:
                    raise ValueError(f"Missing date field in row: {row}")
                    
                try:
                    date = datetime.strptime(date_str, date_format)
                except ValueError:
                    try:
                        date = parse_date(date_str)
                    except:
                        raise ValueError(f"Could not parse date: {date_str}")
                
                amount_str = row.get('amount', row.get('Amount', '0'))
                price_str = row.get('price', row.get('Price', '0'))
                quantity_str = row.get('quantity', row.get('Quantity', '0'))
                commission_str = row.get('commission', row.get('Commission', '0'))
                
                amount = float(amount_str.replace(',', '')) if amount_str else None
                price = float(price_str.replace(',', '')) if price_str else None
                quantity = float(quantity_str.replace(',', '')) if quantity_str else None
                commission = float(commission_str.replace(',', '')) if commission_str else None
                
                transaction = CSVInvestmentTransaction(
                    date=date,
                    action=row.get('action', row.get('Action', '')),
                    security=row.get('security', row.get('Security')),
                    quantity=quantity,
                    price=price,
                    amount=amount,
                    commission=commission,
                    description=row.get('description', row.get('Description')),
                    category=row.get('category', row.get('Category')),
                    account=row.get('account', row.get('Account')),
                    memo=row.get('memo', row.get('Memo')),
                    status=row.get('status', row.get('Status'))
                )
                
                transactions.append(transaction)
            except (ValueError, KeyError) as e:
                print(f"Error parsing row: {row}. Error: {e}")
                continue
                
        return transactions

    def detect_template(self, file_path: str) -> Optional[str]:
        """Attempt to detect which template to use based on CSV headers."""
        with open(file_path, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()
            
            if 'action' in first_line.lower() and 'security' in first_line.lower():
                return 'investment'
            elif 'amount' in first_line.lower() and 'description' in first_line.lower():
                return 'bank'
                
        return None
