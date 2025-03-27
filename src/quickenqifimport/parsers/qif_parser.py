from typing import Dict, List, Tuple, Optional, Union, Any
from datetime import datetime
import re
from ..models.models import (
    QIFFile, AccountDefinition, BankingTransaction, InvestmentTransaction,
    CategoryItem, ClassItem, MemorizedTransaction, SplitTransaction,
    AccountType, ClearedStatus, InvestmentAction, MemorizedTransactionType
)
from ..utils.date_utils import parse_date

class QIFParserError(Exception):
    """Exception raised for errors during QIF parsing."""
    pass

class QIFParser:
    """Parser for QIF files."""
    
    def __init__(self):
        self._header_parsers = {
            '!Type:Bank': self._parse_banking_transactions,
            '!Type:Cash': self._parse_banking_transactions,
            '!Type:CCard': self._parse_banking_transactions,
            '!Type:Invst': self._parse_investment_transactions,
            '!Type:Oth A': self._parse_banking_transactions,
            '!Type:Oth L': self._parse_banking_transactions,
            '!Account': self._parse_accounts,
            '!Type:Cat': self._parse_categories,
            '!Type:Class': self._parse_classes,
            '!Type:Memorized': self._parse_memorized_transactions,
        }
        
        self._account_type_mapping = {
            AccountType.BANK: 'bank_transactions',
            AccountType.CASH: 'cash_transactions',
            AccountType.CREDIT_CARD: 'credit_card_transactions',
            AccountType.INVESTMENT: 'investment_transactions',
            AccountType.ASSET: 'asset_transactions',
            AccountType.LIABILITY: 'liability_transactions',
        }
        
    def parse(self, qif_content: str) -> QIFFile:
        """Parse QIF content into a QIFFile model.
        
        Args:
            qif_content: String containing QIF data
            
        Returns:
            QIFFile: A QIFFile model containing the parsed data
            
        Raises:
            QIFParserError: If the QIF content cannot be parsed
        """
        try:
            qif_file = QIFFile()
            
            if not qif_content.strip():
                raise QIFParserError("QIF content is empty")
                
            if '^' not in qif_content:
                raise QIFParserError("Invalid QIF format: missing transaction delimiters (^)")
                
            blocks = self._split_into_blocks(qif_content)
            
            if not blocks:
                raise QIFParserError("No valid QIF blocks found")
                
            current_account = "Default"  # Default account name if none specified
            current_account_type = None
            
            for header, content in blocks:
                if header == '!Account':
                    accounts = self._parse_accounts(content)
                    qif_file.accounts.extend(accounts)
                    if accounts:
                        current_account = accounts[0].name
                        current_account_type = accounts[0].type
                elif header in self._header_parsers:
                    parser = self._header_parsers[header]
                    
                    parsed_items = parser(content)
                    
                    if not parsed_items:
                        continue
                        
                    if header.startswith('!Type:'):
                        type_code = header[6:]  # Extract type code after !Type:
                        if type_code in ['Bank', 'Cash', 'CCard', 'Oth A', 'Oth L']:
                            account_type = self._get_account_type_from_code(type_code)
                            
                            current_account_type = account_type
                            
                            attr_name = self._account_type_mapping[current_account_type]
                            transaction_dict = getattr(qif_file, attr_name)
                            if current_account not in transaction_dict:
                                transaction_dict[current_account] = []
                            transaction_dict[current_account].extend(parsed_items)
                        elif type_code == 'Invst':
                            if current_account not in qif_file.investment_transactions:
                                qif_file.investment_transactions[current_account] = []
                            qif_file.investment_transactions[current_account].extend(parsed_items)
                        elif type_code == 'Cat':
                            qif_file.categories.extend(parsed_items)
                        elif type_code == 'Class':
                            qif_file.classes.extend(parsed_items)
                        elif type_code == 'Memorized':
                            qif_file.memorized_transactions.extend(parsed_items)
            
            return qif_file
            
        except Exception as e:
            if isinstance(e, QIFParserError):
                raise
            raise QIFParserError(f"Failed to parse QIF content: {str(e)}")
        
    def _split_into_blocks(self, qif_content: str) -> List[Tuple[str, str]]:
        """Split QIF content into blocks based on headers.
        
        Args:
            qif_content: String containing QIF data
            
        Returns:
            List of tuples (header, content)
        """
        lines = qif_content.strip().split('\n')
        blocks = []
        
        current_header = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('!'):
                if current_header is not None:
                    blocks.append((current_header, '\n'.join(current_content)))
                    current_content = []
                current_header = line
            else:
                current_content.append(line)
                
        if current_header is not None and current_content:
            blocks.append((current_header, '\n'.join(current_content)))
            
        return blocks
        
    def _get_account_type_from_code(self, type_code: str) -> AccountType:
        """Convert QIF type code to AccountType enum.
        
        Args:
            type_code: QIF type code string
            
        Returns:
            AccountType enum value
        """
        mapping = {
            'Bank': AccountType.BANK,
            'Cash': AccountType.CASH,
            'CCard': AccountType.CREDIT_CARD,
            'Invst': AccountType.INVESTMENT,
            'Oth A': AccountType.ASSET,
            'Oth L': AccountType.LIABILITY,
        }
        return mapping.get(type_code, AccountType.BANK)
        
    def _parse_banking_transactions(self, content: str) -> List[BankingTransaction]:
        """Parse banking transactions from QIF content.
        
        Args:
            content: String containing transaction data
            
        Returns:
            List of BankingTransaction objects
        """
        transactions = []
        entries = content.split('^')
        
        for entry in entries:
            if not entry.strip():
                continue
                
            lines = entry.strip().split('\n')
            transaction_data = {}
            splits = []
            current_split = {}
            
            for line in lines:
                if not line:
                    continue
                    
                code = line[0]
                value = line[1:].strip()
                
                if code == 'D':  # Date
                    transaction_data['date'] = value
                elif code == 'T':  # Amount
                    transaction_data['amount'] = self._parse_amount(value)
                elif code == 'U':  # Amount (alternate)
                    if 'amount' not in transaction_data:
                        transaction_data['amount'] = self._parse_amount(value)
                elif code == 'C':  # Cleared status
                    transaction_data['cleared_status'] = value
                elif code == 'N':  # Check number/reference
                    transaction_data['number'] = value
                elif code == 'P':  # Payee
                    transaction_data['payee'] = value
                elif code == 'M':  # Memo
                    transaction_data['memo'] = value
                elif code == 'A':  # Address
                    if 'address' not in transaction_data:
                        transaction_data['address'] = []
                    transaction_data['address'].append(value)
                elif code == 'L':  # Category
                    transaction_data['category'] = value
                elif code == 'S':  # Split category
                    if current_split:
                        splits.append(current_split)
                        current_split = {}
                    current_split['category'] = value
                elif code == 'E':  # Split memo
                    if current_split:
                        current_split['memo'] = value
                elif code == '$':  # Split amount
                    if current_split:
                        current_split['amount'] = self._parse_amount(value)
                elif code == '%':  # Split percentage
                    if current_split:
                        current_split['percentage'] = float(value)
            
            if current_split:
                splits.append(current_split)
                
            if splits:
                transaction_data['splits'] = [SplitTransaction(**split) for split in splits]
                
            transactions.append(BankingTransaction(**transaction_data))
            
        return transactions
        
    def _parse_investment_transactions(self, content: str) -> List[InvestmentTransaction]:
        """Parse investment transactions from QIF content.
        
        Args:
            content: String containing transaction data
            
        Returns:
            List of InvestmentTransaction objects
        """
        transactions = []
        entries = content.split('^')
        
        for entry in entries:
            if not entry.strip():
                continue
                
            lines = entry.strip().split('\n')
            transaction_data = {}
            
            for line in lines:
                if not line:
                    continue
                    
                code = line[0]
                value = line[1:].strip()
                
                if code == 'D':  # Date
                    transaction_data['date'] = value
                elif code == 'N':  # Action
                    if value.startswith('InvestmentAction.'):
                        action_name = value.split('.')[-1]
                        for member_name, member_value in InvestmentAction.__members__.items():
                            if member_name.upper() == action_name.upper():
                                transaction_data['action'] = member_value.value
                                break
                        else:
                            for member_value in InvestmentAction:
                                if member_value.value.upper() == action_name.upper():
                                    transaction_data['action'] = member_value.value
                                    break
                            else:
                                transaction_data['action'] = value
                    else:
                        for member_name, member_value in InvestmentAction.__members__.items():
                            if member_name.upper() == value.upper():
                                transaction_data['action'] = member_value.value
                                break
                        else:
                            for member_value in InvestmentAction:
                                if member_value.value.upper() == value.upper():
                                    transaction_data['action'] = member_value.value
                                    break
                            else:
                                transaction_data['action'] = value
                elif code == 'Y':  # Security
                    transaction_data['security'] = value
                elif code == 'I':  # Price
                    transaction_data['price'] = self._parse_amount(value)
                elif code == 'Q':  # Quantity
                    transaction_data['quantity'] = self._parse_amount(value)
                elif code == 'T':  # Transaction amount
                    transaction_data['amount'] = self._parse_amount(value)
                elif code == 'C':  # Cleared status
                    transaction_data['cleared_status'] = value
                elif code == 'P':  # Text for transfers
                    transaction_data['payee'] = value
                elif code == 'M':  # Memo
                    transaction_data['memo'] = value
                elif code == 'O':  # Commission
                    transaction_data['commission'] = self._parse_amount(value)
                elif code == 'L':  # Category or Account for transfers
                    if ':' in value:  # If it contains a colon, it's likely a category
                        transaction_data['category'] = value
                    else:  # Otherwise treat as account
                        transaction_data['account'] = value
                elif code == '$':  # Transfer amount
                    transaction_data['transfer_amount'] = self._parse_amount(value)
            
            transactions.append(InvestmentTransaction(**transaction_data))
            
        return transactions
        
    def _parse_accounts(self, content: str) -> List[AccountDefinition]:
        """Parse account definitions from QIF content.
        
        Args:
            content: String containing account data
            
        Returns:
            List of AccountDefinition objects
        """
        accounts = []
        entries = content.split('^')
        
        for entry in entries:
            if not entry.strip():
                continue
                
            lines = entry.strip().split('\n')
            account_data = {}
            
            for line in lines:
                if not line:
                    continue
                    
                code = line[0]
                value = line[1:].strip()
                
                if code == 'N':  # Name
                    account_data['name'] = value
                elif code == 'T':  # Type
                    account_data['type'] = self._parse_account_type(value)
                elif code == 'D':  # Description
                    account_data['description'] = value
                elif code == 'L':  # Credit limit
                    account_data['credit_limit'] = self._parse_amount(value)
                elif code == '/':  # Statement date
                    account_data['statement_balance_date'] = value
                elif code == '$':  # Statement balance
                    account_data['statement_balance'] = self._parse_amount(value)
            
            accounts.append(AccountDefinition(**account_data))
            
        return accounts
        
    def _parse_categories(self, content: str) -> List[CategoryItem]:
        """Parse category list from QIF content.
        
        Args:
            content: String containing category data
            
        Returns:
            List of CategoryItem objects
        """
        categories = []
        entries = content.split('^')
        
        for entry in entries:
            if not entry.strip():
                continue
                
            lines = entry.strip().split('\n')
            category_data = {
                'tax_related': False,
                'income': False,
                'expense': True
            }
            
            for line in lines:
                if not line:
                    continue
                    
                code = line[0]
                value = line[1:].strip()
                
                if code == 'N':  # Name
                    category_data['name'] = value
                elif code == 'D':  # Description
                    category_data['description'] = value
                elif code == 'T':  # Tax related
                    category_data['tax_related'] = True
                elif code == 'I':  # Income
                    category_data['income'] = True
                    category_data['expense'] = False
                elif code == 'E':  # Expense
                    category_data['expense'] = True
                    category_data['income'] = False
                elif code == 'B':  # Budget
                    category_data['budget_amount'] = self._parse_amount(value)
                elif code == 'R':  # Tax schedule
                    category_data['tax_schedule'] = value
            
            categories.append(CategoryItem(**category_data))
            
        return categories
        
    def _parse_classes(self, content: str) -> List[ClassItem]:
        """Parse class list from QIF content.
        
        Args:
            content: String containing class data
            
        Returns:
            List of ClassItem objects
        """
        classes = []
        entries = content.split('^')
        
        for entry in entries:
            if not entry.strip():
                continue
                
            lines = entry.strip().split('\n')
            class_data = {}
            
            for line in lines:
                if not line:
                    continue
                    
                code = line[0]
                value = line[1:].strip()
                
                if code == 'N':  # Name
                    class_data['name'] = value
                elif code == 'D':  # Description
                    class_data['description'] = value
            
            classes.append(ClassItem(**class_data))
            
        return classes
        
    def _parse_memorized_transactions(self, content: str) -> List[MemorizedTransaction]:
        """Parse memorized transactions from QIF content.
        
        Args:
            content: String containing memorized transaction data
            
        Returns:
            List of MemorizedTransaction objects
        """
        transactions = []
        entries = content.split('^')
        
        for entry in entries:
            if not entry.strip():
                continue
                
            lines = entry.strip().split('\n')
            transaction_data = {}
            splits = []
            current_split = {}
            
            for line in lines:
                if not line:
                    continue
                    
                code = line[0]
                value = line[1:].strip()
                
                if code == 'K':  # Transaction type
                    if len(value) > 0:
                        transaction_type = value[0]
                        if transaction_type == 'C':
                            transaction_data['transaction_type'] = MemorizedTransactionType.CHECK
                        elif transaction_type == 'D':
                            transaction_data['transaction_type'] = MemorizedTransactionType.DEPOSIT
                        elif transaction_type == 'P':
                            transaction_data['transaction_type'] = MemorizedTransactionType.PAYMENT
                        elif transaction_type == 'I':
                            transaction_data['transaction_type'] = MemorizedTransactionType.INVESTMENT
                        elif transaction_type == 'E':
                            transaction_data['transaction_type'] = MemorizedTransactionType.ELECTRONIC
                elif code == 'T':  # Amount
                    transaction_data['amount'] = self._parse_amount(value)
                elif code == 'C':  # Cleared status
                    transaction_data['cleared_status'] = value
                elif code == 'P':  # Payee
                    transaction_data['payee'] = value
                elif code == 'M':  # Memo
                    transaction_data['memo'] = value
                elif code == 'A':  # Address
                    if 'address' not in transaction_data:
                        transaction_data['address'] = []
                    transaction_data['address'].append(value)
                elif code == 'L':  # Category
                    transaction_data['category'] = value
                elif code == 'S':  # Split category
                    if current_split:
                        splits.append(current_split)
                        current_split = {}
                    current_split['category'] = value
                elif code == 'E':  # Split memo
                    if current_split:
                        current_split['memo'] = value
                elif code == '$':  # Split amount
                    if current_split:
                        current_split['amount'] = self._parse_amount(value)
                elif code == '%':  # Split percentage
                    if current_split:
                        current_split['percentage'] = float(value)
            
            if current_split:
                splits.append(current_split)
                
            if splits:
                transaction_data['splits'] = [SplitTransaction(**split) for split in splits]
                
            transactions.append(MemorizedTransaction(**transaction_data))
            
        return transactions
        
    def _parse_account_type(self, type_str: str) -> AccountType:
        """Parse account type string to AccountType enum.
        
        Args:
            type_str: Account type string from QIF
            
        Returns:
            AccountType enum value
        """
        type_map = {
            'Bank': AccountType.BANK,
            'Cash': AccountType.CASH,
            'CCard': AccountType.CREDIT_CARD,
            'Invst': AccountType.INVESTMENT,
            'Oth A': AccountType.ASSET,
            'Oth L': AccountType.LIABILITY,
            'Invoice': AccountType.INVOICE,
        }
        
        return type_map.get(type_str, AccountType.BANK)
        
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float.
        
        Args:
            amount_str: Amount string from QIF
            
        Returns:
            float: Parsed amount
            
        Raises:
            QIFParserError: If the amount cannot be parsed
        """
        if not amount_str:
            return 0.0
            
        if not any(c.isdigit() for c in amount_str):
            raise QIFParserError(f"Invalid amount format: {amount_str}")
            
        cleaned = re.sub(r'[^\d\-\+\.,]', '', amount_str)
        
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned and '.' not in cleaned:
            cleaned = cleaned.replace(',', '.')
            
        try:
            return float(cleaned)
        except ValueError:
            raise QIFParserError(f"Invalid amount format: {amount_str}")
