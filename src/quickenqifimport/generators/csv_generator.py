from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import csv
from io import StringIO

from ..models.models import (
    BankingTransaction, InvestmentTransaction, BaseTransaction,
    SplitTransaction, CSVTemplate, AccountType
)
from ..utils.date_utils import format_date

class CSVGeneratorError(Exception):
    """Exception raised for errors during CSV generation."""
    pass

class CSVGenerator:
    """Generator for CSV files from transaction data."""
    
    def __init__(self):
        """Initialize the CSV generator."""
        pass
    
    def generate_csv(self, transactions: List[BaseTransaction], 
                    template: Optional[CSVTemplate] = None,
                    headers: Optional[List[str]] = None) -> str:
        """Generate CSV content from transaction data.
        
        Args:
            transactions: List of transaction models
            template: Optional CSVTemplate to use for field mapping
            headers: Optional list of column headers (used if template is None)
            
        Returns:
            str: Generated CSV content
            
        Raises:
            CSVGeneratorError: If the CSV content cannot be generated
        """
        try:
            if not transactions:
                output = StringIO()
                delimiter = template.delimiter if template else ','
                writer = csv.writer(output, delimiter=delimiter)
                
                if headers:
                    writer.writerow(headers)
                elif template:
                    writer.writerow(list(template.field_mapping.values()))
                else:
                    return ""
                    
                return output.getvalue()
            
            is_investment = isinstance(transactions[0], InvestmentTransaction)
            
            if template:
                field_mapping = template.field_mapping
                csv_headers = list(field_mapping.values())
                delimiter = template.delimiter
                date_format = template.date_format or '%Y-%m-%d'
                
                if is_investment:
                    required_fields = ['date', 'action', 'security']
                else:
                    required_fields = ['date', 'amount']
                
                for field in required_fields:
                    if field not in field_mapping:
                        raise CSVGeneratorError(f"Missing required field mapping: {field}")
            else:
                if is_investment:
                    field_mapping = self._get_default_investment_field_mapping()
                else:
                    field_mapping = self._get_default_banking_field_mapping()
                
                if headers:
                    csv_headers = headers
                else:
                    csv_headers = list(field_mapping.values())
                
                delimiter = ','
                date_format = '%Y-%m-%d'
            
            output = StringIO()
            writer = csv.writer(output, delimiter=delimiter)
            
            writer.writerow(csv_headers)
            
            for transaction in transactions:
                row = self._transaction_to_row(transaction, field_mapping, date_format)
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            raise CSVGeneratorError(f"Failed to generate CSV content: {str(e)}")
    
    def _transaction_to_row(self, transaction: BaseTransaction, 
                           field_mapping: Dict[str, str],
                           date_format: str) -> List[str]:
        """Convert a transaction to a CSV row.
        
        Args:
            transaction: Transaction model
            field_mapping: Mapping of model fields to CSV columns
            date_format: Format string for dates
            
        Returns:
            List[str]: CSV row values
        """
        column_values = {column: "" for column in field_mapping.values()}
        
        for field, column in field_mapping.items():
            if hasattr(transaction, field):
                value = getattr(transaction, field)
                
                if value is not None:
                    if field == 'date':
                        column_values[column] = self._format_date(value, date_format)
                    elif field in ('amount', 'price', 'commission'):
                        column_values[column] = self._format_amount(value)
                    elif field == 'quantity':
                        column_values[column] = str(int(value)) if value == int(value) else self._format_amount(value)
                    elif field == 'action' and hasattr(transaction, 'action'):
                        if isinstance(value, str):
                            column_values[column] = value
                        else:
                            column_values[column] = str(value).split('.')[-1]
                    elif field == 'address' and isinstance(value, list):
                        column_values[column] = '\n'.join(value)
                    else:
                        column_values[column] = str(value)
        
        return [column_values.get(column, "") for column in field_mapping.values()]
    
    def _format_date(self, date_obj: datetime, date_format: str = '%Y-%m-%d') -> str:
        """Format a datetime object as a string.
        
        Args:
            date_obj: Datetime object to format
            date_format: Format string for output
            
        Returns:
            str: Formatted date string
        """
        return format_date(date_obj, date_format)
    
    def _format_amount(self, amount: float) -> str:
        """Format an amount as a string.
        
        Args:
            amount: Amount to format
            
        Returns:
            str: Formatted amount string
        """
        return str(amount) if amount == int(amount) else f"{amount:.1f}" if amount * 10 == int(amount * 10) else f"{amount:.2f}"
    
    def _get_default_banking_field_mapping(self) -> Dict[str, str]:
        """Get the default field mapping for banking transactions.
        
        Returns:
            Dict[str, str]: Mapping of model fields to CSV columns
        """
        return {
            'date': 'Date',
            'amount': 'Amount',
            'payee': 'Description',
            'number': 'Reference',
            'memo': 'Memo',
            'category': 'Category',
            'account': 'Account Name',
            'cleared_status': 'Status'
        }
    
    def _get_default_investment_field_mapping(self) -> Dict[str, str]:
        """Get the default field mapping for investment transactions.
        
        Returns:
            Dict[str, str]: Mapping of model fields to CSV columns
        """
        return {
            'date': 'Date',
            'action': 'Action',
            'security': 'Security',
            'quantity': 'Quantity',
            'price': 'Price',
            'amount': 'Amount',
            'commission': 'Commission',
            'payee': 'Description',
            'category': 'Category',
            'account': 'Account',
            'memo': 'Memo',
            'cleared_status': 'Status'
        }
