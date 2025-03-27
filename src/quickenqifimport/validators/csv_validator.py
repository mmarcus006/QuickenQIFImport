from typing import Dict, List, Any, Optional, Union, Tuple
import re
from datetime import datetime

from ..models.models import CSVTemplate, AccountType
from ..utils.date_utils import parse_date, DateFormatError

class CSVValidationError(Exception):
    """Exception raised for CSV validation errors."""
    def __init__(self, message: str, row: Optional[int] = None, column: Optional[str] = None):
        self.row = row
        self.column = column
        self.message = message
        super().__init__(self._format_message())
        
    def _format_message(self) -> str:
        """Format the error message with row and column information."""
        if self.row is not None and self.column is not None:
            return f"Row {self.row}, Column '{self.column}': {self.message}"
        elif self.row is not None:
            return f"Row {self.row}: {self.message}"
        elif self.column is not None:
            return f"Column '{self.column}': {self.message}"
        else:
            return self.message

class CSVValidator:
    """Validator for CSV files and data."""
    
    def __init__(self):
        """Initialize the CSV validator."""
        pass
    
    def validate_csv_format(self, csv_content: str, template_or_delimiter: Union[CSVTemplate, str] = ',', 
                           has_header: bool = True) -> Tuple[bool, List[CSVValidationError]]:
        """Validate the format of a CSV file.
        
        Args:
            csv_content: String containing CSV data
            template_or_delimiter: CSVTemplate or CSV delimiter character
            has_header: Whether the CSV has a header row (ignored if template is provided)
            
        Returns:
            Tuple[bool, List[CSVValidationError]]: Validation result and list of errors
        """
        if isinstance(template_or_delimiter, CSVTemplate):
            template = template_or_delimiter
            delimiter = template.delimiter
            has_header = template.has_header
        else:
            delimiter = template_or_delimiter
            template = None
        errors = []
        
        if not csv_content.strip():
            errors.append(CSVValidationError("CSV content is empty"))
            return False, errors
        
        lines = [line.strip() for line in csv_content.strip().split('\n')]
        
        if has_header and len(lines) < 2:
            errors.append(CSVValidationError("CSV file has a header but no data rows"))
            return False, errors
            
        if template and has_header:
            header_row = lines[0].split(delimiter)
            for field, column_name in template.field_mapping.items():
                if column_name and column_name not in header_row:
                    errors.append(CSVValidationError(
                        f"Mapped column '{column_name}' for field '{field}' not found in header",
                        column=column_name
                    ))
        
        column_counts = []
        for i, line in enumerate(lines):
            if not line.strip():
                continue
                
            columns = line.split(delimiter)
            column_counts.append(len(columns))
            
            for j, column in enumerate(columns):
                if not column.strip() and i > 0:  # Allow empty header columns
                    errors.append(CSVValidationError(
                        "Empty column value", row=i+1, column=f"Column {j+1}"
                    ))
        
        if len(set(column_counts)) > 1:
            errors.append(CSVValidationError(
                "Inconsistent number of columns across rows"
            ))
        
        if template:
            filtered_errors = [error for error in errors if "Empty column value" not in str(error)]
            if not filtered_errors:
                return True, []
            
        return len(errors) == 0, errors
    
    def validate_csv_data(self, csv_content: str, template: CSVTemplate) -> Tuple[bool, List[CSVValidationError]]:
        """Validate CSV data against a template.
        
        Args:
            csv_content: String containing CSV data
            template: CSVTemplate to validate against
            
        Returns:
            Tuple[bool, List[CSVValidationError]]: Validation result and list of errors
        """
        errors = []
        
        format_valid, format_errors = self.validate_csv_format(csv_content, template)
        errors.extend(format_errors)
        
        if not format_valid:
            return False, errors
        
        lines = [line.strip() for line in csv_content.strip().split('\n')]
        
        header_row = None
        if template.has_header and template.skip_rows < len(lines):
            header_row = lines[template.skip_rows].split(template.delimiter)
            header_row = [col.strip() for col in header_row]
        
        if not template.amount_columns and "amount" in template.field_mapping:
            amount_field = template.field_mapping["amount"]
            if amount_field:
                template.amount_columns = [amount_field]
        
        start_row = template.skip_rows
        if template.has_header:
            start_row += 1
            
        for i, line in enumerate(lines[start_row:], start=start_row+1):
            if not line.strip():
                continue
                
            columns = [col.strip() for col in line.split(template.delimiter)]
            
            self._validate_row_data(columns, header_row, template, i, errors)
        
        if not errors:
            return True, []
            
        date_errors = any("date" in str(error).lower() for error in errors)
        amount_errors = any("amount" in str(error).lower() for error in errors)
        
        if date_errors or amount_errors:
            return False, errors
            
        return len(errors) == 0, errors
    
    def _validate_row_data(self, columns: List[str], header_row: Optional[List[str]], 
                          template: CSVTemplate, row_num: int, 
                          errors: List[CSVValidationError]) -> None:
        """Validate a single row of CSV data.
        
        Args:
            columns: List of column values
            header_row: List of column headers (or None if no header)
            template: CSVTemplate to validate against
            row_num: Row number for error reporting
            errors: List to append errors to
        """
        date_column = self._get_column_index(template.field_mapping.get('date'), header_row)
        if date_column is not None and date_column < len(columns):
            date_value = columns[date_column].strip()
            if date_value:
                try:
                    parse_date(date_value, template.date_format)
                except DateFormatError as e:
                    errors.append(CSVValidationError(
                        f"Invalid date format: {str(e)}", row=row_num, 
                        column=header_row[date_column] if header_row else f"Column {date_column+1}"
                    ))
            else:
                errors.append(CSVValidationError(
                    "Date field is required", row=row_num,
                    column=header_row[date_column] if header_row else f"Column {date_column+1}"
                ))
        
        for amount_field in ['amount', 'price', 'quantity', 'commission']:
            amount_column = self._get_column_index(template.field_mapping.get(amount_field), header_row)
            if amount_column is not None and amount_column < len(columns):
                amount_value = columns[amount_column].strip()
                if amount_value:
                    try:
                        cleaned = re.sub(r'[^\d\-\+\.,]', '', amount_value)
                        
                        if ',' in cleaned and '.' in cleaned:
                            cleaned = cleaned.replace(',', '')
                        elif ',' in cleaned and '.' not in cleaned:
                            cleaned = cleaned.replace(',', '.')
                            
                        float(cleaned)
                    except ValueError:
                        errors.append(CSVValidationError(
                            f"Invalid {amount_field} format: {amount_value}", row=row_num,
                            column=header_row[amount_column] if header_row else f"Column {amount_column+1}"
                        ))
        
        if template.account_type == AccountType.INVESTMENT:
            action_column = self._get_column_index(template.field_mapping.get('action'), header_row)
            if action_column is not None and action_column < len(columns):
                action_value = columns[action_column].strip()
                if action_value:
                    valid_actions = [
                        'Buy', 'BuyX', 'Sell', 'SellX', 'Div', 'DivX', 'IntInc',
                        'ReinvDiv', 'ShrsIn', 'ShrsOut', 'StkSplit', 'XIn', 'XOut',
                        'CGLong', 'CGShort'
                    ]
                    valid_actions.extend([a.lower() for a in valid_actions])
                    
                    if action_value not in valid_actions:
                        errors.append(CSVValidationError(
                            f"Invalid investment action: {action_value}", row=row_num,
                            column=header_row[action_column] if header_row else f"Column {action_column+1}"
                        ))
    
    def _get_column_index(self, column_name: Optional[str], 
                         header_row: Optional[List[str]]) -> Optional[int]:
        """Get the index of a column by name.
        
        Args:
            column_name: Name of the column to find
            header_row: List of column headers (or None if no header)
            
        Returns:
            Optional[int]: Column index or None if not found
        """
        if not column_name:
            return None
            
        if header_row:
            try:
                return header_row.index(column_name)
            except ValueError:
                return None
        else:
            try:
                return int(column_name)
            except ValueError:
                return None
