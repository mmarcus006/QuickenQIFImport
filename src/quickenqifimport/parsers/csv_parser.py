import csv
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re

from ..models.models import (
    BankingTransaction, InvestmentTransaction, BaseTransaction,
    SplitTransaction, CSVTemplate, AccountType, ClearedStatus, InvestmentAction
)
from ..utils.date_utils import parse_date

class CSVParserError(Exception):
    """Exception raised for errors during CSV parsing."""
    pass

class CSVParser:
    """Parser for CSV files into transaction models."""
    
    def __init__(self):
        self._transaction_classes = {
            AccountType.BANK: BankingTransaction,
            AccountType.CASH: BankingTransaction,
            AccountType.CREDIT_CARD: BankingTransaction,
            AccountType.ASSET: BankingTransaction,
            AccountType.LIABILITY: BankingTransaction,
            AccountType.INVESTMENT: InvestmentTransaction,
        }
        
        self._field_handlers = {
            'date': self._handle_date,
            'amount': self._handle_amount,
            'payee': self._handle_string,
            'number': self._handle_string,
            'memo': self._handle_string,
            'category': self._handle_category,
            'cleared_status': self._handle_cleared_status,
            'address': self._handle_address,
            'action': self._handle_investment_action,
            'security': self._handle_string,
            'price': self._handle_amount,
            'quantity': self._handle_amount,
            'commission': self._handle_amount,
            'account': self._handle_account,
        }
    
    def parse_csv(self, csv_content: str, template: CSVTemplate) -> List[BaseTransaction]:
        """Parse CSV content into transaction models using the provided template.
        
        Args:
            csv_content: String containing CSV data
            template: CSVTemplate defining the mapping between CSV columns and transaction fields
            
        Returns:
            List of transaction models (BankingTransaction or InvestmentTransaction)
            
        Raises:
            CSVParserError: If the CSV content cannot be parsed
        """
        try:
            transaction_class = self._transaction_classes.get(template.account_type)
            if not transaction_class:
                raise CSVParserError(f"Unsupported account type: {template.account_type}")
            
            reader = csv.reader(csv_content.splitlines(), delimiter=template.delimiter)
            
            rows = list(reader)
            if not rows:
                return []
                
            start_row = template.skip_rows
            if template.has_header:
                start_row += 1
                
            header_row = None
            if template.has_header and template.skip_rows < len(rows):
                header_row = rows[template.skip_rows]
                
            transactions = []
            for row_idx, row in enumerate(rows[start_row:], start=start_row):
                if not any(cell.strip() for cell in row):
                    continue
                    
                try:
                    transaction = self._map_row_to_transaction(
                        row, header_row, template, transaction_class, row_idx + 1
                    )
                    transactions.append(transaction)
                except Exception as e:
                    raise CSVParserError(f"Error parsing row {row_idx + 1}: {str(e)}")
            
            return transactions
            
        except Exception as e:
            if isinstance(e, CSVParserError):
                raise
            raise CSVParserError(f"Failed to parse CSV content: {str(e)}")
    
    def _map_row_to_transaction(
        self, 
        row: List[str], 
        header_row: Optional[List[str]], 
        template: CSVTemplate, 
        transaction_class: Any,
        row_number: int
    ) -> BaseTransaction:
        """Map a CSV row to a transaction model.
        
        Args:
            row: List of values from the CSV row
            header_row: List of column headers (or None if no header)
            template: CSVTemplate defining the mapping
            transaction_class: Class to instantiate (BankingTransaction or InvestmentTransaction)
            row_number: Row number for error reporting
            
        Returns:
            BaseTransaction: A transaction model
            
        Raises:
            CSVParserError: If the row cannot be mapped to a transaction
        """
        transaction_data = {}
        
        for field_name, column_name in template.field_mapping.items():
            if not column_name:
                continue
                
            column_idx = None
            if header_row:
                try:
                    column_idx = header_row.index(column_name)
                except ValueError:
                    continue
            else:
                try:
                    column_idx = int(column_name)
                except ValueError:
                    continue
            
            if column_idx is None or column_idx >= len(row):
                continue
                
            value = row[column_idx].strip()
            
            if not value:
                continue
                
            handler = self._field_handlers.get(field_name)
            if handler:
                try:
                    processed_value = handler(
                        value, field_name, template, row, header_row, row_number
                    )
                    if processed_value is not None:
                        transaction_data[field_name] = processed_value
                except Exception as e:
                    raise CSVParserError(
                        f"Error processing field '{field_name}' with value '{value}': {str(e)}"
                    )
        
        if 'date' not in transaction_data:
            raise CSVParserError(f"Missing required field 'date' in row {row_number}")
            
        if template.account_type != AccountType.INVESTMENT and 'amount' not in transaction_data:
            if 'amount' in template.field_mapping:
                raise CSVParserError(f"Missing required field 'amount' in row {row_number}")
                
        if template.account_type == AccountType.INVESTMENT:
            if 'action' not in transaction_data:
                raise CSVParserError(f"Missing required field 'action' in row {row_number}")
            if 'security' not in transaction_data:
                raise CSVParserError(f"Missing required field 'security' in row {row_number}")
            
        try:
            return transaction_class(**transaction_data)
        except Exception as e:
            raise CSVParserError(f"Failed to create transaction from row {row_number}: {str(e)}")
    
    def _handle_date(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> datetime:
        """Handle date field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            datetime: Parsed date
            
        Raises:
            CSVParserError: If the date cannot be parsed
        """
        try:
            return parse_date(value, template.date_format)
        except Exception as e:
            raise CSVParserError(f"Invalid date format in row {row_number}: {str(e)}")
    
    def _handle_amount(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> float:
        """Handle amount field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            float: Parsed amount
            
        Raises:
            CSVParserError: If the amount cannot be parsed
        """
        try:
            cleaned = re.sub(r'[^\d\-\+\.,]', '', value)
            
            if ',' in cleaned and '.' in cleaned:
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned and '.' not in cleaned:
                cleaned = cleaned.replace(',', '.')
                
            amount = float(cleaned)
            
            if template.amount_multiplier and field_name in template.amount_multiplier:
                amount *= template.amount_multiplier[field_name]
                
            return amount
        except ValueError:
            raise CSVParserError(f"Invalid amount format in row {row_number}: {value}")
    
    def _handle_string(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> str:
        """Handle string field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            str: Processed string value
        """
        return value
    
    def _handle_category(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> str:
        """Handle category field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            str: Processed category value
        """
        if template.detect_transfers and template.transfer_pattern:
            match = re.search(template.transfer_pattern, value)
            if match:
                return f"[{match.group(1)}]"
                
        return value
    
    def _handle_cleared_status(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> str:
        """Handle cleared status field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            str: Processed cleared status value
        """
        status_map = {
            'cleared': 'c',
            'reconciled': 'R',
            'uncleared': '',
            'c': 'c',
            'r': 'R',
            'R': 'R',
            '*': 'c',
            'X': 'R',
        }
        
        return status_map.get(value.lower(), value)
    
    def _handle_address(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> List[str]:
        """Handle address field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            List[str]: List of address lines
        """
        return [line.strip() for line in value.split('\n')]
    
    def _handle_investment_action(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> str:
        """Handle investment action field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            str: Processed investment action value
        """
        action_map = {
            'buy': 'Buy',
            'sell': 'Sell',
            'dividend': 'Div',
            'div': 'Div',
            'reinvest': 'ReinvDiv',
            'reinvdiv': 'ReinvDiv',
            'deposit': 'XIn',
            'xin': 'XIn',
            'withdrawal': 'XOut',
            'xout': 'XOut',
            'transfer in': 'ShrsIn',
            'shrsin': 'ShrsIn',
            'transfer out': 'ShrsOut',
            'shrsout': 'ShrsOut',
            'split': 'StkSplit',
            'stksplit': 'StkSplit',
            'interest': 'IntInc',
            'intinc': 'IntInc',
            'cglong': 'CGLong',
            'cgshort': 'CGShort',
        }
        
        return action_map.get(value.lower(), value)
    
    def _handle_account(
        self, value: str, field_name: str, template: CSVTemplate, 
        row: List[str], header_row: Optional[List[str]], row_number: int
    ) -> str:
        """Handle account field.
        
        Args:
            value: Field value from CSV
            field_name: Name of the field
            template: CSVTemplate being used
            row: Complete row data
            header_row: Header row (or None)
            row_number: Row number for error reporting
            
        Returns:
            str: Processed account value
        """
        if value.startswith('[') and value.endswith(']'):
            return value
            
        return f"[{value}]"
