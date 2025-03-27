from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from ..models.models import (
    QIFFile, AccountDefinition, BankingTransaction, InvestmentTransaction,
    CategoryItem, ClassItem, MemorizedTransaction, SplitTransaction,
    AccountType, ClearedStatus, InvestmentAction, MemorizedTransactionType
)
from ..utils.date_utils import format_date

class QIFGeneratorError(Exception):
    """Exception raised for errors during QIF generation."""
    pass

class QIFGenerator:
    """Generator for QIF files from model data."""
    
    def __init__(self, date_format: str = '%m/%d/%Y'):
        """Initialize the QIF generator.
        
        Args:
            date_format: Format string for dates in the QIF output
        """
        self.date_format = date_format
        
        self._account_type_headers = {
            AccountType.BANK: '!Type:Bank',
            AccountType.CASH: '!Type:Cash',
            AccountType.CREDIT_CARD: '!Type:CCard',
            AccountType.INVESTMENT: '!Type:Invst',
            AccountType.ASSET: '!Type:Oth A',
            AccountType.LIABILITY: '!Type:Oth L',
        }
        
    def _get_enum_value(self, enum_or_str):
        """Get the value from an enum or string.
        
        Args:
            enum_or_str: Enum instance or string
            
        Returns:
            str: The value to use in QIF output
        """
        if isinstance(enum_or_str, str):
            return enum_or_str
        elif hasattr(enum_or_str, 'value'):
            if str(enum_or_str).startswith('InvestmentAction.'):
                action_map = {
                    'InvestmentAction.BUY': 'Buy',
                    'InvestmentAction.SELL': 'Sell',
                    'InvestmentAction.DIV': 'Div',
                    'InvestmentAction.BUY_X': 'BuyX',
                    'InvestmentAction.SELL_X': 'SellX',
                    'InvestmentAction.DIV_X': 'DivX',
                    'InvestmentAction.REINVDIV': 'ReinvDiv',
                    'InvestmentAction.INTINC': 'IntInc',
                    'InvestmentAction.CGLONG': 'CGLong',
                    'InvestmentAction.CGSHORT': 'CGShort',
                    'InvestmentAction.SHRSIN': 'ShrsIn',
                    'InvestmentAction.SHRSOUT': 'ShrsOut',
                    'InvestmentAction.STKSPLIT': 'StkSplit',
                    'InvestmentAction.XIN': 'XIn',
                    'InvestmentAction.XOUT': 'XOut',
                }
                return action_map.get(str(enum_or_str), str(enum_or_str).split('.')[-1])
            elif str(enum_or_str).startswith('ClearedStatus.'):
                status_map = {
                    'ClearedStatus.CLEARED': '*',
                    'ClearedStatus.CLEARED_ALT': 'c',
                    'ClearedStatus.RECONCILED': 'X',
                    'ClearedStatus.RECONCILED_ALT': 'R',
                    'ClearedStatus.UNCLEARED': '',
                }
                return status_map.get(str(enum_or_str), enum_or_str.value)
            return enum_or_str.value
        else:
            return str(enum_or_str)
    
    def generate_qif_file(self, qif_file: QIFFile) -> str:
        """Generate QIF content from a QIFFile model.
        
        Args:
            qif_file: QIFFile model containing the data to generate
            
        Returns:
            str: Generated QIF content
            
        Raises:
            QIFGeneratorError: If the QIF content cannot be generated
        """
        try:
            qif_content = []
            
            if qif_file.accounts:
                qif_content.append('!Account')
                for account in qif_file.accounts:
                    qif_content.append(self._generate_account(account))
                
            for account_name, transactions in qif_file.bank_transactions.items():
                if transactions:
                    qif_content.append(self._generate_account_header(AccountType.BANK))
                    for transaction in transactions:
                        qif_content.append(self._generate_transaction(transaction))
            
            for account_name, transactions in qif_file.cash_transactions.items():
                if transactions:
                    qif_content.append(self._generate_account_header(AccountType.CASH))
                    for transaction in transactions:
                        qif_content.append(self._generate_transaction(transaction))
            
            for account_name, transactions in qif_file.credit_card_transactions.items():
                if transactions:
                    qif_content.append(self._generate_account_header(AccountType.CREDIT_CARD))
                    for transaction in transactions:
                        qif_content.append(self._generate_transaction(transaction))
            
            for account_name, transactions in qif_file.investment_transactions.items():
                if transactions:
                    qif_content.append(self._generate_account_header(AccountType.INVESTMENT))
                    for transaction in transactions:
                        qif_content.append(self._generate_investment_transaction(transaction))
            
            for account_name, transactions in qif_file.asset_transactions.items():
                if transactions:
                    qif_content.append(self._generate_account_header(AccountType.ASSET))
                    for transaction in transactions:
                        qif_content.append(self._generate_transaction(transaction))
            
            for account_name, transactions in qif_file.liability_transactions.items():
                if transactions:
                    qif_content.append(self._generate_account_header(AccountType.LIABILITY))
                    for transaction in transactions:
                        qif_content.append(self._generate_transaction(transaction))
            
            if qif_file.categories:
                qif_content.append('!Type:Cat')
                for category in qif_file.categories:
                    qif_content.append(self._generate_category(category))
            
            if qif_file.classes:
                qif_content.append('!Type:Class')
                for class_item in qif_file.classes:
                    qif_content.append(self._generate_class(class_item))
            
            if qif_file.memorized_transactions:
                qif_content.append('!Type:Memorized')
                for transaction in qif_file.memorized_transactions:
                    qif_content.append(self._generate_memorized_transaction(transaction))
            
            return '\n'.join(qif_content)
            
        except Exception as e:
            raise QIFGeneratorError(f"Failed to generate QIF content: {str(e)}")
    
    def _generate_account_header(self, account_type: AccountType) -> str:
        """Generate a QIF account type header.
        
        Args:
            account_type: AccountType enum value
            
        Returns:
            str: QIF account type header
        """
        return self._account_type_headers.get(account_type, '!Type:Bank')
    
    def _generate_transaction(self, transaction: BankingTransaction) -> str:
        """Generate QIF content for a banking transaction.
        
        Args:
            transaction: BankingTransaction model
            
        Returns:
            str: QIF transaction content
        """
        lines = []
        
        if transaction.date:
            lines.append(f"D{format_date(transaction.date, self.date_format)}")
        
        if transaction.amount is not None:
            lines.append(f"T{transaction.amount:.2f}")
        
        if transaction.cleared_status:
            lines.append(f"C{self._get_enum_value(transaction.cleared_status)}")
        
        if transaction.number:
            lines.append(f"N{transaction.number}")
        
        if transaction.payee:
            lines.append(f"P{transaction.payee}")
        
        if transaction.memo:
            lines.append(f"M{transaction.memo}")
        
        if transaction.address:
            for line in transaction.address:
                lines.append(f"A{line}")
        
        if transaction.category:
            lines.append(f"L{transaction.category}")
        
        if transaction.splits:
            for split in transaction.splits:
                lines.extend(self._generate_split(split))
        
        lines.append("^")
        
        return '\n'.join(lines)
    
    def _generate_investment_transaction(self, transaction: InvestmentTransaction) -> str:
        """Generate QIF content for an investment transaction.
        
        Args:
            transaction: InvestmentTransaction model
            
        Returns:
            str: QIF transaction content
        """
        lines = []
        
        if transaction.date:
            lines.append(f"D{format_date(transaction.date, self.date_format)}")
        
        if transaction.action:
            if isinstance(transaction.action, str):
                if transaction.action.startswith('InvestmentAction.'):
                    action_name = transaction.action.split('.')[-1]
                    for member_name in InvestmentAction.__members__:
                        if member_name.upper() == action_name:
                            lines.append(f"N{InvestmentAction[member_name].value}")
                            break
                    else:
                        lines.append(f"N{action_name}")
                else:
                    if transaction.action.upper() in [a.upper() for a in InvestmentAction.__members__]:
                        for member_name in InvestmentAction.__members__:
                            if member_name.upper() == transaction.action.upper():
                                lines.append(f"N{InvestmentAction[member_name].value}")
                                break
                    else:
                        lines.append(f"N{transaction.action}")
            else:
                lines.append(f"N{transaction.action.value}")
        
        if transaction.security:
            lines.append(f"Y{transaction.security}")
        
        if transaction.price is not None:
            lines.append(f"I{transaction.price}")
        
        if transaction.quantity is not None:
            quantity_str = str(int(transaction.quantity)) if transaction.quantity == int(transaction.quantity) else str(transaction.quantity)
            lines.append(f"Q{quantity_str}")
        
        if transaction.amount is not None:
            lines.append(f"T{transaction.amount:.2f}")
        
        if transaction.cleared_status:
            lines.append(f"C{self._get_enum_value(transaction.cleared_status)}")
        
        if transaction.payee:
            lines.append(f"P{transaction.payee}")
        
        if transaction.memo:
            lines.append(f"M{transaction.memo}")
        
        if transaction.commission is not None:
            lines.append(f"O{transaction.commission:.2f}")
        
        if transaction.account:
            lines.append(f"L{transaction.account}")
        elif transaction.category:
            lines.append(f"L{transaction.category}")
        
        if transaction.transfer_amount is not None:
            lines.append(f"${transaction.transfer_amount:.2f}")
        
        lines.append("^")
        
        return '\n'.join(lines)
    
    def _generate_split(self, split: SplitTransaction) -> List[str]:
        """Generate QIF content for a split transaction.
        
        Args:
            split: SplitTransaction model
            
        Returns:
            List[str]: QIF split content lines
        """
        lines = []
        
        if split.category:
            lines.append(f"S{split.category}")
        
        if split.memo:
            lines.append(f"E{split.memo}")
        
        if split.amount is not None:
            lines.append(f"${split.amount:.2f}")
        
        if split.percentage is not None:
            lines.append(f"%{split.percentage}")
        
        return lines
    
    def _generate_account(self, account: AccountDefinition) -> str:
        """Generate QIF content for an account definition.
        
        Args:
            account: AccountDefinition model
            
        Returns:
            str: QIF account content
        """
        lines = []
        
        if account.name:
            lines.append(f"N{account.name}")
        
        if account.type:
            type_str = self._get_account_type_str(account.type)
            lines.append(f"T{type_str}")
        
        if account.description:
            lines.append(f"D{account.description}")
        
        if account.credit_limit is not None:
            lines.append(f"L{account.credit_limit:.2f}")
        
        if account.statement_balance_date:
            lines.append(f"/{format_date(account.statement_balance_date, self.date_format)}")
        
        if account.statement_balance is not None:
            lines.append(f"${account.statement_balance:.2f}")
        
        lines.append("^")
        
        return '\n'.join(lines)
    
    def _generate_category(self, category: CategoryItem) -> str:
        """Generate QIF content for a category.
        
        Args:
            category: CategoryItem model
            
        Returns:
            str: QIF category content
        """
        lines = []
        
        if category.name:
            lines.append(f"N{category.name}")
        
        if category.description:
            lines.append(f"D{category.description}")
        
        if category.tax_related:
            lines.append("T")
        
        if category.income:
            lines.append("I")
        elif category.expense:
            lines.append("E")
        
        if category.budget_amount is not None:
            lines.append(f"B{category.budget_amount:.2f}")
        
        if category.tax_schedule:
            lines.append(f"R{category.tax_schedule}")
        
        lines.append("^")
        
        return '\n'.join(lines)
    
    def _generate_class(self, class_item: ClassItem) -> str:
        """Generate QIF content for a class.
        
        Args:
            class_item: ClassItem model
            
        Returns:
            str: QIF class content
        """
        lines = []
        
        if class_item.name:
            lines.append(f"N{class_item.name}")
        
        if class_item.description:
            lines.append(f"D{class_item.description}")
        
        lines.append("^")
        
        return '\n'.join(lines)
    
    def _generate_memorized_transaction(self, transaction: MemorizedTransaction) -> str:
        """Generate QIF content for a memorized transaction.
        
        Args:
            transaction: MemorizedTransaction model
            
        Returns:
            str: QIF memorized transaction content
        """
        lines = []
        
        if transaction.transaction_type:
            type_code = self._get_memorized_transaction_type_code(transaction.transaction_type)
            lines.append(f"K{type_code}")
        
        if transaction.amount is not None:
            lines.append(f"T{transaction.amount:.2f}")
        
        if transaction.cleared_status:
            lines.append(f"C{self._get_enum_value(transaction.cleared_status)}")
        
        if transaction.payee:
            lines.append(f"P{transaction.payee}")
        
        if transaction.memo:
            lines.append(f"M{transaction.memo}")
        
        if transaction.address:
            for line in transaction.address:
                lines.append(f"A{line}")
        
        if transaction.category:
            lines.append(f"L{transaction.category}")
        
        if transaction.splits:
            for split in transaction.splits:
                lines.extend(self._generate_split(split))
        
        lines.append("^")
        
        return '\n'.join(lines)
    
    def _get_account_type_str(self, account_type: AccountType) -> str:
        """Convert AccountType enum to QIF account type string.
        
        Args:
            account_type: AccountType enum value
            
        Returns:
            str: QIF account type string
        """
        type_map = {
            AccountType.BANK: 'Bank',
            AccountType.CASH: 'Cash',
            AccountType.CREDIT_CARD: 'CCard',
            AccountType.INVESTMENT: 'Invst',
            AccountType.ASSET: 'Oth A',
            AccountType.LIABILITY: 'Oth L',
            AccountType.INVOICE: 'Invoice',
        }
        
        return type_map.get(account_type, 'Bank')
    
    def _get_memorized_transaction_type_code(self, transaction_type: MemorizedTransactionType) -> str:
        """Convert MemorizedTransactionType enum to QIF type code.
        
        Args:
            transaction_type: MemorizedTransactionType enum value
            
        Returns:
            str: QIF memorized transaction type code
        """
        type_map = {
            MemorizedTransactionType.CHECK: 'C',
            MemorizedTransactionType.DEPOSIT: 'D',
            MemorizedTransactionType.PAYMENT: 'P',
            MemorizedTransactionType.INVESTMENT: 'I',
            MemorizedTransactionType.ELECTRONIC: 'E',
        }
        
        return type_map.get(transaction_type, 'C')
        
    def generate_qif(self, transactions: List[Union[BankingTransaction, InvestmentTransaction]], 
                   account_type: AccountType, account_name: str, 
                   include_account_info: bool = False) -> str:
        """Generate QIF content from a list of transactions.
        
        Args:
            transactions: List of transactions to generate QIF content for
            account_type: Type of account for the transactions
            account_name: Name of the account
            include_account_info: Whether to include account information in the QIF content
            
        Returns:
            str: Generated QIF content
            
        Raises:
            QIFGeneratorError: If the QIF content cannot be generated
        """
        try:
            qif_content = []
            
            if not isinstance(account_type, AccountType):
                raise QIFGeneratorError(f"Invalid account type: {account_type}")
            
            if include_account_info:
                qif_content.append('!Account')
                account = AccountDefinition(name=account_name, type=account_type)
                qif_content.append(self._generate_account(account))
            
            qif_content.append(self._generate_account_header(account_type))
            
            for transaction in transactions:
                if account_type == AccountType.INVESTMENT:
                    if isinstance(transaction, InvestmentTransaction):
                        qif_content.append(self._generate_investment_transaction(transaction))
                    else:
                        raise QIFGeneratorError(
                            f"Expected InvestmentTransaction for account type {account_type}, "
                            f"got {type(transaction).__name__}"
                        )
                else:
                    if isinstance(transaction, BankingTransaction):
                        qif_content.append(self._generate_transaction(transaction))
                    else:
                        raise QIFGeneratorError(
                            f"Expected BankingTransaction for account type {account_type}, "
                            f"got {type(transaction).__name__}"
                        )
            
            return '\n'.join(qif_content)
            
        except Exception as e:
            if isinstance(e, QIFGeneratorError):
                raise
            raise QIFGeneratorError(f"Failed to generate QIF content: {str(e)}")
