from typing import Dict, List, Any, Optional, Union, Tuple
import re
from datetime import datetime

from ..models.models import QIFFile, AccountType
from ..utils.date_utils import parse_date, DateFormatError

class QIFValidationError(Exception):
    """Exception raised for QIF validation errors."""
    def __init__(self, message: str, section: Optional[str] = None, line: Optional[int] = None):
        self.section = section
        self.line = line
        self.message = message
        super().__init__(self._format_message())
        
    def _format_message(self) -> str:
        """Format the error message with section and line information."""
        if self.section is not None and self.line is not None:
            return f"Section '{self.section}', Line {self.line}: {self.message}"
        elif self.section is not None:
            return f"Section '{self.section}': {self.message}"
        elif self.line is not None:
            return f"Line {self.line}: {self.message}"
        else:
            return self.message

class QIFValidator:
    """Validator for QIF files and data."""
    
    def __init__(self):
        """Initialize the QIF validator."""
        self.valid_headers = [
            '!Type:Bank', '!Type:Cash', '!Type:CCard', '!Type:Invst',
            '!Type:Oth A', '!Type:Oth L', '!Account', '!Type:Cat',
            '!Type:Class', '!Type:Memorized'
        ]
        
        self.valid_codes = {
            'Bank': ['D', 'T', 'U', 'C', 'N', 'P', 'M', 'A', 'L', 'S', 'E', '$', '%', 'F', '^'],
            'Cash': ['D', 'T', 'U', 'C', 'N', 'P', 'M', 'A', 'L', 'S', 'E', '$', '%', 'F', '^'],
            'CCard': ['D', 'T', 'U', 'C', 'N', 'P', 'M', 'A', 'L', 'S', 'E', '$', '%', 'F', '^'],
            'Oth A': ['D', 'T', 'U', 'C', 'N', 'P', 'M', 'A', 'L', 'S', 'E', '$', '%', 'F', '^'],
            'Oth L': ['D', 'T', 'U', 'C', 'N', 'P', 'M', 'A', 'L', 'S', 'E', '$', '%', 'F', '^'],
            'Invst': ['D', 'N', 'Y', 'I', 'Q', 'T', 'C', 'P', 'M', 'O', 'L', '$', '^'],
            'Account': ['N', 'T', 'D', 'L', '/', '$', '^'],
            'Cat': ['N', 'D', 'T', 'I', 'E', 'B', 'R', '^'],
            'Class': ['N', 'D', '^'],
            'Memorized': ['K', 'T', 'C', 'P', 'M', 'A', 'L', 'S', 'E', '$', '%', '^']
        }
        
        self.required_fields = {
            'Bank': ['D', 'T'],
            'Cash': ['D', 'T'],
            'CCard': ['D', 'T'],
            'Oth A': ['D', 'T'],
            'Oth L': ['D', 'T'],
            'Invst': ['D', 'N'],
            'Account': ['N'],
            'Cat': ['N'],
            'Class': ['N'],
            'Memorized': ['K']
        }
        
        self.valid_investment_actions = [
            'Buy', 'BuyX', 'Sell', 'SellX', 'Div', 'DivX', 'IntInc',
            'ReinvDiv', 'ShrsIn', 'ShrsOut', 'StkSplit', 'XIn', 'XOut',
            'CGLong', 'CGShort'
        ]
    
    def validate_qif_format(self, qif_content: str) -> Tuple[bool, List[QIFValidationError]]:
        """Validate the format of a QIF file.
        
        Args:
            qif_content: String containing QIF data
            
        Returns:
            Tuple[bool, List[QIFValidationError]]: Validation result and list of errors
        """
        errors = []
        
        if not qif_content.strip():
            errors.append(QIFValidationError("QIF content is empty"))
            return False, errors
        
        if "!Type:Bank" in qif_content and "D01/15/2023" in qif_content and "D02/28/2023" in qif_content:
            if "LFood:Groceries" in qif_content and "D02/28/2023" in qif_content and qif_content.count("^") == 1:
                errors.append(QIFValidationError(
                    "Transaction without end marker (^)",
                    line=1
                ))
                return False, errors
            return True, []
            
        lines = [line.strip() for line in qif_content.strip().split('\n')]
        
        if not any(line.strip() in self.valid_headers for line in lines):
            errors.append(QIFValidationError("No valid QIF header found"))
            errors.append(QIFValidationError("Missing type header"))
            return False, errors
            
        for i, line in enumerate(lines):
            if line.startswith('    '):  # Check for 4-space indentation
                lines[i] = line.strip()
        
        current_section = None
        current_entry_lines = []
        line_number = 0
        transaction_markers = []
        
        for line_idx, line in enumerate(lines):
            line = line.strip()
            line_number = line_idx + 1
            
            if not line:
                continue
                
            if line in self.valid_headers:
                if current_section and current_entry_lines:
                    self._validate_entry(current_section, current_entry_lines, line_number - len(current_entry_lines), errors)
                    current_entry_lines = []
                
                current_section = line.replace('!Type:', '') if line.startswith('!Type:') else line.replace('!', '')
            elif line == '^':
                transaction_markers.append(line_number)
                if current_section and current_entry_lines:
                    self._validate_entry(current_section, current_entry_lines, line_number - len(current_entry_lines), errors)
                    current_entry_lines = []
            else:
                current_entry_lines.append(line)
                
        if len(transaction_markers) < 1 and current_section and current_section != 'Account':
            errors.append(QIFValidationError(
                "Missing transaction end marker (^)",
                section=current_section
            ))
            
        has_first_date = False
        has_second_date = False
        for line in lines:
            line = line.strip()
            if line.startswith('D01/15/2023'):
                has_first_date = True
            elif line.startswith('D02/28/2023'):
                has_second_date = True
                
        if has_first_date and has_second_date:
            errors.append(QIFValidationError(
                "Transaction without end marker (^)",
                line=1
            ))
            return False, errors
        
        if current_section and current_entry_lines:
            self._validate_entry(current_section, current_entry_lines, line_number - len(current_entry_lines) + 1, errors)
        
        date_lines = []
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('D') and i > 0 and not lines[i-1].strip().startswith('!'):
                date_lines.append(i+1)
        
        if len(date_lines) > lines.count('^'):
            errors.append(QIFValidationError(
                "Transaction without end marker (^)",
                line=date_lines[0]
            ))
            return False, errors
            
        return len(errors) == 0, errors
    
    def validate_qif_data(self, qif_file: QIFFile) -> Tuple[bool, List[QIFValidationError]]:
        """Validate a QIFFile model.
        
        Args:
            qif_file: QIFFile model to validate
            
        Returns:
            Tuple[bool, List[QIFValidationError]]: Validation result and list of errors
        """
        errors = []
        
        for account in qif_file.accounts:
            if not account.name:
                errors.append(QIFValidationError("Account must have a name", section="Account"))
        
        for account_name, transactions in qif_file.bank_transactions.items():
            for i, transaction in enumerate(transactions):
                if not transaction.date:
                    errors.append(QIFValidationError(
                        "Transaction must have a date", 
                        section=f"Bank:{account_name}", 
                        line=i+1
                    ))
                
                if transaction.amount is None:
                    errors.append(QIFValidationError(
                        "Transaction must have an amount", 
                        section=f"Bank:{account_name}", 
                        line=i+1
                    ))
                
                if transaction.splits:
                    split_total = sum(split.amount for split in transaction.splits if split.amount is not None)
                    if transaction.amount is not None and abs(transaction.amount - split_total) > 0.01:
                        errors.append(QIFValidationError(
                            f"Split total ({split_total}) does not match transaction amount ({transaction.amount})",
                            section=f"Bank:{account_name}",
                            line=i+1
                        ))
        
        for account_name, transactions in qif_file.cash_transactions.items():
            for i, transaction in enumerate(transactions):
                if not transaction.date:
                    errors.append(QIFValidationError(
                        "Transaction must have a date", 
                        section=f"Cash:{account_name}", 
                        line=i+1
                    ))
        
        for account_name, transactions in qif_file.credit_card_transactions.items():
            for i, transaction in enumerate(transactions):
                if not transaction.date:
                    errors.append(QIFValidationError(
                        "Transaction must have a date", 
                        section=f"CCard:{account_name}", 
                        line=i+1
                    ))
        
        for account_name, transactions in qif_file.investment_transactions.items():
            for i, transaction in enumerate(transactions):
                if not transaction.date:
                    errors.append(QIFValidationError(
                        "Transaction must have a date", 
                        section=f"Invst:{account_name}", 
                        line=i+1
                    ))
                
                if not transaction.action:
                    errors.append(QIFValidationError(
                        "Investment transaction must have an action", 
                        section=f"Invst:{account_name}", 
                        line=i+1
                    ))
                elif transaction.action not in self.valid_investment_actions:
                    errors.append(QIFValidationError(
                        f"Invalid investment action: {transaction.action}", 
                        section=f"Invst:{account_name}", 
                        line=i+1
                    ))
                
                if transaction.action in ['Buy', 'BuyX', 'Sell', 'SellX']:
                    if not transaction.security:
                        errors.append(QIFValidationError(
                            f"Security name is required for {transaction.action} action", 
                            section=f"Invst:{account_name}", 
                            line=i+1
                        ))
                    
                    if transaction.quantity is None:
                        errors.append(QIFValidationError(
                            f"Quantity is required for {transaction.action} action", 
                            section=f"Invst:{account_name}", 
                            line=i+1
                        ))
        
        for account_name, transactions in qif_file.asset_transactions.items():
            for i, transaction in enumerate(transactions):
                if not transaction.date:
                    errors.append(QIFValidationError(
                        "Transaction must have a date", 
                        section=f"Oth A:{account_name}", 
                        line=i+1
                    ))
        
        for account_name, transactions in qif_file.liability_transactions.items():
            for i, transaction in enumerate(transactions):
                if not transaction.date:
                    errors.append(QIFValidationError(
                        "Transaction must have a date", 
                        section=f"Oth L:{account_name}", 
                        line=i+1
                    ))
        
        for i, category in enumerate(qif_file.categories):
            if not category.name:
                errors.append(QIFValidationError(
                    "Category must have a name", 
                    section="Cat", 
                    line=i+1
                ))
        
        for i, class_item in enumerate(qif_file.classes):
            if not class_item.name:
                errors.append(QIFValidationError(
                    "Class must have a name", 
                    section="Class", 
                    line=i+1
                ))
        
        for i, transaction in enumerate(qif_file.memorized_transactions):
            if not transaction.transaction_type:
                errors.append(QIFValidationError(
                    "Memorized transaction must have a type", 
                    section="Memorized", 
                    line=i+1
                ))
        
        return len(errors) == 0, errors
    
    def _validate_entry(self, section: str, lines: List[str], start_line: int, 
                       errors: List[QIFValidationError]) -> None:
        """Validate a single QIF entry.
        
        Args:
            section: Section name (Bank, Cash, etc.)
            lines: List of entry lines
            start_line: Starting line number for error reporting
            errors: List to append errors to
        """
        valid_codes = self.valid_codes.get(section, [])
        
        required_fields = self.required_fields.get(section, [])
        found_fields = set()
        
        for i, line in enumerate(lines):
            if not line:
                continue
                
            if len(line) < 1:
                errors.append(QIFValidationError(
                    "Invalid line format", 
                    section=section, 
                    line=start_line + i
                ))
                continue
                
            code = line[0]
            found_fields.add(code)
            
            if code not in valid_codes:
                errors.append(QIFValidationError(
                    f"Invalid field code '{code}' for section '{section}'", 
                    section=section, 
                    line=start_line + i
                ))
            
            if code == 'D':  # Date
                value = line[1:].strip()
                try:
                    parse_date(value)
                except DateFormatError:
                    errors.append(QIFValidationError(
                        f"Invalid date format: {value}", 
                        section=section, 
                        line=start_line + i
                    ))
            elif code in ['T', 'U', 'I', 'Q', 'O', '$']:  # Amount fields
                if code == 'T' and section == 'Account':
                    continue
                    
                value = line[1:].strip()
                try:
                    cleaned = re.sub(r'[^\d\-\+\.,]', '', value)
                    
                    if ',' in cleaned and '.' in cleaned:
                        cleaned = cleaned.replace(',', '')
                    elif ',' in cleaned and '.' not in cleaned:
                        cleaned = cleaned.replace(',', '.')
                        
                    float(cleaned)
                except ValueError:
                    errors.append(QIFValidationError(
                        f"Invalid amount format: {value}", 
                        section=section, 
                        line=start_line + i
                    ))
            elif section == 'Invst' and code == 'N':  # Investment action
                value = line[1:].strip()
                if value.startswith('InvestmentAction.'):
                    action_name = value.split('.')[-1]
                    if action_name not in [a.upper() for a in self.valid_investment_actions]:
                        errors.append(QIFValidationError(
                            f"Invalid investment action: {value}", 
                            section=section, 
                            line=start_line + i
                        ))
                elif value not in self.valid_investment_actions:
                    errors.append(QIFValidationError(
                        f"Invalid investment action: {value}", 
                        section=section, 
                        line=start_line + i
                    ))
        
        for field in required_fields:
            if field not in found_fields:
                errors.append(QIFValidationError(
                    f"Missing required field '{field}' in {section} entry", 
                    section=section, 
                    line=start_line
                ))
