from typing import Dict, List, Any, Optional, Union, Tuple
import re

from ..models.models import CSVTemplate, AccountType

class TemplateValidationError(Exception):
    """Exception raised for template validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        self.message = message
        super().__init__(self._format_message())
        
    def _format_message(self) -> str:
        """Format the error message with field information."""
        if self.field is not None:
            return f"Field '{self.field}': {self.message}"
        else:
            return self.message

class TemplateValidator:
    """Validator for CSV templates."""
    
    def __init__(self):
        """Initialize the template validator."""
        self.required_fields = {
            AccountType.BANK: ['date', 'amount'],
            AccountType.CASH: ['date', 'amount'],
            AccountType.CREDIT_CARD: ['date', 'amount'],
            AccountType.ASSET: ['date', 'amount'],
            AccountType.LIABILITY: ['date', 'amount'],
            AccountType.INVESTMENT: ['date', 'action', 'security'],
        }
        
        self.valid_fields = {
            AccountType.BANK: [
                'date', 'amount', 'payee', 'number', 'memo', 'category',
                'account', 'cleared_status', 'address'
            ],
            AccountType.CASH: [
                'date', 'amount', 'payee', 'number', 'memo', 'category',
                'account', 'cleared_status', 'address'
            ],
            AccountType.CREDIT_CARD: [
                'date', 'amount', 'payee', 'number', 'memo', 'category',
                'account', 'cleared_status', 'address'
            ],
            AccountType.ASSET: [
                'date', 'amount', 'payee', 'number', 'memo', 'category',
                'account', 'cleared_status', 'address'
            ],
            AccountType.LIABILITY: [
                'date', 'amount', 'payee', 'number', 'memo', 'category',
                'account', 'cleared_status', 'address'
            ],
            AccountType.INVESTMENT: [
                'date', 'action', 'security', 'quantity', 'price', 'amount',
                'commission', 'payee', 'category', 'account', 'memo',
                'cleared_status', 'transfer_amount'
            ],
        }
    
    def validate_template(self, template: CSVTemplate) -> Tuple[bool, List[TemplateValidationError]]:
        """Validate a CSV template.
        
        Args:
            template: CSVTemplate to validate
            
        Returns:
            Tuple[bool, List[TemplateValidationError]]: Validation result and list of errors
        """
        errors = []
        
        if not template.name:
            errors.append(TemplateValidationError("Template name cannot be empty", field="name"))
        
        self._validate_required_fields(template, errors)
        
        self._validate_field_mapping(template, errors)
        
        if not template.delimiter:
            errors.append(TemplateValidationError("Delimiter cannot be empty", field="delimiter"))
        
        if template.date_format and not self._is_valid_date_format(template.date_format):
            errors.append(TemplateValidationError(
                f"Invalid date format: {template.date_format}", field="date_format"
            ))
        
        if template.account_type != AccountType.INVESTMENT:
            if not template.amount_columns and "amount" in template.field_mapping:
                amount_field = template.field_mapping["amount"]
                if amount_field:
                    template.amount_columns = [amount_field]
            elif not template.amount_columns:
                errors.append(TemplateValidationError(
                    "At least one amount column must be specified", field="amount_columns"
                ))
        
        if template.amount_multiplier:
            for column, multiplier in template.amount_multiplier.items():
                if column not in template.amount_columns:
                    errors.append(TemplateValidationError(
                        f"Amount multiplier specified for non-amount column: {column}",
                        field="amount_multiplier"
                    ))
                
                if not isinstance(multiplier, (int, float)):
                    errors.append(TemplateValidationError(
                        f"Amount multiplier must be a number: {multiplier}",
                        field="amount_multiplier"
                    ))
        
        if template.detect_transfers and template.transfer_pattern:
            try:
                re.compile(template.transfer_pattern)
            except re.error:
                errors.append(TemplateValidationError(
                    f"Invalid regular expression for transfer pattern: {template.transfer_pattern}",
                    field="transfer_pattern"
                ))
        
        return len(errors) == 0, errors
    
    def _validate_required_fields(self, template: CSVTemplate, 
                                errors: List[TemplateValidationError]) -> None:
        """Validate that all required fields are present in the template.
        
        Args:
            template: CSVTemplate to validate
            errors: List to append errors to
        """
        required_fields = self.required_fields.get(template.account_type, [])
        
        for field in required_fields:
            if field not in template.field_mapping or not template.field_mapping[field]:
                errors.append(TemplateValidationError(
                    f"Required field '{field}' is not mapped",
                    field="field_mapping"
                ))
    
    def _validate_field_mapping(self, template: CSVTemplate, 
                              errors: List[TemplateValidationError]) -> None:
        """Validate the field mapping in the template.
        
        Args:
            template: CSVTemplate to validate
            errors: List to append errors to
        """
        valid_fields = self.valid_fields.get(template.account_type, [])
        
        for field in template.field_mapping.keys():
            if field not in valid_fields:
                errors.append(TemplateValidationError(
                    f"Invalid field '{field}' for account type {template.account_type}",
                    field="field_mapping"
                ))
    
    def _is_valid_date_format(self, date_format: str) -> bool:
        """Check if a date format string is valid.
        
        Args:
            date_format: Date format string to check
            
        Returns:
            bool: True if the format is valid, False otherwise
        """
        valid_specifiers = ['%d', '%m', '%y', '%Y', '%b', '%B', '%a', '%A']
        
        return any(specifier in date_format for specifier in valid_specifiers)
